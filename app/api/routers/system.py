import asyncio
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.api.deps import require_auth
from app.api.deps import require_platform_admin
from app.config import get_settings
from app.db.models import AcpSwapOrder, DecisionLog, ReferralOnchainPayoutJob, SystemJobRun
from app.jobs.activity_feed_materialize_tick import activity_feed_materialize_tick
from app.jobs.agent_relationships_upsert import upsert_agent_relationships_from_orders
from app.jobs.bridge_rail_tick import bridge_rail_tick
from app.jobs.circuit_breaker_by_metric import circuit_breaker_by_metric_tick
from app.jobs.edges_daily_upsert import upsert_edges_daily_from_orders
from app.jobs.evolution_auto_ab import auto_ab_tick
from app.jobs.evolution_auto_limits import auto_limits_tick
from app.jobs.evolution_auto_quarantine import auto_quarantine_tick
from app.jobs.faucet_abuse_check_tick import faucet_abuse_check_tick
from app.jobs.governance_checks_tick import governance_checks_tick
from app.jobs.graph_enforcement_tick import graph_enforcement_tick
from app.jobs.growth_metrics_rollup_tick import growth_metrics_rollup_tick
from app.jobs.leaderboard_recompute_tick import leaderboard_recompute_tick
from app.jobs.mobile_acp_indexer_tick import mobile_acp_indexer_tick
from app.jobs.notifications_fanout_tick import notifications_fanout_tick
from app.jobs.referral_rewards_tick import referral_rewards_tick
from app.jobs.subscriptions_tick import subscriptions_tick
from app.jobs.reputation_tick import reputation_tick
from app.jobs.staking_rewards_tick import staking_rewards_tick
from app.schemas import DecisionLogPublic
from app.services.cache import redis_ping
from app.services.helio_commerce import helio_is_configured
from app.services.stripe_payments import SUPPORTED_STRIPE_CURRENCIES, stripe_is_configured
from app.services.graph_enforcement_preview import build_graph_enforcement_preview
from app.services.ledger import check_ledger_invariant, is_ledger_invariant_halted, set_ledger_invariant_halted

router = APIRouter(prefix="/system", tags=["System"])
_internal_router = APIRouter(prefix="/internal/ops", tags=["Internal Ops"])

_LLM_PROBE_CACHE_TTL_S = 60.0
_ACP_RPC_PROBE_CACHE_TTL_S = 30.0
_SYSTEM_JOBS_TICK_MAX_ATTEMPTS = 3
_SYSTEM_JOBS_TICK_RETRY_DELAYS_S = (60, 300)

_llm_probe_cache: dict[str, Any] = {"expires_at": 0.0, "value": {"status": "unknown", "error": None, "checked_at": None}}
_llm_probe_task: asyncio.Task[Any] | None = None

_acp_rpc_probe_cache: dict[str, Any] = {"expires_at": 0.0, "value": {"status": "unknown", "ok": False, "error": None, "checked_at": None}}
_acp_rpc_probe_task: asyncio.Task[Any] | None = None


def _is_llm_configured(settings) -> bool:
    provider = (settings.llm_provider or "").lower()
    if provider == "teneta_claude":
        return bool(settings.anthropic_api_key and settings.anthropic_base_url)
    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "ollama":
        return bool(settings.ollama_base_url)
    return False


def _build_llm_check(
    settings,
    probe: dict[str, Any] | None = None,
    *,
    require_probe_success: bool = False,
) -> dict[str, Any]:
    llm_configured = _is_llm_configured(settings)
    provider = (settings.llm_provider or "").lower()
    provider_disabled = provider.startswith("disabled")
    probe_status = str((probe or {}).get("status") or "unknown")
    probe_error = (probe or {}).get("error")

    if require_probe_success and llm_configured and not provider_disabled:
        llm_ok = probe_status == "ok"
    else:
        llm_ok = probe_status == "ok" or llm_configured or settings.llm_fallback_to_template or provider_disabled

    return {
        "ok": llm_ok,
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "configured": llm_configured,
        "fallback_enabled": settings.llm_fallback_to_template,
        "probe_status": probe_status,
        "probe_error": probe_error,
        "probe_cached": bool((probe or {}).get("checked_at")),
        "probe_checked_at": (probe or {}).get("checked_at"),
    }


