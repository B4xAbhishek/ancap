"""ACP-hub exchange office foundation tests."""

from decimal import Decimal
from uuid import uuid4

from app.services.exchange_office import build_pairs, catalog, quote
from app.schemas.exchange_office import ExchangeQuoteRequest


def _register_user(client, label: str):
    email = f"{label}_{uuid4().hex[:12]}@test.com"
    password = "password123"
    res = client.post(
        "/v1/auth/users",
        json={"email": email, "password": password, "display_name": label},
        headers={"Authorization": ""},
    )
    assert res.status_code in (200, 201), res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user = client.get("/v1/users/me", headers=headers).json()
    return user, headers


def test_catalog_has_hub_and_core_assets():
    c = catalog()
    ids = {a.id for a in c.assets}
    assert c.hub_asset == "acp"
    assert c.model == "acp_hub"
    assert "acp" in ids
    assert "usdt_trc20" in ids
    assert "wacp_bsc" in ids
    assert "sacp_bsc" in ids
    assert "metal_gold" in ids
    assert "goods_electronics" in ids
    assert "commodity_oil" in ids
    assert "commodity_uranium" in ids
    assert "fiat_usd" in ids
    assert c.quote_ttl_seconds > 0
    assert len(c.pairs) > 10


def test_quote_commodity_into_acp():
    q = quote(
        ExchangeQuoteRequest(from_asset="commodity_oil", to_asset="acp", from_amount="5")
    )
    assert Decimal(q.to_amount) == Decimal("400")
    assert q.rail == "otc_commodity"



def test_pairs_include_cross_and_direct():
    pairs = build_pairs()
    direct = next(p for p in pairs if p.from_asset == "usdt_trc20" and p.to_asset == "acp")
    assert direct.legs == 1
    assert direct.rail == "swap_desk"
    cross = next(p for p in pairs if p.from_asset == "metal_gold" and p.to_asset == "usdt_trc20")
    assert cross.legs == 2
    assert cross.rail == "hub_cross"


def test_quote_usdt_into_acp(monkeypatch):
    monkeypatch.setenv("WACP_ORACLE_PIN_DESK", "true")
    monkeypatch.setenv("USDT_TRC20_TO_ACP_RATE", "1")
    from app.config import get_settings

    get_settings.cache_clear()
    q = quote(ExchangeQuoteRequest(from_asset="usdt_trc20", to_asset="acp", from_amount="100"))
    assert Decimal(q.to_amount) == Decimal("100")  # pinned desk rate 1
    assert q.rail == "swap_desk"
    assert len(q.legs) == 1
    assert q.quote_id
    get_settings.cache_clear()


def test_quote_wacp_bridge_ratio_1_to_10():
    """Bridge doctrine: 1 ACP ↔ 10 wACP (not 1:1)."""
    into = quote(ExchangeQuoteRequest(from_asset="wacp_bsc", to_asset="acp", from_amount="10"))
    assert Decimal(into.to_amount) == Decimal("1")
    assert into.rail == "bridge"
    assert "10 wACP = 1 ACP" in into.rate_note

    out = quote(ExchangeQuoteRequest(from_asset="acp", to_asset="wacp_bsc", from_amount="1"))
    assert Decimal(out.to_amount) == Decimal("10")
    assert out.rail == "bridge"
    assert "1 ACP = 10 wACP" in out.rate_note

    # Floor on redeem dust
    dust = quote(ExchangeQuoteRequest(from_asset="wacp_bsc", to_asset="acp", from_amount="9"))
    assert Decimal(dust.to_amount) == Decimal("0.9")


def test_quote_metal_into_acp_with_purity():
    q = quote(
        ExchangeQuoteRequest(
            from_asset="metal_gold",
            to_asset="acp",
            from_amount="10",
            purity_ppt=999,
        )
    )
    assert Decimal(q.to_amount) == Decimal("2497.5")
    assert q.rail == "otc_metal"


def test_quote_cross_metal_to_usdt():
    q = quote(
        ExchangeQuoteRequest(
            from_asset="metal_gold",
            to_asset="usdt_trc20",
            from_amount="1",
            purity_ppt=1000,
        )
    )
    assert q.rail == "hub_cross"
    assert len(q.legs) == 2
    assert Decimal(q.acp_hub_amount) == Decimal("250")
    assert Decimal(q.to_amount) > 0


def test_exchange_ticket_auth_settle_opens_swap_order(client):
    _user, headers = _register_user(client, "xo_settle")
    q = client.post(
        "/v1/mobile/exchange/quote",
        json={"from_asset": "usdt_trc20", "to_asset": "acp", "from_amount": "25"},
    )
    assert q.status_code == 200, q.text
    quote_id = q.json()["quote_id"]
    payout = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"

    ticket = client.post(
        "/v1/mobile/exchange/tickets",
        headers={**headers, "Idempotency-Key": f"xo-{quote_id}"},
        json={"quote_id": quote_id, "payout_acp_address": payout},
    )
    assert ticket.status_code == 201, ticket.text
    body = ticket.json()
    assert body["status"] == "awaiting_user"
    assert body["rail"] == "swap_desk"

    settle = client.post(
        f"/v1/mobile/exchange/tickets/{body['id']}/auth-settle",
        headers=headers,
        json={},
    )
    assert settle.status_code == 200, settle.text
    settled = settle.json()
    assert settled["status"] == "settling"
    assert settled["rail_ref_type"] == "swap_order"
    assert settled["rail_ref_id"]

    sync = client.post(
        f"/v1/mobile/exchange/tickets/{body['id']}/sync",
        headers=headers,
    )
    assert sync.status_code == 200, sync.text
    assert sync.json()["status"] == "settling"

    settle2 = client.post(
        f"/v1/mobile/exchange/tickets/{body['id']}/auth-settle",
        headers=headers,
        json={},
    )
    assert settle2.status_code == 200, settle2.text
    assert settle2.json()["rail_ref_id"] == settled["rail_ref_id"]
