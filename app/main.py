"""ANCAP Core API - AI-Native Capital Allocation Platform."""
import logging
import time
from uuid import uuid4
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.services.logging import configure_logging, get_logger
from app.services.observability import record_http_request
from app.api.routers import (
    auth,
    users,
    agents,
    keys,
    verticals,
    strategies,
    strategy_versions,
    listings,
    orders,
    access,
    pools,
    ledger,
    runs,
    metrics,
    evaluations,
    reputation,
    moderation,
    risk,
    reviews,
    funds,
    onboarding,
    stakes_router,
    chain,
    wallet_acp,
    mobile_acp,
    mobile_devices,
    exchange_office,
    assay_gc,
    numismatic_auth,
    ownership_proofs,
    bridge_rail,
    wacp_liquidity_ops,
    wacp_public,
    sacp_public,
    market_data,
    weather,
    system,
    flows,
    contracts,
    contract_milestones,
    onboarding_growth,
    referrals,
    social,
    public,
    notifications,
    tasks,
    workflow_store,
    workflow_ops,
    paid_api,
    leaderboards,
    growth_dashboard,
    platform_admin,
    governance,
    settlements,
    evolution,
    autonomy,
    search,
    audit,
    organizations,
    org_identity,
    digital_passport,
    dna_rna_bank,
    perimeter_cleanup,
    payments,
    payouts,
    creators,
    subscriptions,
    webhooks,
    social_profiles,
    merchant,
    acp_explorer,
    claim_codes,
    payment_scanner,
    commerce,
    token_snapshot,
    treasury,
    securities,
    watch_fleet,
    orbital_edge,
    aeterna,
    lunar_land,
    mail_accounts,
    embodied_ai,
    crypto_benchmark,
    space_auction,
    animal_auction,
    flora_auction,
    insurance,
    arena,
    exponential_growth,
    tech_auction,
    cryo_desk,
    humanitarian,
    counsel,
    starlink_install,
    field_services,
    literary_auction,
    quantum_sim,
    saliva_rx,
    social_network,
    dating,
    startup_invest,
    stardust_srt,
    robot_ops,
)

settings = get_settings()
configure_logging()
logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from contextlib import suppress
    from app.services.workflow_ops import workflow_ops_tick, WORKER_HEALTH

    async def workflow_worker():
        while True:
            try:
                summary = await workflow_ops_tick(max_items=2)
                delay = 1 if summary["processed"] else 15
            except Exception as exc:
                WORKER_HEALTH["last_error_type"] = type(exc).__name__
                logger.warning("workflow_operations_retry", error_type=type(exc).__name__)
                delay = 15
            await asyncio.sleep(delay)

    workflow_task = asyncio.create_task(workflow_worker()) if get_settings().workflow_operations_worker_enabled else None
    try:
        from app.api.routers.wallet_acp import _schedule_chain_scan_warm

        _schedule_chain_scan_warm()
    except Exception:
        logger.exception("Failed to schedule ACP chain-scan warm on startup")
    try:
        from app.services.acp_utxo_index import schedule_utxo_index_catchup

        schedule_utxo_index_catchup()
    except Exception:
        logger.exception("Failed to schedule ACP UTXO index catch-up on startup")
    try:
        yield
    finally:
        if workflow_task:
            workflow_task.cancel()
            with suppress(asyncio.CancelledError):
                await workflow_task


app = FastAPI(
    title="ANCAP Core API",
    version="0.1.0",
    description="AI-Native Capital Allocation Platform - Core Engine",
    lifespan=lifespan,
    # Public OpenAPI/Swagger: site links and BscScan/dev expect
    # https://ancap.cloud/api/docs (nginx strips /api → FastAPI /docs).
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Idempotency-Key",
        "X-API-Key",
        "X-Bridge-Operator-Secret",
        "X-Cron-Secret",
        "X-Requested-With",
        "X-Request-Id",
    ],
)