async def _refresh_llm_probe_cache() -> None:
    settings = get_settings()
    probe_status = "unknown"
    probe_error: str | None = None

    if _is_llm_configured(settings) and not (settings.llm_provider or "").startswith("disabled"):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
                payload = {"model": settings.llm_model, "max_tokens": 1, "messages": [{"role": "user", "content": "ping"}]}
                response = await client.post(f"{settings.anthropic_base_url}/v1/messages", headers=headers, json=payload)
                probe_status = "ok" if response.status_code == 200 else "degraded"
                if response.status_code != 200:
                    probe_error = f"HTTP {response.status_code}"
        except Exception as exc:
            probe_status = "degraded"
            probe_error = str(exc)[:120]

    _llm_probe_cache["value"] = {
        "status": probe_status,
        "error": probe_error,
        "checked_at": int(time.time()),
    }
    _llm_probe_cache["expires_at"] = time.monotonic() + _LLM_PROBE_CACHE_TTL_S


def _clear_llm_probe_task(task: asyncio.Task[Any]) -> None:
    global _llm_probe_task
    _llm_probe_task = None
    try:
        task.exception()
    except Exception:
        pass


def _schedule_llm_probe_refresh() -> None:
    global _llm_probe_task
    if _llm_probe_task and not _llm_probe_task.done():
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    _llm_probe_task = loop.create_task(_refresh_llm_probe_cache())
    _llm_probe_task.add_done_callback(_clear_llm_probe_task)


def _get_cached_llm_probe() -> dict[str, Any]:
    return dict(_llm_probe_cache.get("value") or {"status": "unknown", "error": None, "checked_at": None})


def _get_or_schedule_llm_probe() -> dict[str, Any]:
    if time.monotonic() >= float(_llm_probe_cache.get("expires_at") or 0.0):
        _schedule_llm_probe_refresh()
    return _get_cached_llm_probe()


async def _refresh_acp_rpc_probe_cache() -> None:
    settings = get_settings()
    rpc_url = (settings.acp_rpc_url or "").strip()
    rpc_ok = False
    rpc_error: str | None = None
    probe_status = "disabled" if not rpc_url else "unknown"

    if rpc_url:
        try:
            from app.services.acp_rpc import acp_rpc_headers

            body = {"jsonrpc": "2.0", "id": 1, "method": "getblockcount", "params": {}}
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(rpc_url, json=body, headers=acp_rpc_headers())
            payload = response.json()
            rpc_ok = bool(response.status_code == 200 and not payload.get("error"))
            probe_status = "ok" if rpc_ok else "degraded"
            if not rpc_ok:
                rpc_error = str(payload.get("error") or f"status={response.status_code}")
        except Exception as exc:
            probe_status = "degraded"
            rpc_error = str(exc)[:120]

    _acp_rpc_probe_cache["value"] = {
        "status": probe_status,
        "ok": rpc_ok,
        "error": rpc_error,
        "checked_at": int(time.time()),
    }
    _acp_rpc_probe_cache["expires_at"] = time.monotonic() + _ACP_RPC_PROBE_CACHE_TTL_S


def _clear_acp_rpc_probe_task(task: asyncio.Task[Any]) -> None:
    global _acp_rpc_probe_task
    _acp_rpc_probe_task = None
    try:
        task.exception()
    except Exception:
        pass


def _schedule_acp_rpc_probe_refresh() -> None:
    global _acp_rpc_probe_task
    if _acp_rpc_probe_task and not _acp_rpc_probe_task.done():
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    _acp_rpc_probe_task = loop.create_task(_refresh_acp_rpc_probe_cache())
    _acp_rpc_probe_task.add_done_callback(_clear_acp_rpc_probe_task)


def _get_cached_acp_rpc_probe() -> dict[str, Any]:
    return dict(_acp_rpc_probe_cache.get("value") or {"status": "unknown", "ok": False, "error": None, "checked_at": None})


def _get_or_schedule_acp_rpc_probe() -> dict[str, Any]:
    if time.monotonic() >= float(_acp_rpc_probe_cache.get("expires_at") or 0.0):
        _schedule_acp_rpc_probe_refresh()
    return _get_cached_acp_rpc_probe()


