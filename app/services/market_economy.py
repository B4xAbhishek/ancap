"""Market-aligned ACP/wACP economy helpers.

Official wACP/USDT pool (PancakeSwap V2 / GeckoTerminal):
https://www.geckoterminal.com/bsc/pools/0xf391ca2bcbab93afa23326ebf1e35db950841601

Bridge doctrine (2026-10-04): **1 ACP ↔ 10 wACP**.
ACP USD spot ≈ 10 × wACP DEX USD; checkout ACP = usd_sticker / acp_usd.
"""

from __future__ import annotations

import re
import time
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from typing import Any

import httpx

from app.config import get_settings
from app.services.bridge_decimal import WACP_PER_ACP, acp_usd_from_wacp_usd

OFFICIAL_WACP_POOL_V2 = "0xf391ca2bcbab93afa23326ebf1e35db950841601"
# PancakeSwap V3 wACP/USDT 0.25% — bootstrap / shallow (not oracle until gated).
OFFICIAL_WACP_POOL_V3 = "0xe626bd3ef516c4f784e5d5fb46e297d9c0d7f5e1"
OFFICIAL_WACP_POOL = OFFICIAL_WACP_POOL_V2  # backward-compatible alias


def _configured_v3_pool() -> str:
    s = get_settings()
    v3 = (getattr(s, "wacp_v3_pool", None) or "").strip().lower()
    if v3 and re.fullmatch(r"0x[a-f0-9]{40}", v3):
        return v3
    return OFFICIAL_WACP_POOL_V3


def _official_pool_for_oracle() -> str:
    """Checkout oracle pool. Stays on V2 until WACP_ORACLE_USE_V3=true."""
    s = get_settings()
    if not bool(getattr(s, "wacp_oracle_use_v3", False)):
        return OFFICIAL_WACP_POOL_V2
    v3 = _configured_v3_pool()
    if v3 and re.fullmatch(r"0x[a-f0-9]{40}", v3):
        return v3
    return OFFICIAL_WACP_POOL_V2


def _gt_pool_url(pool: str) -> str:
    return f"https://api.geckoterminal.com/api/v2/networks/bsc/pools/{pool.lower()}"
_GT_TOKEN = "0x349797e2f1a4fd722af2db181ab1c4ed7606f402"
_GT_TOKEN_URL = f"https://api.geckoterminal.com/api/v2/networks/bsc/tokens/{_GT_TOKEN}"

_ORACLE: dict[str, Any] = {"at": 0.0, "price": None, "source": "none"}
_Q_SPOT = Decimal("0.00000000000001")
_Q_RATE = Decimal("0.00000001")
_Q_ACP = Decimal("0.01")
# Soft fallback when GT is unreachable (order-of-magnitude of thin-pool spot).
_FALLBACK_WACP_USD = Decimal("0.0000023189")


def _to_dec(raw: Any) -> Decimal | None:
    try:
        if raw is None:
            return None
        v = Decimal(str(raw))
        if v <= 0:
            return None
        return v
    except (InvalidOperation, ValueError, TypeError):
        return None


def _ttl() -> int:
    return int(getattr(get_settings(), "coingecko_cache_ttl_seconds", 60) or 60)


def _stale_ttl() -> int:
    return int(getattr(get_settings(), "wacp_oracle_stale_ttl_seconds", 3600) or 3600)


def _clamp_spot(spot: Decimal) -> Decimal:
    settings = get_settings()
    lo = _to_dec(getattr(settings, "wacp_oracle_min_usd", None) or "0.00000001") or Decimal(
        "0.00000001"
    )
    hi = _to_dec(getattr(settings, "wacp_oracle_max_usd", None) or "1") or Decimal("1")
    if spot < lo:
        return lo
    if spot > hi:
        return hi
    return spot


def clear_oracle_cache() -> None:
    _ORACLE["at"] = 0.0
    _ORACLE["price"] = None
    _ORACLE["source"] = "none"


