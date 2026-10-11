"""ACP Insurance desk — policies, quotes, claims settled in ACP."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import InsuranceClaim, InsurancePolicy, InsurancePool
from app.schemas.insurance import (
    CoverageClass,
    InsuranceCatalogPublic,
    InsuranceClaimCreate,
    InsuranceClaimPublic,
    InsurancePolicyCreate,
    InsurancePolicyPublic,
    InsuranceProductPublic,
    InsuranceQuotePublic,
    InsuranceQuoteRequest,
)

_Q = Decimal("0.00000001")

_COMPLIANCE = (
    "ACP Insurance is a capital-rail prototype: premiums and claim payouts are denominated in ACP. "
    "Settlement mode is record-only until ledger debit/credit is enabled — no real ACP is moved yet. "
    "It is not a licensed insurer in any jurisdiction. Coverage terms are smart-contract hashes for "
    "desk settlement — obtain local counsel before relying on policies for regulated risk."
)

_PRODUCTS: tuple[dict[str, Any], ...] = (
    {
        "coverage_class": "wallet_theft",
        "label": "Wallet / key compromise",
        "description": "Indicative cover for device theft or reported key compromise after lock+report window.",
        "pool_id": "pool-wallet",
        "min": "100",
        "max": "250000",
        "premium_bps": 120,
        "term_days": 90,
        "asset_ref_types": ["wallet_address", "digital_passport"],
    },
    {
        "coverage_class": "bridge_ops",
        "label": "Bridge / wACP ops delay",
        "description": "Cover for documented bridge intent delay or operator pause beyond SLA window.",
        "pool_id": "pool-bridge",
        "min": "500",
        "max": "1000000",
        "premium_bps": 80,
        "term_days": 30,
        "asset_ref_types": ["bridge_intent", "exchange_ticket"],
    },
    {
        "coverage_class": "cargo_shipping",
        "label": "Cargo / goods in transit",
        "description": "OTC goods and antiques shipment risk while ticket is open.",
        "pool_id": "pool-cargo",
        "min": "250",
        "max": "500000",
        "premium_bps": 150,
        "term_days": 60,
        "asset_ref_types": ["exchange_ticket", "ownership_certificate"],
    },
    {
        "coverage_class": "real_estate",
        "label": "Real estate deal escrow",
        "description": "Title-desk escrow delay / failed closing on ACP ownership rails.",
        "pool_id": "pool-re",
        "min": "1000",
        "max": "5000000",
        "premium_bps": 60,
        "term_days": 180,
        "asset_ref_types": ["ownership_certificate", "otc_real_estate"],
    },
    {
        "coverage_class": "commodities",
        "label": "Commodities desk",
        "description": "Oil/gas/uranium/timber/ores OTC intake delivery risk (controlled materials need licenses).",
        "pool_id": "pool-commodities",
        "min": "500",
        "max": "2000000",
        "premium_bps": 100,
        "term_days": 90,
        "asset_ref_types": ["otc_commodity", "exchange_ticket"],
    },
    {
        "coverage_class": "health_travel",
        "label": "Travel / health stipend",
        "description": "Parametric travel disruption stipend paid in ACP (not medical insurance).",
        "pool_id": "pool-health",
        "min": "50",
        "max": "50000",
        "premium_bps": 200,
        "term_days": 30,
        "asset_ref_types": [],
    },
    {
        "coverage_class": "device_nfc",
        "label": "NFC / implant device",
        "description": "Biohax/NFC credential re-issuance stipend after verified loss report.",
        "pool_id": "pool-nfc",
        "min": "25",
        "max": "10000",
        "premium_bps": 180,
        "term_days": 365,
        "asset_ref_types": ["nfc_credential", "digital_passport"],
    },
    {
        "coverage_class": "cyber_incident",
        "label": "Cyber incident response",
        "description": "Org incident response budget for verified members (passport-gated).",
        "pool_id": "pool-cyber",
        "min": "1000",
        "max": "1000000",
        "premium_bps": 140,
        "term_days": 365,
        "asset_ref_types": ["organization", "digital_passport"],
    },
    {
        "coverage_class": "livestock",
        "label": "FAUNA livestock companion",
        "description": "Companion-animal auction escrow disruption cover (licensed pets only).",
        "pool_id": "pool-fauna",
        "min": "100",
        "max": "100000",
        "premium_bps": 160,
        "term_days": 60,
        "asset_ref_types": ["animal_auction_lot"],
    },
    {
        "coverage_class": "floriculture",
        "label": "FLORA flower cargo / escrow",
        "description": "Flower auction escrow disruption cover (cut/potted/seed lots; licensed florist handoff).",
        "pool_id": "pool-flora",
        "min": "50",
        "max": "250000",
        "premium_bps": 140,
        "term_days": 45,
        "asset_ref_types": ["flora_auction_lot"],
    },
    {
        "coverage_class": "space_payload",
        "label": "Space / orbital payload",
        "description": "Galaxy auction / orbital payload title-desk parametric cover.",
        "pool_id": "pool-space",
        "min": "1000",
        "max": "10000000",
        "premium_bps": 90,
        "term_days": 365,
        "asset_ref_types": ["space_auction_lot", "ownership_certificate"],
    },
    {
        "coverage_class": "perimeter_cleanup",
        "label": "Perimeter cleanup / decontamination",
        "description": "Parametric cover for licensed perimeter cleanup jobs (all contamination classes) booked via /perimeter.",
        "pool_id": "pool-perimeter",
        "min": "500",
        "max": "2000000",
        "premium_bps": 120,
        "term_days": 90,
        "asset_ref_types": ["perimeter_cleanup_job"],
    },
    {
        "coverage_class": "neonatal_install",
        "label": "Neonatal install / Installation Project",
        "description": (
            "Parametric cover for licensed Installation Project partner intakes "
            "(high-protein infant-nutrition line + neonatal hyperbaric-chamber literacy) booked via /aeterna#installation-project. "
            "Not medical malpractice insurance, not a formula warranty, and not a CE/FDA device policy."
        ),
        "pool_id": "pool-neonatal-install",
        "min": "500",
        "max": "2000000",
        "premium_bps": 130,
        "term_days": 180,
        "asset_ref_types": ["aeterna_intent_order", "installation_project_brief"],
    },
    {
        "coverage_class": "weather_control",
        "label": "Weather control / Stardust earth ops",
        "description": (
            "Parametric cover for licensed StardustSRT-style weather-control and disaster-monitoring "
            "partner intakes booked via /stardust. Not a geoengineering warranty, not official "
            "meteorological insurance, and not a guaranteed storm-dissipation outcome."
        ),
        "pool_id": "pool-weather-control",
        "min": "500",
        "max": "5000000",
        "premium_bps": 140,
        "term_days": 90,
        "asset_ref_types": [
            "stardust_service",
            "weather_control_brief",
            "tech_auction_lot",
        ],
    },
    {
        "coverage_class": "antique_fire_restore",
        "label": "Antique fire restore / conservation",
        "description": (
            "Parametric cover for licensed antique fire-restore partner briefs booked via "
            "/antique-fire-restore. Not a DIY furnace warranty, not medical burn care, not an "
            "authenticity guarantee, and not a licensed insurer payout by ANCAP."
        ),
        "pool_id": "pool-antique-fire-restore",
        "min": "500",
        "max": "2000000",
        "premium_bps": 110,
        "term_days": 180,
        "asset_ref_types": ["antique_fire_restore_brief"],
    },
    {
        "coverage_class": "custom",
        "label": "Custom everything desk",
        "description": "Catch-all parametric cover — underwriter review required before claim pay.",
        "pool_id": "pool-custom",
        "min": "100",
        "max": "10000000",
        "premium_bps": 250,
        "term_days": 90,
        "asset_ref_types": ["custom"],
    },
)


def _dec(raw: str) -> Decimal:
    try:
        value = Decimal(str(raw).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid ACP amount") from exc
    if value <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    return value.quantize(_Q, rounding=ROUND_HALF_UP)


def _fmt(value: Decimal) -> str:
    return format(value.quantize(_Q, rounding=ROUND_HALF_UP), "f")


def _hash_payload(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def _product(coverage_class: CoverageClass) -> dict[str, Any]:
    for item in _PRODUCTS:
        if item["coverage_class"] == coverage_class:
            return item
    raise HTTPException(status_code=404, detail="Unknown coverage class")


async def ensure_pools(session: AsyncSession) -> None:
    for item in _PRODUCTS:
        existing = await session.get(InsurancePool, item["pool_id"])
        if existing is not None:
            continue
        session.add(
            InsurancePool(
                id=item["pool_id"],
                label=item["label"],
                coverage_class=item["coverage_class"],
                status="open",
                collateral_spec_json={
                    "currency": "ACP",
                    "min_sum_insured_acp": item["min"],
                    "max_sum_insured_acp": item["max"],
                    "premium_bps": item["premium_bps"],
                },
            )
        )
    await session.flush()


async def catalog(session: AsyncSession) -> InsuranceCatalogPublic:
    await ensure_pools(session)
    products = [
        InsuranceProductPublic(
            coverage_class=item["coverage_class"],
            label=item["label"],
            description=item["description"],
            pool_id=item["pool_id"],
            min_sum_insured_acp=item["min"],
            max_sum_insured_acp=item["max"],
            premium_bps=item["premium_bps"],
            term_days_default=item["term_days"],
            asset_ref_types=list(item["asset_ref_types"]),
        )
        for item in _PRODUCTS
    ]
    return InsuranceCatalogPublic(
        title="ACP Insurance Desk",
        tagline="Parametric cover across wallet, bridge, cargo, real estate, commodities, space, neonatal install, weather control — premiums in ACP.",
        compliance_note=_COMPLIANCE,
        products=products,
    )


def _build_quote(body: InsuranceQuoteRequest) -> InsuranceQuotePublic:
    product = _product(body.coverage_class)
    sum_insured = _dec(body.sum_insured_acp)
    min_sum = Decimal(product["min"])
    max_sum = Decimal(product["max"])
    if sum_insured < min_sum or sum_insured > max_sum:
        raise HTTPException(
            status_code=400,
            detail=f"sum_insured_acp must be between {product['min']} and {product['max']}",
        )
    premium_bps = int(product["premium_bps"])
    premium = (sum_insured * Decimal(premium_bps) / Decimal(10000)).quantize(_Q, rounding=ROUND_HALF_UP)
    now = datetime.now(timezone.utc)
    ends = now + timedelta(days=body.term_days)
    quote_hash = _hash_payload(
        {
            "coverage_class": body.coverage_class,
            "sum_insured_acp": _fmt(sum_insured),
            "premium_acp": _fmt(premium),
            "term_days": body.term_days,
            "asset_ref_type": body.asset_ref_type,
            "asset_ref_id": body.asset_ref_id,
        }
    )
    return InsuranceQuotePublic(
        coverage_class=body.coverage_class,
        pool_id=product["pool_id"],
        sum_insured_acp=_fmt(sum_insured),
        premium_acp=_fmt(premium),
        premium_bps=premium_bps,
        term_days=body.term_days,
        starts_at=now,
        ends_at=ends,
        quote_hash=quote_hash,
    )


async def quote(session: AsyncSession, body: InsuranceQuoteRequest) -> InsuranceQuotePublic:
    await ensure_pools(session)
    return _build_quote(body)


def _policy_public(row: InsurancePolicy) -> InsurancePolicyPublic:
    return InsurancePolicyPublic(
        id=row.id,
        pool_id=row.pool_id,
        coverage_class=row.coverage_class,  # type: ignore[arg-type]
        coverage_json=row.coverage_json or {},
        asset_ref_type=row.asset_ref_type,
        asset_ref_id=row.asset_ref_id,
        sum_insured_acp=_fmt(Decimal(row.sum_insured_acp)),
        premium_acp=_fmt(Decimal(row.premium_acp)),
        status=row.status,  # type: ignore[arg-type]
        contract_hash=row.contract_hash,
        starts_at=row.starts_at,
        ends_at=row.ends_at,
        created_at=row.created_at,
    )


async def create_policy(
    session: AsyncSession,
    *,
    user_id: str,
    body: InsurancePolicyCreate,
) -> InsurancePolicyPublic:
    await ensure_pools(session)
    q = _build_quote(
        InsuranceQuoteRequest(
            coverage_class=body.coverage_class,
            sum_insured_acp=body.sum_insured_acp,
            term_days=body.term_days,
            asset_ref_type=body.asset_ref_type,
            asset_ref_id=body.asset_ref_id,
        )
    )
    policy_id = uuid.uuid4()
    contract_hash = _hash_payload(
        {
            "policy_id": str(policy_id),
            "holder": user_id,
            "quote_hash": q.quote_hash,
            "note": body.note,
        }
    )
    row = InsurancePolicy(
        id=policy_id,
        pool_id=q.pool_id,
        holder_user_id=uuid.UUID(user_id),
        coverage_class=body.coverage_class,
        coverage_json={
            "note": body.note,
            "quote_hash": q.quote_hash,
            "premium_bps": q.premium_bps,
        },
        asset_ref_type=body.asset_ref_type,
        asset_ref_id=body.asset_ref_id,
        sum_insured_acp=Decimal(q.sum_insured_acp),
        premium_acp=Decimal(q.premium_acp),
        status="active",
        contract_hash=contract_hash,
        starts_at=q.starts_at,
        ends_at=q.ends_at,
    )
    session.add(row)
    await session.flush()
    return _policy_public(row)


async def list_my_policies(session: AsyncSession, *, user_id: str) -> list[InsurancePolicyPublic]:
    q = (
        select(InsurancePolicy)
        .where(InsurancePolicy.holder_user_id == uuid.UUID(user_id))
        .order_by(InsurancePolicy.created_at.desc())
    )
    rows = list((await session.execute(q)).scalars().all())
    return [_policy_public(r) for r in rows]


async def get_policy(session: AsyncSession, *, user_id: str, policy_id: str) -> InsurancePolicyPublic:
    try:
        pid = uuid.UUID(policy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid policy_id") from exc
    row = await session.get(InsurancePolicy, str(pid))
    if row is None or str(row.holder_user_id) != user_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    return _policy_public(row)


async def get_pool(session: AsyncSession, pool_id: str) -> dict[str, Any]:
    await ensure_pools(session)
    pool = await session.get(InsurancePool, pool_id)
    if pool is None:
        raise HTTPException(status_code=404, detail="Pool not found")
    return {
        "id": pool.id,
        "label": pool.label,
        "coverage_class": pool.coverage_class,
        "status": pool.status,
        "collateral_spec": pool.collateral_spec_json,
        "created_at": pool.created_at,
    }


def _claim_public(row: InsuranceClaim) -> InsuranceClaimPublic:
    return InsuranceClaimPublic(
        id=row.id,
        policy_id=row.policy_id,
        amount_acp=_fmt(Decimal(row.amount_acp)),
        status=row.status,  # type: ignore[arg-type]
        note=row.note,
        contract_hash=row.contract_hash,
        created_at=row.created_at,
        resolved_at=row.resolved_at,
    )


async def file_claim(
    session: AsyncSession,
    *,
    user_id: str,
    policy_id: str,
    body: InsuranceClaimCreate,
) -> InsuranceClaimPublic:
    try:
        pid = uuid.UUID(policy_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid policy_id") from exc
    policy = await session.get(InsurancePolicy, str(pid))
    if policy is None or str(policy.holder_user_id) != user_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    if policy.status != "active":
        raise HTTPException(status_code=400, detail="Policy is not active")
    now = datetime.now(timezone.utc)
    starts = policy.starts_at
    ends = policy.ends_at
    if starts.tzinfo is None:
        starts = starts.replace(tzinfo=timezone.utc)
    if ends.tzinfo is None:
        ends = ends.replace(tzinfo=timezone.utc)
    if now < starts:
        raise HTTPException(status_code=400, detail="Policy has not started yet")
    if now > ends:
        policy.status = "expired"
        await session.flush()
        raise HTTPException(status_code=400, detail="Policy has expired")
    amount = _dec(body.amount_acp)
    if amount > Decimal(policy.sum_insured_acp):
        raise HTTPException(status_code=400, detail="Claim exceeds sum insured")
    claim_id = uuid.uuid4()
    contract_hash = _hash_payload(
        {
            "claim_id": str(claim_id),
            "policy_id": str(pid),
            "amount_acp": _fmt(amount),
            "evidence": body.evidence,
        }
    )
    row = InsuranceClaim(
        id=claim_id,
        policy_id=str(pid),
        claimant_user_id=uuid.UUID(user_id),
        amount_acp=amount,
        status="filed",
        ref_json=body.evidence or {},
        note=body.note,
        contract_hash=contract_hash,
    )
    policy.status = "claimed"
    session.add(row)
    await session.flush()
    return _claim_public(row)
