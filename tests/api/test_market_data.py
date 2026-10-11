"""CoinGecko market-data client tests (mocked HTTP)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services import coingecko, market_economy


class _Resp:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_fetch_simple_prices_ok(monkeypatch):
    coingecko.clear_cache()
    market_economy.clear_oracle_cache()
    monkeypatch.setenv("COINGECKO_API_KEY", "CG-test-key")
    from app.config import get_settings

    get_settings.cache_clear()

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, params=None, headers=None):
            assert "x-cg-demo-api-key" in (headers or {})
            return _Resp(
                200,
                {
                    "bitcoin": {"usd": 100000.0, "last_updated_at": 1},
                    "ethereum": {"usd": 3500.0, "last_updated_at": 1},
                    "tether": {"usd": 1.0, "last_updated_at": 1},
                    "binancecoin": {"usd": 600.0, "last_updated_at": 1},
                    "solana": {"usd": 150.0, "last_updated_at": 1},
                },
            )

    monkeypatch.setattr(coingecko.httpx, "AsyncClient", _Client)
    data = await coingecko.fetch_simple_prices()
    assert data["status"] == "ok"
    assert data["configured"] is True
    symbols = [p["symbol"] for p in data["prices"]]
    assert symbols == ["BTC", "ETH", "USDT", "BNB", "SOL"]
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_fetch_market_board_acp_tracks_wacp(monkeypatch):
    coingecko.clear_cache()
    market_economy.clear_oracle_cache()
    monkeypatch.setenv("COINGECKO_API_KEY", "CG-test-key")
    monkeypatch.setenv("WACP_ORACLE_PIN_DESK", "false")
    from app.config import get_settings

    get_settings.cache_clear()

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, params=None, headers=None):
            url_s = str(url)
            if "geckoterminal.com" in url_s and "pools/0xf391" in url_s:
                return _Resp(
                    200,
                    {
                        "data": {
                            "attributes": {"base_token_price_usd": "0.00042"},
                        }
                    },
                )
            if "geckoterminal.com" in url_s:
                return _Resp(404, {})
            return _Resp(
                200,
                {
                    "bitcoin": {"usd": 100000.0, "last_updated_at": 1},
                    "ethereum": {"usd": 3500.0, "last_updated_at": 1},
                    "tether": {"usd": 1.0, "last_updated_at": 1},
                    "binancecoin": {"usd": 600.0, "last_updated_at": 1},
                    "solana": {"usd": 150.0, "last_updated_at": 1},
                },
            )

    monkeypatch.setattr(coingecko.httpx, "AsyncClient", _Client)
    monkeypatch.setattr(market_economy.httpx, "AsyncClient", _Client)
    data = await coingecko.fetch_market_board()
    assert data["status"] == "ok"
    symbols = [p["symbol"] for p in data["prices"]]
    assert symbols[:3] == ["ACP", "wACP", "sACP"]
    acp = next(p for p in data["prices"] if p["symbol"] == "ACP")
    wacp = next(p for p in data["prices"] if p["symbol"] == "wACP")
    # Bridge 1 ACP ↔ 10 wACP: ACP USD = 10 × wACP DEX USD.
    assert float(wacp["price"]) == 0.00042
    assert float(acp["price"]) == 0.0042
    sacp = next(p for p in data["prices"] if p["symbol"] == "sACP")
    assert float(sacp["price"]) == 1.0
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_wacp_geckoterminal_official_pool(monkeypatch):
    coingecko.clear_cache()
    market_economy.clear_oracle_cache()
    monkeypatch.setenv("COINGECKO_API_KEY", "")
    monkeypatch.setenv("WACP_ORACLE_PIN_DESK", "false")
    from app.config import get_settings

    get_settings.cache_clear()

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, params=None, headers=None):
            url_s = str(url)
            if "pools/0xf391" in url_s:
                return _Resp(
                    200,
                    {
                        "data": {
                            "attributes": {
                                "base_token_price_usd": "0.00042",
                            }
                        }
                    },
                )
            return _Resp(200, {"data": {"attributes": {"price_usd": None}}})

    monkeypatch.setattr(coingecko.httpx, "AsyncClient", _Client)
    monkeypatch.setattr(market_economy.httpx, "AsyncClient", _Client)
    board = await coingecko.fetch_market_board()
    wacp = next(p for p in board["prices"] if p["symbol"] == "wACP")
    assert float(wacp["price"]) == 0.00042
    assert any("geckoterminal" in n for n in board["notes"])
    rate = market_economy.usdt_to_acp_desk_rate()
    # ACP per USDT = 1 / (10 × wACP USD).
    assert rate == (Decimal("1") / Decimal("0.0042")).quantize(Decimal("0.00000001"))
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_quote_catalog_acp_from_usd_sticker(monkeypatch):
    market_economy.clear_oracle_cache()
    monkeypatch.setenv("WACP_ORACLE_PIN_DESK", "false")
    from app.config import get_settings

    get_settings.cache_clear()
    # Seed oracle cache
    market_economy._ORACLE["at"] = __import__("time").time()
    market_economy._ORACLE["price"] = "0.000002"
    market_economy._ORACLE["source"] = "test"
    acp, sticker, spot = market_economy.quote_catalog_acp("349")
    assert sticker == Decimal("349.00")
    assert spot == Decimal("0.000002")
    assert acp == Decimal("17450000.00")  # ceil(349 / (10 × 0.000002))
    wacp_charge, _, _ = market_economy.quote_catalog_acp("349", payment_currency="WACP")
    # wACP charge = ACP liability × 10 × 0.9
    assert wacp_charge == Decimal("157050000.00")
    monkeypatch.setenv("WACP_ORACLE_PIN_DESK", "true")
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_quote_catalog_wacp_pin_desk_scales_10x(monkeypatch):
    monkeypatch.setenv("WACP_ORACLE_PIN_DESK", "true")
    from app.config import get_settings

    get_settings.cache_clear()
    acp, sticker, spot = market_economy.quote_catalog_acp("100", payment_currency="ACP")
    assert acp == Decimal("100.00")
    wacp, _, _ = market_economy.quote_catalog_acp("100", payment_currency="WACP")
    assert wacp == Decimal("900.00")  # 100 × 10 × 0.9
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_fetch_not_configured(monkeypatch):
    coingecko.clear_cache()
    market_economy.clear_oracle_cache()
    monkeypatch.setenv("COINGECKO_API_KEY", "")
    from app.config import get_settings

    get_settings.cache_clear()

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, url, params=None, headers=None):
            return _Resp(500, {})

    monkeypatch.setattr(market_economy.httpx, "AsyncClient", _Client)
    data = await coingecko.fetch_simple_prices()
    assert data["status"] == "not_configured"
    board = await coingecko.fetch_market_board()
    assert board["status"] == "partial"
    assert [p["symbol"] for p in board["prices"][:3]] == ["ACP", "wACP", "sACP"]
    get_settings.cache_clear()


def test_market_routes_registered():
    from app.main import app

    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/v1/market/prices" in paths
    assert "/v1/market/status" in paths


def test_catalog_amount_to_usd_sticker_scales_aeterna():
    assert market_economy.catalog_amount_to_usd_sticker("59") == Decimal("59.00")
    assert market_economy.catalog_amount_to_usd_sticker("8900") == Decimal("8900.00")
    assert market_economy.catalog_amount_to_usd_sticker("1000000") == Decimal("1000")
    assert market_economy.catalog_amount_to_usd_sticker("250000") == Decimal("250")