def get_cached_wacp_usd(*, allow_stale: bool = True) -> Decimal | None:
    """Sync read of last good oracle spot (fresh or stale)."""
    raw = _ORACLE.get("price")
    if raw is None:
        return None
    spot = _to_dec(raw)
    if spot is None:
        return None
    age = time.time() - float(_ORACLE.get("at") or 0)
    if age <= _ttl():
        return spot
    if allow_stale and age <= _stale_ttl():
        return spot
    return None if not allow_stale else spot


def oracle_meta() -> dict[str, Any]:
    pool = _official_pool_for_oracle()
    s = get_settings()
    return {
        "pool": pool,
        "pool_v2_reference": OFFICIAL_WACP_POOL_V2,
        "pool_v3_bootstrap": _configured_v3_pool(),
        "oracle_use_v3": bool(getattr(s, "wacp_oracle_use_v3", False)),
        "source": _ORACLE.get("source") or "none",
        "price_usd": _ORACLE.get("price"),
        "cached_at": _ORACLE.get("at"),
        "pool_url": f"https://www.geckoterminal.com/bsc/pools/{pool}",
    }


async def fetch_official_pool_wacp_usd() -> Decimal | None:
    """Fetch base_token_price_usd from the official GeckoTerminal pool."""
    pool = _official_pool_for_oracle()
    gt_url = _gt_pool_url(pool)
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(gt_url, headers={"accept": "application/json"})
            if resp.status_code < 400:
                attrs = ((resp.json() or {}).get("data") or {}).get("attributes") or {}
                price = _to_dec(attrs.get("base_token_price_usd"))
                if price is not None:
                    return price
            token = await client.get(_GT_TOKEN_URL, headers={"accept": "application/json"})
            if token.status_code < 400:
                attrs = ((token.json() or {}).get("data") or {}).get("attributes") or {}
                return _to_dec(attrs.get("price_usd"))
    except Exception:  # noqa: BLE001 — soft fallback
        return None
    return None


async def get_wacp_usd_oracle() -> tuple[Decimal, str]:
    """Return clamped wACP USD spot and source label.

    Preference: fresh cache → live GT pool → stale cache → soft fallback.
    """
    now = time.time()
    cached = get_cached_wacp_usd(allow_stale=False)
    if cached is not None:
        return cached, str(_ORACLE.get("source") or "cache")

    live = await fetch_official_pool_wacp_usd()
    if live is not None:
        spot = _clamp_spot(live)
        _ORACLE["at"] = now
        _ORACLE["price"] = format(spot, "f")
        _ORACLE["source"] = "geckoterminal"
        return spot, "geckoterminal"

    stale = get_cached_wacp_usd(allow_stale=True)
    if stale is not None:
        return stale, f"stale:{_ORACLE.get('source') or 'cache'}"

    fallback = _clamp_spot(_FALLBACK_WACP_USD)
    _ORACLE["at"] = now
    _ORACLE["price"] = format(fallback, "f")
    _ORACLE["source"] = "fallback"
    return fallback, "fallback"


def usdt_to_acp_desk_rate(*, wacp_usd: Decimal | None = None) -> Decimal:
    """ACP per 1 USDT for desk/exchange quotes.

    Emergency pin: set WACP_ORACLE_PIN_DESK=true and keep USDT_TRC20_TO_ACP_RATE.
    Otherwise rate = 1 / (WACP_PER_ACP * wacp_usd) — 1 ACP ≈ 10 wACP ≈ 10× spot USD.
    """
    settings = get_settings()
    if bool(getattr(settings, "wacp_oracle_pin_desk", False)):
        pinned = _to_dec(getattr(settings, "usdt_trc20_to_acp_rate", None) or "1") or Decimal("1")
        return pinned if pinned > 0 else Decimal("1")

    spot = wacp_usd or get_cached_wacp_usd(allow_stale=True)
    if spot is None or spot <= 0:
        pinned = _to_dec(getattr(settings, "usdt_trc20_to_acp_rate", None) or "1") or Decimal("1")
        if pinned > 1:
            return pinned
        spot = _FALLBACK_WACP_USD

    acp_spot = acp_usd_from_wacp_usd(spot)
    rate = (Decimal("1") / acp_spot).quantize(_Q_RATE, rounding=ROUND_HALF_UP)
    min_rate = _to_dec(getattr(settings, "usdt_trc20_acp_rate_min", None) or "1") or Decimal("1")
    max_rate = _to_dec(getattr(settings, "usdt_trc20_acp_rate_max", None) or "1000000000000") or Decimal(
        "1000000000000"
    )
    if rate < min_rate:
        return min_rate
    if rate > max_rate:
        return max_rate
    return rate