@router.get("/health")
async def health():
    """Lightweight liveness probe. No external I/O."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness(session: DbSession):
    """Readiness probe: DB + Redis. No external HTTP calls."""
    checks: dict[str, bool] = {}
    try:
        await session.execute(select(func.count()).select_from(DecisionLog))
        checks["database"] = True
    except Exception:
        checks["database"] = False
    redis_ok, _ = await redis_ping()
    checks["redis"] = redis_ok
    status = "ready" if all(checks.values()) else "not_ready"
    return {"status": status, "checks": checks}


@router.get("/health/full")
async def health_full(session: DbSession):
    """Expanded public health view. Local checks only; no external probes."""
    settings = get_settings()
    checks: dict[str, dict[str, object]] = {}

    try:
        await session.execute(select(func.count()).select_from(DecisionLog))
        checks["database"] = {"ok": True}
    except Exception:
        # Never return raw exception / stack details on public health surfaces.
        checks["database"] = {"ok": False, "error": "unavailable"}

    redis_ok, _redis_error = await redis_ping()
    checks["redis"] = {
        "ok": redis_ok,
        "configured": bool(settings.redis_url),
        "error": None if redis_ok else "unavailable",
    }
    checks["llm"] = _build_llm_check(settings)
    checks["mail"] = {
        "ok": (not settings.mail_enabled) or bool(settings.smtp_host and settings.smtp_from_email),
        "enabled": settings.mail_enabled,
        "configured": bool(settings.smtp_host and settings.smtp_from_email),
    }
    checks["bridge"] = {
        "ok": not settings.bridge_rail_paused,
        "enabled": settings.bridge_rail_enabled,
        "paused": settings.bridge_rail_paused,
        "dry_run": settings.bridge_dry_run,
    }
    checks["stripe"] = {
        "ok": True,
        "configured": stripe_is_configured(),
        "webhook_secret_present": bool((settings.stripe_webhook_secret or "").strip()),
        "currencies": list(SUPPORTED_STRIPE_CURRENCIES),
    }
    checks["helio"] = {
        "ok": True,
        "configured": helio_is_configured(),
        "paylink_present": bool((settings.helio_paylink_id or "").strip()),
        "webhook_secret_present": bool((settings.helio_webhook_shared_token or "").strip()),
        "network": (settings.helio_network or "main").strip() or "main",
    }

    status = "ok" if all(bool(item.get("ok")) for item in checks.values()) else "degraded"
    return {"status": status, "checks": checks}


@_internal_router.get("/diagnostics")
async def ops_diagnostics(admin_user_id: str = Depends(require_platform_admin)):
    """Operational diagnostics. Platform-admin auth required."""
    _ = admin_user_id
    settings = get_settings()
    return {
        "status": "ok",
        "currencies": {
            "stake_to_activate_currency": settings.stake_to_activate_currency,
            "run_fee_currency": settings.run_fee_currency,
            "listing_fee_currency": settings.listing_fee_currency,
            "moderation_slash_currency": settings.moderation_slash_currency,
        },
        "acp": {
            "chain_anchor_driver": settings.chain_anchor_driver,
            "acp_rpc_url": settings.acp_rpc_url,
            "walletd_configured": bool(os.getenv("ACP_WALLETD_PATH", "").strip()),
        },
    }


@_internal_router.get("/deep-health")
async def deep_health(session: DbSession, admin_user_id: str = Depends(require_platform_admin)):
    """Full internal health with cached external probes. Platform-admin auth required."""
    _ = admin_user_id
    settings = get_settings()
    checks: dict[str, dict[str, object]] = {}

    try:
        await session.execute(select(func.count()).select_from(DecisionLog))
        checks["database"] = {"ok": True}
    except Exception:
        checks["database"] = {"ok": False, "error": "unavailable"}

    redis_ok, _redis_error = await redis_ping()
    checks["redis"] = {
        "ok": redis_ok,
        "configured": bool(settings.redis_url),
        "error": None if redis_ok else "unavailable",
    }
    checks["llm"] = _build_llm_check(settings, _get_or_schedule_llm_probe(), require_probe_success=True)
    acp_rpc_probe = _get_or_schedule_acp_rpc_probe()
    probe_error = acp_rpc_probe.get("error")
    checks["acp_rpc"] = {
        "ok": bool(acp_rpc_probe.get("ok")),
        "status": acp_rpc_probe.get("status", "unknown"),
        # Keep detail for admins but avoid raw stack/connection strings.
        "error": ("unavailable" if probe_error else None),
        "probe_cached": bool(acp_rpc_probe.get("checked_at")),
        "probe_checked_at": acp_rpc_probe.get("checked_at"),
    }
    checks["mail"] = {
        "ok": (not settings.mail_enabled) or bool(settings.smtp_host and settings.smtp_from_email),
        "enabled": settings.mail_enabled,
        "configured": bool(settings.smtp_host and settings.smtp_from_email),
    }
    checks["bridge"] = {
        "ok": not settings.bridge_rail_paused,
        "enabled": settings.bridge_rail_enabled,
        "paused": settings.bridge_rail_paused,
        "dry_run": settings.bridge_dry_run,
    }

    overall = "ok" if all(bool(item.get("ok")) for item in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}


@router.get("/fees")
async def fee_settings():
    settings = get_settings()
    return {
        "listing_fee_percent": str(getattr(settings, "listing_fee_percent", "0") or "0"),
        "listing_fee_amount": str(getattr(settings, "listing_fee_amount", "0") or "0"),
        "listing_fee_currency": settings.listing_fee_currency,
        "run_fee_percent": str(getattr(settings, "run_fee_percent", "0") or "0"),
        "run_fee_amount": str(getattr(settings, "run_fee_amount", "0") or "0"),
        "run_fee_currency": settings.run_fee_currency,
        "order_fee_percent": str(getattr(settings, "order_fee_percent", "0") or "0"),
        "referral_signup_bonus_acp": str(getattr(settings, "referral_signup_bonus_acp", "0") or "0"),
        "referral_commission_share_rate": str(getattr(settings, "referral_commission_share_rate", "0") or "0"),
    }


@router.get("/staking-economics")
async def staking_economics():
    settings = get_settings()
    return {
        "enabled": settings.staking_rewards_enabled,
        "currency": settings.staking_rewards_currency,
        "fees_share_percent": str(settings.staking_rewards_fees_share_percent),
        "slash_share_percent": str(settings.staking_rewards_slash_share_percent),
        "bootstrap_emission_daily": str(settings.staking_rewards_bootstrap_daily_emission),
        "bootstrap_emission_cap_total": str(settings.staking_rewards_bootstrap_emission_cap_total),
        "apy_floor_percent": str(settings.staking_rewards_apy_floor_percent),
        "apy_ceiling_percent": str(settings.staking_rewards_apy_ceiling_percent),
        "min_stake_for_rewards": str(settings.staking_rewards_min_stake_for_rewards),
    }


@_internal_router.get("/economy-health")
async def ops_economy_health(session: DbSession, admin_user_id: str = Depends(require_platform_admin)):
    """Bridge swap queue + referral payout job health. Platform-admin auth required."""
    _ = admin_user_id
    acp_rpc_probe = _get_or_schedule_acp_rpc_probe()
    pending_swaps = (
        await session.execute(
            select(func.count(AcpSwapOrder.id)).where(AcpSwapOrder.status.in_(("awaiting_deposit", "pending_review")))
        )
    ).scalar_one()
    pending_payout_jobs = (
        await session.execute(
            select(func.count(ReferralOnchainPayoutJob.id)).where(ReferralOnchainPayoutJob.status == "pending")
        )
    ).scalar_one()
    failed_payout_jobs = (
        await session.execute(
            select(func.count(ReferralOnchainPayoutJob.id)).where(ReferralOnchainPayoutJob.status == "failed")
        )
    ).scalar_one()
    halted = await is_ledger_invariant_halted(session)
    return {
        "acp_rpc_ok": bool(acp_rpc_probe.get("ok")),
        "acp_rpc_error": acp_rpc_probe.get("error"),
        "acp_rpc_probe_status": acp_rpc_probe.get("status", "unknown"),
        "acp_rpc_probe_cached": bool(acp_rpc_probe.get("checked_at")),
        "ledger_halted": halted,
        "pending_swaps": int(pending_swaps or 0),
        "pending_referral_payout_jobs": int(pending_payout_jobs or 0),
        "failed_referral_payout_jobs": int(failed_payout_jobs or 0),
    }


@_internal_router.get("/ledger-invariant-status")
async def ops_ledger_invariant_status(session: DbSession, user_id: str = Depends(require_platform_admin)):
    """Ledger invariant halt status. Platform admin required."""
    _ = user_id
    halted = await is_ledger_invariant_halted(session)
    return {"halted": halted}


@router.get("/graph-enforcement/preview")
async def graph_enforcement_preview_for_console(
    session: DbSession,
    user_id: str = Depends(require_auth),
    limit: int = 50,
):
    """Read-only graph enforcement preview for authenticated console users."""
    _ = user_id
    return await build_graph_enforcement_preview(session, limit=limit)


@_internal_router.get("/decision-logs", response_model=list[DecisionLogPublic])
async def ops_list_decision_logs(
    session: DbSession,
    user_id: str = Depends(require_auth),
    limit: int = 100,
    scope: str | None = None,
    reason_code: str | None = None,
):
    """Decision logs. Auth required."""
    _ = user_id
    q = select(DecisionLog).order_by(desc(DecisionLog.created_at)).limit(min(max(limit, 1), 500))
    if scope:
        q = q.where(DecisionLog.scope == scope)
    if reason_code:
        q = q.where(DecisionLog.reason_code == reason_code)
    r = await session.execute(q)
    out: list[DecisionLogPublic] = []
    for x in r.scalars().all():
        out.append(
            DecisionLogPublic(
                id=str(x.id),
                decision=x.decision,
                reason_code=x.reason_code,
                message=x.message,
                scope=x.scope,
                actor_type=x.actor_type,
                actor_id=str(x.actor_id) if x.actor_id else None,
                subject_type=x.subject_type,
                subject_id=str(x.subject_id) if x.subject_id else None,
                threshold_value=x.threshold_value,
                actual_value=x.actual_value,
                metadata_json=x.metadata_json,
                created_at=x.created_at,
            )
        )
    return out


async def _run_all_jobs(session: DbSession) -> dict:
    """Execute all scheduled jobs. Called by both sync and async tick endpoints."""
    processed = await upsert_edges_daily_from_orders(session, batch_size=2000, commit=False)
    agent_rel_processed = await upsert_agent_relationships_from_orders(session, batch_size=2000, commit=False)
    limits_updated = await auto_limits_tick(session, max_updates=100)
    quarantine_count = await auto_quarantine_tick(session, threshold=0.2)
    ab_result = await auto_ab_tick(session, min_sample_size=5, promote_percentile=0.9)
    cb_result = await circuit_breaker_by_metric_tick(session, commit=False)
    rep_result = await reputation_tick(session, max_subjects=50, since_days=7, commit=False)
    growth_referrals = await referral_rewards_tick(session, max_items=500)
    growth_notifications = await notifications_fanout_tick(session, max_events=500)
    subscriptions_summary = await subscriptions_tick(session, max_items=500)
    from app.services.workflow_ops import workflow_ops_tick
    workflow_operations = await workflow_ops_tick(max_items=2)
    growth_leaderboards = await leaderboard_recompute_tick(session)
    growth_feed = await activity_feed_materialize_tick(session, limit=200)
    growth_metrics = await growth_metrics_rollup_tick(session)
    growth_faucet_abuse = await faucet_abuse_check_tick(session, max_items=500)
    governance_checks = await governance_checks_tick(session, commit=False)
    graph_enforcement = await graph_enforcement_tick(session, max_agents=200)
    staking_rewards = await staking_rewards_tick(session)
    ledger_violations = await check_ledger_invariant(session)
    await set_ledger_invariant_halted(session, halted=len(ledger_violations) > 0)
    bridge_rail = await bridge_rail_tick(session)
    try:
        from app.services.wacp_liquidity_monitor import wacp_liquidity_monitor_tick

        wacp_liquidity = await wacp_liquidity_monitor_tick(session)
    except Exception as exc:
        wacp_liquidity = {"ok": False, "error": str(exc)[:200]}
    mobile_indexer = await mobile_acp_indexer_tick(session)
    try:
        from app.jobs.mobile_acp_indexer_tick import build_address_watchlist
        from app.services.acp_utxo_index import acp_utxo_index_tick

        extras = await build_address_watchlist(session)
        utxo_index = await acp_utxo_index_tick(
            extra_addresses=extras,
            chunk=500,
            max_chunks=4,
        )
    except Exception as exc:
        utxo_index = {"ok": False, "error": str(exc)[:200]}
    try:
        from app.services.acp_explorer_index import acp_explorer_index_tick

        explorer_index = await acp_explorer_index_tick(session, max_blocks=80)
    except Exception as exc:
        explorer_index = {"ok": False, "error": str(exc)[:200]}
    try:
        from app.api.routers.wallet_acp import _schedule_chain_scan_warm

        _schedule_chain_scan_warm()
        chain_scan_warm = {"scheduled": True}
    except Exception as exc:
        chain_scan_warm = {"scheduled": False, "error": str(exc)}
    return {
        "ok": True,
        "edges_daily_orders_processed": processed,
        "agent_relationships_orders_processed": agent_rel_processed,
        "auto_limits_updated": limits_updated,
        "auto_quarantine_count": quarantine_count,
        "auto_ab": ab_result,
        "circuit_breaker_by_metric": cb_result,
        "reputation_recomputed": rep_result["recomputed"],
        "growth_referrals": growth_referrals,
        "growth_notifications": growth_notifications,
        "subscriptions": subscriptions_summary,
        "workflow_operations": workflow_operations,
        "growth_leaderboards": growth_leaderboards,
        "growth_feed": growth_feed,
        "growth_metrics": growth_metrics,
        "growth_faucet_abuse": growth_faucet_abuse,
        "governance_checks": governance_checks,
        "graph_enforcement": graph_enforcement,
        "staking_rewards": staking_rewards,
        "ledger_invariant_violations": [{"currency": c, "sum": str(s)} for c, s in ledger_violations],
        "bridge_rail": bridge_rail,
        "wacp_liquidity": wacp_liquidity,
        "mobile_indexer": mobile_indexer,
        "acp_utxo_index": utxo_index,
        "acp_explorer_index": explorer_index,
        "chain_scan_warm": chain_scan_warm,
    }


def _serialize_system_job_run(row: SystemJobRun) -> dict[str, Any]:
    return {
        "job_run_id": str(row.id),
        "job_name": row.job_name,
        "status": row.status,
        "attempts": int(row.attempts or 0),
        "max_attempts": int(row.max_attempts or 0),
        "next_retry_at": row.next_retry_at.isoformat() if row.next_retry_at else None,
        "last_error": row.last_error,
        "started_at": row.started_at.isoformat() if row.started_at else None,
        "finished_at": row.finished_at.isoformat() if row.finished_at else None,
        "result": row.result_json,
    }


async def _execute_system_jobs_tick_run(session: AsyncSession, job_run: SystemJobRun) -> dict[str, Any]:
    job_run_id = str(job_run.id)
    now = datetime.now(UTC)
    job_run.attempts = int(job_run.attempts or 0) + 1
    job_run.status = "running"
    job_run.started_at = now
    job_run.finished_at = None
    job_run.next_retry_at = None
    await session.flush()

    try:
        result = await _run_all_jobs(session)
        job_run.status = "succeeded"
        job_run.result_json = result
        job_run.last_error = None
        job_run.finished_at = datetime.now(UTC)
        await session.commit()
        return {"ok": True, "job_run": _serialize_system_job_run(job_run), "result": result}
    except Exception as exc:
        await session.rollback()
        db_row = await session.get(SystemJobRun, job_run_id)
        if db_row is None:
            raise
        db_row.attempts = int(db_row.attempts or 0) + 1
        error_text = str(exc)[:1000]
        db_row.last_error = error_text
        db_row.result_json = None
        db_row.finished_at = datetime.now(UTC)
        if db_row.attempts >= int(db_row.max_attempts or _SYSTEM_JOBS_TICK_MAX_ATTEMPTS):
            db_row.status = "dead_letter"
            db_row.next_retry_at = None
        else:
            retry_index = max(0, min(db_row.attempts - 1, len(_SYSTEM_JOBS_TICK_RETRY_DELAYS_S) - 1))
            db_row.status = "retry"
            db_row.next_retry_at = datetime.now(UTC) + timedelta(seconds=_SYSTEM_JOBS_TICK_RETRY_DELAYS_S[retry_index])
        await session.commit()
        return {"ok": False, "job_run": _serialize_system_job_run(db_row), "error": error_text}


async def _run_pending_system_jobs_tick_runs(session: AsyncSession, *, limit: int = 3) -> dict[str, int]:
    now = datetime.now(UTC)
    rows = (
        await session.execute(
            select(SystemJobRun)
            .where(
                SystemJobRun.job_name == "system_jobs_tick",
                SystemJobRun.status == "retry",
                SystemJobRun.next_retry_at.is_not(None),
                SystemJobRun.next_retry_at <= now,
            )
            .order_by(SystemJobRun.next_retry_at.asc(), SystemJobRun.created_at.asc())
            .limit(limit)
        )
    ).scalars().all()

    retried = 0
    dead_lettered = 0
    for row in rows:
        result = await _execute_system_jobs_tick_run(session, row)
        retried += 1
        if not bool(result.get("ok")) and str(result.get("job_run", {}).get("status")) == "dead_letter":
            dead_lettered += 1
    return {"retried": retried, "dead_lettered": dead_lettered}


async def _enqueue_system_jobs_tick_run(trigger_source: str) -> str:
    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        job_run = SystemJobRun(
            job_name="system_jobs_tick",
            trigger_source=trigger_source,
            status="queued",
            attempts=0,
            max_attempts=_SYSTEM_JOBS_TICK_MAX_ATTEMPTS,
            payload_json={"requested_at": datetime.now(UTC).isoformat()},
        )
        session.add(job_run)
        await session.flush()
        job_run_id = str(job_run.id)
        await session.commit()
        return job_run_id


async def _process_system_jobs_tick_queue(job_run_id: str) -> None:
    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        pending_summary = await _run_pending_system_jobs_tick_runs(session)
        job_run = await session.get(SystemJobRun, job_run_id)
        if job_run is None:
            return
        if job_run.status == "queued":
            result = await _execute_system_jobs_tick_run(session, job_run)
            if pending_summary and isinstance(result.get("result"), dict):
                result["result"]["retry_queue"] = pending_summary


def _enforce_cron_secret(request: Request) -> None:
    """Fail closed: jobs tick requires CRON_SECRET unless ALLOW_INSECURE_CRON is explicitly enabled."""
    settings = get_settings()
    if settings.cron_secret:
        provided_secret = request.headers.get("X-Cron-Secret")
        if provided_secret != settings.cron_secret:
            raise HTTPException(status_code=403, detail="Invalid or missing cron secret")
        return
    if settings.allow_insecure_cron and settings.environment == "development":
        return
    raise HTTPException(status_code=403, detail="Cron secret is not configured; jobs tick is disabled")


@router.post("/jobs/tick/async", status_code=202)
async def jobs_tick_async(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Async job tick: enqueues all jobs as a background task and returns immediately.
    Use this for normal scheduled runs (e.g., cron every 5 min).
    Requires CRON_SECRET (X-Cron-Secret header) outside development.
    """
    _enforce_cron_secret(request)

    job_run_id = await _enqueue_system_jobs_tick_run(trigger_source="api")
    background_tasks.add_task(_process_system_jobs_tick_queue, job_run_id)
    return {
        "status": "queued",
        "message": "All jobs are running in the background",
        "job_run_id": job_run_id,
        "max_attempts": _SYSTEM_JOBS_TICK_MAX_ATTEMPTS,
    }


@router.post("/jobs/tick")
async def jobs_tick(request: Request, session: DbSession):
    """
    Synchronous job tick: runs all jobs in the request path.
    Use only for manual emergency triggers (ops console).
    Prefer /jobs/tick/async for scheduling.
    Requires CRON_SECRET (X-Cron-Secret header) outside development.
    """
    _enforce_cron_secret(request)
    return await _run_all_jobs(session)