@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    started = time.perf_counter()
    status_code = 500
    user_id = getattr(request.state, "user_id", None)
    agent_id = getattr(request.state, "agent_id", None)
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["x-request-id"] = request_id
        return response
    finally:
        duration_ms = int((time.perf_counter() - started) * 1000)
        record_http_request(request.method, request.url.path, status_code)
        logger.info(
            "http_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=str(user_id) if user_id else None,
            agent_id=str(agent_id) if agent_id else None,
        )


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add hardening security headers to every response.

    - X-Frame-Options: DENY — prevents clickjacking (was SAMEORIGIN)
    - X-Content-Type-Options: nosniff — prevents MIME sniffing
    - Referrer-Policy: strict-origin-when-cross-origin — controls referrer leakage
    - Permissions-Policy: disable unneeded browser features
    - Strict-Transport-Security: enforced in production (also set at reverse-proxy level)
    """
    response: Response = await call_next(request)
    # Skip health probes — no browser-facing headers needed there
    path = request.url.path
    if not path.startswith("/health") and not path.startswith("/ready"):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )
        if settings.environment == "production":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
    return response


ALL_ROUTERS = [
    auth.router,
    users.router,
    agents.router,
    keys.router,
    verticals.router,
    strategies.router,
    strategy_versions.router,
    listings.router,
    orders.router,
    access.router,
    pools.router,
    ledger.router,
    runs.router,
    contracts.router,
    contract_milestones.router,
    onboarding_growth.router,
    referrals.router,
    social.router,
    public.router,
    notifications.router,
    tasks.router,
    workflow_store.router,
    workflow_ops.router,
    paid_api.router,
    leaderboards.router,
    growth_dashboard.router,
    platform_admin.router,
    metrics.router,
    evaluations.router,
    reputation.router,
    moderation.router,
    risk.router,
    reviews.router,
    reviews.disputes_router,
    funds.router,
    onboarding.router,
    stakes_router.router,
    chain.router,
    wallet_acp.router,
    mobile_acp.router,
    mobile_devices.router,
    exchange_office.router,
    assay_gc.router,
    numismatic_auth.router,
    ownership_proofs.router,
    bridge_rail.router,
    wacp_liquidity_ops.router,
    wacp_public.router,
    sacp_public.router,
    market_data.router,
    weather.router,
    system.router,
    system._internal_router,
    flows.router,
    governance.router,
    governance.moderation_cases_router,
    settlements.router,
    evolution.router,
    evolution.tournaments_router,
    evolution.bounties_router,
    autonomy.router,
    search.router,
    audit.router,
    organizations.router,
    org_identity.router,
    digital_passport.router,
    dna_rna_bank.router,
    perimeter_cleanup.router,
    payments.router,
    payouts.router,
    creators.router,
    subscriptions.router,
    webhooks.router,
    social_profiles.router,
    merchant.pay_router,
    merchant.merchant_router,
    acp_explorer.router,
    claim_codes.router,
    payment_scanner.router,
    commerce.router,
    token_snapshot.router,
    treasury.router,
    securities.router,
    watch_fleet.router,
    orbital_edge.router,
    aeterna.router,
    lunar_land.router,
    mail_accounts.router,
    embodied_ai.router,
    crypto_benchmark.router,
    space_auction.router,
    animal_auction.router,
    flora_auction.router,
    # dark_matter_auction retired from public launch surface (routes unmounted).
    insurance.router,
    arena.router,
    exponential_growth.router,
    tech_auction.router,
    cryo_desk.router,
    humanitarian.router,
    counsel.router,
    starlink_install.router,
    field_services.router,
    literary_auction.router,
    quantum_sim.router,
    saliva_rx.router,
    social_network.router,
    dating.router,
    startup_invest.router,
    stardust_srt.router,
    robot_ops.router,
]

for r in ALL_ROUTERS:
    app.include_router(r, prefix="")
    # Backward-compatible API namespace expected by tests/legacy clients.
    app.include_router(r, prefix="/v1")


@app.get("/")
async def root():
    return {"service": "ANCAP Core API", "version": "0.1.0", "docs": "/docs"}