def catalog_amount_to_usd_sticker(catalog_amount: Decimal | str) -> Decimal:
    """Map historical catalog ACP figures (desk fiction ACP≈USD) to retail USD stickers.

    Small SKUs keep their face value as USD. Mid desks (≤10k) stay as USD.
    Larger AETERNA-style figures scale by /1000 so 1_000_000 → $1000, 250_000 → $250.
    """
    amount = _to_dec(catalog_amount) or Decimal("0")
    if amount <= 0:
        return Decimal("0")
    if amount <= Decimal("10000"):
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return (amount / Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def usd_to_acp(usd: Decimal | str, *, wacp_usd: Decimal | None = None) -> Decimal:
    """Convert USD sticker to ACP amount (ceil to 0.01 ACP).

    Uses ACP USD = WACP_PER_ACP × wACP DEX USD (bridge 1↔10).
    """
    sticker = _to_dec(usd) or Decimal("0")
    if sticker <= 0:
        return Decimal("0")
    spot = wacp_usd or get_cached_wacp_usd(allow_stale=True) or _FALLBACK_WACP_USD
    if spot <= 0:
        spot = _FALLBACK_WACP_USD
    acp_spot = acp_usd_from_wacp_usd(spot)
    raw = sticker / acp_spot
    return raw.quantize(_Q_ACP, rounding=ROUND_CEILING)


def quote_catalog_acp(
    catalog_amount: Decimal | str,
    *,
    payment_currency: str = "ACP",
    wacp_usd: Decimal | None = None,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (charge_amount, usd_sticker, oracle_spot) for a catalog face amount.

    Charge amount is in ``payment_currency`` units. For ACP it is the ACP liability.
    For wACP it is bridge-scaled: ``acp_liability × WACP_PER_ACP × 0.9`` (10% wACP rail
    discount), matching field-services desk doctrine (1 ACP ↔ 10 wACP).

    When WACP_ORACLE_PIN_DESK is true (tests / emergency), catalog faces are treated
    as ACP at a $1 accounting spot so existing credit balances stay meaningful.
    """
    settings = get_settings()
    pay = (payment_currency or "ACP").upper()
    if bool(getattr(settings, "wacp_oracle_pin_desk", False)):
        amount = _to_dec(catalog_amount) or Decimal("0")
        acp = amount.quantize(_Q_ACP, rounding=ROUND_HALF_UP)
        sticker = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        spot = Decimal("1")
    else:
        sticker = catalog_amount_to_usd_sticker(catalog_amount)
        spot = wacp_usd or get_cached_wacp_usd(allow_stale=True) or _FALLBACK_WACP_USD
        acp = usd_to_acp(sticker, wacp_usd=spot)

    if pay == "WACP":
        # Discount on ACP liability, then mint-scale to wACP charge units.
        charge = (acp * Decimal(WACP_PER_ACP) * Decimal("0.9")).quantize(
            _Q_ACP, rounding=ROUND_CEILING
        )
        return charge, sticker, spot
    return acp, sticker, spot


def workflow_platform_fee_percent() -> Decimal:
    settings = get_settings()
    raw = _to_dec(getattr(settings, "workflow_platform_fee_percent", None) or "10") or Decimal("10")
    if raw < 0:
        return Decimal("0")
    if raw > 50:
        return Decimal("50")
    return raw
