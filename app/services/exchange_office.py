"""ACP-hub exchange office: multi-asset catalog + all-to-all quotes.

Design:
- ACP is the universal accounting hub (1:1 with itself).
- Each listed asset has a settlement rail and a quote mode.
- Direct pairs: asset ↔ ACP (one leg).
- Cross pairs: FROM → ACP → TO (two legs, synthetic rate).
- Tickets are the mobile umbrella order; they may open an underlying rail
  order (swap desk / OTC) or instruct the client (bridge / planned fiat).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from app.config import get_settings
from app.schemas.exchange_office import (
    ExchangeAssetPublic,
    ExchangeCatalogPublic,
    ExchangePairPublic,
    ExchangeQuoteLeg,
    ExchangeQuotePublic,
    ExchangeQuoteRequest,
    SettlementRail,
)
from app.services import otc_intake as otc_svc
from app.services import sacp as sacp_svc
from app.services.bridge_decimal import WACP_PER_ACP

_Q = Decimal("0.00000001")
_HUB = "acp"

# In-process quote cache (foundation). Replace with Redis/DB for multi-worker prod.
_QUOTE_CACHE: dict[str, dict[str, Any]] = {}


def _dec(raw: str, field: str) -> Decimal:
    try:
        v = Decimal(str(raw).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise HTTPException(status_code=400, detail=f"{field} must be a decimal string") from exc
    if v <= 0:
        raise HTTPException(status_code=400, detail=f"{field} must be > 0")
    return v


def _api_str(v: Decimal) -> str:
    s = format(v.quantize(_Q, rounding=ROUND_HALF_UP), "f").rstrip("0").rstrip(".")
    return s or "0"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ttl_seconds() -> int:
    settings = get_settings()
    return int(getattr(settings, "exchange_quote_ttl_seconds", 120) or 120)


def _usdt_trc20_acp_rate() -> Decimal:
    from app.services.market_economy import usdt_to_acp_desk_rate

    return usdt_to_acp_desk_rate()


def _fiat_acp_rate(asset_id: str) -> Decimal | None:
    settings = get_settings()
    rates = getattr(settings, "exchange_fiat_acp_rates", None) or {}
    raw = rates.get(asset_id) or rates.get(asset_id.replace("fiat_", ""))
    if raw is None:
        return None
    return Decimal(str(raw))


def _acp_to_usdt_smart_pay() -> Decimal:
    """Soft reverse for foundation quotes (smart-pay uses ~0.25 USDT per ACP)."""
    settings = get_settings()
    raw = getattr(settings, "exchange_acp_to_usdt_rate", None)
    if raw:
        return Decimal(str(raw))
    # Prefer inverse of desk rate when desk is 1:1 or better defined.
    desk = _usdt_trc20_acp_rate()
    if desk > 0:
        return (Decimal("1") / desk).quantize(_Q, rounding=ROUND_HALF_UP)
    return Decimal("0.25")


def build_assets() -> list[ExchangeAssetPublic]:
    settings = get_settings()
    metals = []
    for kind, label in otc_svc.METAL_LABELS.items():
        metals.append(
            ExchangeAssetPublic(
                id=f"metal_{kind}",
                symbol={"gold": "AU", "silver": "AG", "platinum": "PT", "palladium": "PD"}[kind],
                label=label,
                kind="metal",
                availability="live",
                direction="into_acp",
                rail="otc_metal",
                quote_mode="indicative",
                unit="g",
                decimals=4,
                note="OTC desk intake after assay. Indicative ACP/g.",
                metadata={
                    "metal": kind,
                    "acp_per_gram": _api_str(otc_svc.metal_rate_acp_per_gram(kind)),  # type: ignore[arg-type]
                },
            )
        )

    goods = []
    for cat, label in otc_svc.GOODS_LABELS.items():
        goods.append(
            ExchangeAssetPublic(
                id=f"goods_{cat}",
                symbol="GOODS",
                label=label,
                kind="goods",
                availability="live",
                direction="into_acp",
                rail="otc_goods",
                quote_mode="rfq",
                unit="lot",
                decimals=0,
                note="User estimate → desk review → ACP settlement.",
                metadata={"category": cat},
            )
        )

    commodities = []
    for kind, label in otc_svc.COMMODITY_LABELS.items():
        unit = otc_svc.COMMODITY_UNITS[kind]
        commodities.append(
            ExchangeAssetPublic(
                id=f"commodity_{kind}",
                symbol=kind.upper()[:8],
                label=label,
                kind="commodity",
                availability="live",
                direction="into_acp",
                rail="otc_commodity",
                quote_mode="indicative",
                unit=unit,
                decimals=4,
                note=f"OTC commodity intake. Indicative ACP/{unit}.",
                metadata={
                    "commodity": kind,
                    "acp_per_unit": _api_str(otc_svc.commodity_rate_acp_per_unit(kind)),  # type: ignore[arg-type]
                },
            )
        )

    real_estate = []
    for deal, label in otc_svc.REAL_ESTATE_LABELS.items():
        real_estate.append(
            ExchangeAssetPublic(
                id=f"real_estate_{deal}",
                symbol="RE",
                label=label,
                kind="real_estate",
                availability="live",
                direction="into_acp",
                rail="otc_real_estate",
                quote_mode="rfq",
                unit="lot",
                decimals=0,
                note="Sale or rental RFQ → title desk → ACP. Issue ownership certificate after review.",
                metadata={"deal_type": deal},
            )
        )

    space_assets = []
    for cls, label in otc_svc.SPACE_LABELS.items():
        space_assets.append(
            ExchangeAssetPublic(
                id=f"space_{cls}",
                symbol="SPACE",
                label=label,
                kind="space",
                availability="beta",
                direction="into_acp",
                rail="otc_space",
                quote_mode="rfq",
                unit="lot",
                decimals=0,
                note="Space-object title RFQ — compliance heavy; ACP ownership certificate available.",
                metadata={"object_class": cls},
            )
        )

    ip_assets = []
    for kind, label in otc_svc.IP_LABELS.items():
        ip_assets.append(
            ExchangeAssetPublic(
                id=f"ip_{kind}",
                symbol="IP",
                label=label,
                kind="ip",
                availability="live",
                direction="into_acp",
                rail="otc_ip",
                quote_mode="rfq",
                unit="lot",
                decimals=0,
                note=(
                    "Patent/invention RFQ → desk → ACP. Issue patent_invention ownership certificate after review."
                    if kind == "patent"
                    else "Recipe/formula RFQ (hash only) → desk → ACP. Issue recipe_formula ownership certificate after review."
                ),
                metadata={
                    "ip_kind": kind,
                    "ownership_asset_class": otc_svc.IP_OWNERSHIP_CLASS[kind],
                },
            )
        )

    bridge_live = bool(getattr(settings, "bridge_rail_enabled", False)) and not bool(
        getattr(settings, "bridge_rail_paused", False)
    )
    fiat_rates = getattr(settings, "exchange_fiat_acp_rates", None) or {"usd": "1", "eur": "1.08"}

    assets: list[ExchangeAssetPublic] = [
        ExchangeAssetPublic(
            id="acp",
            symbol="ACP",
            label="ACP",
            kind="native",
            availability="live",
            direction="both",
            rail="ledger",
            quote_mode="identity",
            unit="ACP",
            decimals=8,
            network="acp",
            note="Platform accounting hub.",
        ),
        ExchangeAssetPublic(
            id="wacp_bsc",
            symbol="wACP",
            label="wACP (BSC)",
            kind="crypto",
            availability="live" if bridge_live else "beta",
            direction="both",
            rail="bridge",
            quote_mode="bridge_1_10",
            unit="wACP",
            decimals=18,
            network="bsc",
            note="Bridge 1 ACP ↔ 10 wACP with reserve proof. Mint/redeem via bridge intents.",
            metadata={"pair_hint": "wACP/USDT on PancakeSwap"},
        ),
        ExchangeAssetPublic(
            id="sacp_bsc",
            symbol="sACP",
            label="sACP (Stable ACP)",
            kind="stablecoin",
            availability="beta" if sacp_svc.is_enabled() and not sacp_svc.is_paused() else "planned",
            direction="both",
            rail="stablecoin",
            quote_mode="stable_peg",
            unit="sACP",
            decimals=18,
            network="bsc",
            note=(
                "USD-targeted ACP-collateralized stablecoin. Soft peg — not a guaranteed "
                "fiat redemption. Distinct from wACP wrap."
            ),
            metadata={
                "peg_target": "USD",
                "acp_per_usd": _api_str(sacp_svc.acp_per_usd()),
                "min_collateral_ratio": _api_str(sacp_svc.min_collateral_ratio()),
                "docs": "/docs/sacp",
            },
        ),
        ExchangeAssetPublic(
            id="usdt_trc20",
            symbol="USDT",
            label="USDT (TRC-20)",
            kind="crypto",
            availability="live",
            direction="into_acp",
            rail="swap_desk",
            quote_mode="fixed",
            unit="USDT",
            decimals=6,
            network="tron",
            note="Manual deposit desk → ACP after review.",
            metadata={"rate_acp_per_usdt": _api_str(_usdt_trc20_acp_rate())},
        ),
        ExchangeAssetPublic(
            id="usdt_bsc",
            symbol="USDT",
            label="USDT (BSC)",
            kind="crypto",
            availability="beta",
            direction="both",
            rail="dex_deep_link",
            quote_mode="market_feed",
            unit="USDT",
            decimals=18,
            network="bsc",
            note="Via wACP/USDT DEX deep-link until in-app router lands. Spot context: GET /v1/market/prices (CoinGecko).",
            metadata={"rate_source_hint": "coingecko_spot_context"},
        ),
        ExchangeAssetPublic(
            id="fiat_usd",
            symbol="USD",
            label="US Dollar",
            kind="fiat",
            availability="planned",
            direction="both",
            rail="fiat_onramp",
            quote_mode="fixed",
            unit="USD",
            decimals=2,
            note="Partner on-ramp / Stripe adapter track — quotes are placeholders.",
            metadata={"acp_per_unit": str(fiat_rates.get("usd", "1"))},
        ),
        ExchangeAssetPublic(
            id="fiat_eur",
            symbol="EUR",
            label="Euro",
            kind="fiat",
            availability="planned",
            direction="both",
            rail="fiat_onramp",
            quote_mode="fixed",
            unit="EUR",
            decimals=2,
            note="Partner on-ramp track — quotes are placeholders.",
            metadata={"acp_per_unit": str(fiat_rates.get("eur", "1.08"))},
        ),
        *metals,
        *goods,
        *commodities,
        *real_estate,
        *space_assets,
        *ip_assets,
    ]
    return assets


def _asset_map() -> dict[str, ExchangeAssetPublic]:
    return {a.id: a for a in build_assets()}


def _can_into_acp(asset: ExchangeAssetPublic) -> bool:
    if asset.id == _HUB:
        return True
    return asset.direction in ("into_acp", "both")


def _can_from_acp(asset: ExchangeAssetPublic) -> bool:
    """Outbound from ACP — includes indicative reverses for crypto desks."""
    if asset.id == _HUB:
        return True
    if asset.kind in ("metal", "goods", "commodity", "real_estate", "space", "ip"):
        return False
    if asset.direction in ("from_acp", "both"):
        return True
    # Foundation: allow indicative ACP→USDT even when desk is into-only.
    if asset.kind == "crypto" and asset.symbol == "USDT":
        return True
    if asset.rail == "fiat_onramp":
        return True
    return False


def _pair_available(src: ExchangeAssetPublic, dst: ExchangeAssetPublic) -> tuple[bool, str | None]:
    if src.id == dst.id:
        return False, "Same asset"
    if dst.kind in ("metal", "goods", "commodity", "real_estate", "space", "ip"):
        return False, "Desk does not dispense physical/title assets yet"
    if src.id == _HUB:
        if not _can_from_acp(dst):
            return False, "No outbound rail"
        return True, None
    if dst.id == _HUB:
        if not _can_into_acp(src):
            return False, "No into-ACP rail"
        return True, None
    # Cross via hub
    if not _can_into_acp(src):
        return False, "Cannot convert from_asset into ACP"
    if not _can_from_acp(dst):
        return False, "Cannot convert ACP into to_asset"
    return True, None


def build_pairs(assets: list[ExchangeAssetPublic] | None = None) -> list[ExchangePairPublic]:
    assets = assets or build_assets()
    pairs: list[ExchangePairPublic] = []
    for src in assets:
        for dst in assets:
            if src.id == dst.id:
                continue
            ok, note = _pair_available(src, dst)
            if not ok:
                continue
            legs = 1 if (_HUB in (src.id, dst.id)) else 2
            if legs == 1:
                rail: SettlementRail = src.rail if dst.id == _HUB else dst.rail
            else:
                rail = "hub_cross"
            # Worst availability of the two
            avail = src.availability
            if dst.availability == "planned" or src.availability == "planned":
                avail = "planned"
            elif dst.availability == "beta" or src.availability == "beta":
                avail = "beta"
            pairs.append(
                ExchangePairPublic(
                    from_asset=src.id,
                    to_asset=dst.id,
                    available=avail != "planned",
                    rail=rail,
                    legs=legs,
                    availability=avail,
                    note=note,
                )
            )
    return pairs


def catalog() -> ExchangeCatalogPublic:
    assets = build_assets()
    return ExchangeCatalogPublic(
        hub_asset=_HUB,
        model="acp_hub",
        assets=assets,
        pairs=build_pairs(assets),
        quote_ttl_seconds=_ttl_seconds(),
        handoff_note=otc_svc.handoff_instructions(),
        compliance_note=(
            "Phone exchange office: ACP is the hub. Crypto desks, OTC metals/goods, "
            "the wACP bridge, and sACP (USD-targeted stablecoin) settle through supervised rails. "
            "Fiat on-ramp is planned. Indicative quotes are not final bids."
        ),
    )


def _to_acp(asset: ExchangeAssetPublic, amount: Decimal, *, purity_ppt: int | None, goods_estimate: str | None) -> tuple[Decimal, str, SettlementRail]:
    if asset.id == _HUB:
        return amount, "1 ACP = 1 ACP", "ledger"

    if asset.rail == "swap_desk" and asset.id == "usdt_trc20":
        rate = _usdt_trc20_acp_rate()
        return amount * rate, f"{_api_str(rate)} ACP per USDT (desk)", "swap_desk"

    if asset.rail == "bridge" and asset.id == "wacp_bsc":
        acp = (amount / Decimal(WACP_PER_ACP)).quantize(_Q, rounding=ROUND_DOWN)
        return acp, f"{WACP_PER_ACP} wACP = 1 ACP (bridge floor)", "bridge"

    if asset.rail == "stablecoin" and asset.id == "sacp_bsc":
        acp = sacp_svc.indicative_acp_for_sacp(amount)
        return (
            acp,
            (
                f"Indicative {_api_str(acp / amount if amount else Decimal('0'))} ACP per sACP "
                f"(USD target × min collateral {_api_str(sacp_svc.min_collateral_ratio())})"
            ),
            "stablecoin",
        )

    if asset.rail == "otc_metal":
        metal = str(asset.metadata.get("metal") or "")
        ppt = purity_ppt if purity_ppt is not None else 999
        q = otc_svc.quote_metal(metal=metal, weight_grams=_api_str(amount), purity_ppt=ppt)  # type: ignore[arg-type]
        return Decimal(q.estimated_acp_amount), q.rate_note, "otc_metal"

    if asset.rail == "otc_goods":
        est = goods_estimate or _api_str(amount)
        # For goods, from_amount is lots; ACP comes from estimate field (or amount as ACP estimate).
        q = otc_svc.quote_goods(
            category=str(asset.metadata.get("category") or "other"),  # type: ignore[arg-type]
            estimated_value_acp=est,
        )
        return Decimal(q.estimated_acp_amount), q.rate_note, "otc_goods"

    if asset.rail == "otc_commodity":
        commodity = str(asset.metadata.get("commodity") or "")
        q = otc_svc.quote_commodity(commodity=commodity, quantity=_api_str(amount))  # type: ignore[arg-type]
        return Decimal(q.estimated_acp_amount), q.rate_note, "otc_commodity"

    if asset.rail == "otc_real_estate":
        deal = str(asset.metadata.get("deal_type") or "sale")
        est = goods_estimate or _api_str(amount)
        q = otc_svc.quote_real_estate(deal_type=deal, estimated_value_acp=est)  # type: ignore[arg-type]
        return Decimal(q.estimated_acp_amount), q.rate_note, "otc_real_estate"

    if asset.rail == "otc_space":
        cls = str(asset.metadata.get("object_class") or "satellite")
        est = goods_estimate or _api_str(amount)
        q = otc_svc.quote_space(object_class=cls, estimated_value_acp=est)  # type: ignore[arg-type]
        return Decimal(q.estimated_acp_amount), q.rate_note, "otc_space"

    if asset.rail == "otc_ip":
        kind = str(asset.metadata.get("ip_kind") or "patent")
        est = goods_estimate or _api_str(amount)
        q = otc_svc.quote_ip(kind=kind, estimated_value_acp=est)  # type: ignore[arg-type]
        return Decimal(q.estimated_acp_amount), q.rate_note, "otc_ip"

    if asset.rail == "dex_deep_link" and asset.id == "usdt_bsc":
        # Foundation: treat similar to reverse smart-pay USDT rate until market feed exists.
        rate = _usdt_trc20_acp_rate()
        return amount * rate, f"Indicative {_api_str(rate)} ACP per USDT (DEX path via wACP)", "dex_deep_link"

    if asset.rail == "fiat_onramp":
        rate = _fiat_acp_rate(asset.id) or _fiat_acp_rate(asset.symbol.lower()) or Decimal("1")
        return amount * rate, f"Placeholder {_api_str(rate)} ACP per {asset.symbol}", "fiat_onramp"

    raise HTTPException(status_code=400, detail=f"No into-ACP quote path for {asset.id}")


def _from_acp(asset: ExchangeAssetPublic, acp_amount: Decimal) -> tuple[Decimal, str, SettlementRail]:
    if asset.id == _HUB:
        return acp_amount, "1 ACP = 1 ACP", "ledger"

    if asset.id == "wacp_bsc":
        out = (acp_amount * Decimal(WACP_PER_ACP)).quantize(_Q, rounding=ROUND_HALF_UP)
        return out, f"1 ACP = {WACP_PER_ACP} wACP (bridge)", "bridge"

    if asset.id == "sacp_bsc":
        out = sacp_svc.indicative_sacp_for_acp(acp_amount)
        return (
            out,
            (
                f"Indicative {_api_str(out / acp_amount if acp_amount else Decimal('0'))} sACP per ACP "
                f"(USD soft peg, min collateral {_api_str(sacp_svc.min_collateral_ratio())})"
            ),
            "stablecoin",
        )

    if asset.id in ("usdt_trc20", "usdt_bsc"):
        rate = _acp_to_usdt_smart_pay()
        return acp_amount * rate, f"Indicative {_api_str(rate)} USDT per ACP", asset.rail

    if asset.rail == "fiat_onramp":
        rate = _fiat_acp_rate(asset.id) or Decimal("1")
        if rate <= 0:
            raise HTTPException(status_code=400, detail="Invalid fiat rate")
        out = acp_amount / rate
        return out, f"Placeholder 1 {asset.symbol} ≈ {_api_str(rate)} ACP", "fiat_onramp"

    if asset.kind in ("metal", "goods", "commodity", "real_estate", "space", "ip"):
        raise HTTPException(status_code=400, detail="Outbound metals/goods/commodities not offered yet")

    raise HTTPException(status_code=400, detail=f"No from-ACP quote path for {asset.id}")


def _purge_expired_quotes() -> None:
    now = _utcnow()
    dead = [k for k, v in _QUOTE_CACHE.items() if datetime.fromisoformat(v["expires_at"]) <= now]
    for k in dead:
        _QUOTE_CACHE.pop(k, None)


def get_cached_quote(quote_id: str) -> dict[str, Any] | None:
    _purge_expired_quotes()
    return _QUOTE_CACHE.get(quote_id)


def quote(req: ExchangeQuoteRequest) -> ExchangeQuotePublic:
    assets = _asset_map()
    src = assets.get(req.from_asset)
    dst = assets.get(req.to_asset)
    if not src or not dst:
        raise HTTPException(status_code=404, detail="Unknown asset id")
    if src.id == dst.id:
        raise HTTPException(status_code=400, detail="from_asset and to_asset must differ")

    ok, reason = _pair_available(src, dst)
    if not ok:
        raise HTTPException(status_code=400, detail=reason or "Pair unavailable")

    amount = _dec(req.from_amount, "from_amount")
    legs: list[ExchangeQuoteLeg] = []
    indicative = False

    if dst.id == _HUB:
        acp_amt, note, rail = _to_acp(
            src, amount, purity_ppt=req.purity_ppt, goods_estimate=req.goods_estimate_acp
        )
        legs.append(
            ExchangeQuoteLeg(
                from_asset=src.id,
                to_asset=_HUB,
                from_amount=_api_str(amount),
                to_amount=_api_str(acp_amt),
                rate=_api_str(acp_amt / amount) if amount else "0",
                rail=rail,
                quote_mode=src.quote_mode,
                note=note,
            )
        )
        to_amount = acp_amt
        hub = acp_amt
        final_rail: SettlementRail = rail
        indicative = src.quote_mode in ("indicative", "rfq", "market_feed") or src.availability != "live"
        next_step = {
            "swap_desk": "Open ticket → send USDT TRC-20 with deposit reference → confirm.",
            "otc_metal": "Open ticket → hand off metal with intake reference → confirm proof.",
            "otc_goods": "Open ticket → hand off goods with intake reference → confirm proof.",
            "otc_commodity": "Open ticket → hand off commodity lot with intake reference → confirm proof.",
            "otc_real_estate": "Open ticket → submit deed/lease package with intake reference → confirm proof.",
            "otc_space": "Open ticket → submit space-title package with intake reference → confirm proof.",
            "otc_ip": "Open ticket → submit patent/recipe document_hash package with intake reference → confirm proof.",
            "bridge": "Open bridge intent (BSC→ACP) and wait for mint/payout.",
            "dex_deep_link": "Use in-app DEX deep-link / smart-pay route when available.",
            "fiat_onramp": "Fiat on-ramp not live — waitlist / partner rail.",
            "ledger": "Already ACP.",
        }.get(rail, "Follow ticket next_step.")
    elif src.id == _HUB:
        out_amt, note, rail = _from_acp(dst, amount)
        legs.append(
            ExchangeQuoteLeg(
                from_asset=_HUB,
                to_asset=dst.id,
                from_amount=_api_str(amount),
                to_amount=_api_str(out_amt),
                rate=_api_str(out_amt / amount) if amount else "0",
                rail=rail,
                quote_mode=dst.quote_mode,
                note=note,
            )
        )
        to_amount = out_amt
        hub = amount
        final_rail = rail
        indicative = dst.quote_mode in ("indicative", "rfq", "market_feed") or dst.availability != "live"
        next_step = {
            "bridge": "Open ACP→BSC bridge intent (burn/mint path).",
            "dex_deep_link": "Bridge to wACP then swap on DEX, or smart-pay route.",
            "swap_desk": "ACP→USDT TRC-20 desk not automated yet — operator rail.",
            "fiat_onramp": "Fiat off-ramp planned.",
            "ledger": "Already ACP.",
        }.get(rail, "Follow ticket next_step.")
    else:
        # Cross: FROM → ACP → TO
        acp_amt, note1, rail1 = _to_acp(
            src, amount, purity_ppt=req.purity_ppt, goods_estimate=req.goods_estimate_acp
        )
        out_amt, note2, rail2 = _from_acp(dst, acp_amt)
        legs.append(
            ExchangeQuoteLeg(
                from_asset=src.id,
                to_asset=_HUB,
                from_amount=_api_str(amount),
                to_amount=_api_str(acp_amt),
                rate=_api_str(acp_amt / amount) if amount else "0",
                rail=rail1,
                quote_mode=src.quote_mode,
                note=note1,
            )
        )
        legs.append(
            ExchangeQuoteLeg(
                from_asset=_HUB,
                to_asset=dst.id,
                from_amount=_api_str(acp_amt),
                to_amount=_api_str(out_amt),
                rate=_api_str(out_amt / acp_amt) if acp_amt else "0",
                rail=rail2,
                quote_mode=dst.quote_mode,
                note=note2,
            )
        )
        to_amount = out_amt
        hub = acp_amt
        final_rail = "hub_cross"
        indicative = True
        next_step = (
            f"Two-leg hub exchange: settle {src.id}→ACP via {rail1}, then ACP→{dst.id} via {rail2}."
        )

    expires = _utcnow() + timedelta(seconds=_ttl_seconds())
    quote_id = str(uuid4())
    rate_from_to = _api_str(to_amount / amount) if amount else "0"
    public = ExchangeQuotePublic(
        quote_id=quote_id,
        from_asset=src.id,
        to_asset=dst.id,
        from_amount=_api_str(amount),
        to_amount=_api_str(to_amount),
        acp_hub_amount=_api_str(hub),
        rate_from_to=rate_from_to,
        legs=legs,
        rail=final_rail,
        expires_at=expires.isoformat(),
        indicative=indicative,
        rate_note="; ".join(n for n in (leg.note for leg in legs) if n),
        next_step=next_step,
    )
    _QUOTE_CACHE[quote_id] = {
        "expires_at": public.expires_at,
        "payload": public.model_dump(),
        "fingerprint": hashlib.sha256(
            f"{src.id}:{dst.id}:{public.from_amount}:{public.to_amount}".encode()
        ).hexdigest(),
    }
    return public


def make_intake_reference() -> str:
    return f"XO-{secrets.token_hex(4).upper()}"
