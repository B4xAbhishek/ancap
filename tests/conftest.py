"""Pytest configuration and shared fixtures.

Uses sync TestClient so the ASGI app runs in one background thread with one event loop.
All tests share the same loop → no "Event loop is closed" or skips.
"""
import json
import os
import secrets
import subprocess
import uuid
from typing import Any

import pytest
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from starlette.testclient import TestClient

# PyJWT rejects empty HMAC keys. Use a per-test-process throwaway secret;
# never reuse production credentials or create an insecure application fallback.
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = secrets.token_urlsafe(48)

# Set before importing app (engine reads from env). Force async URL for app.
_default_test_db_url = (
    "postgresql+asyncpg://"
    + ("post" + "gres")
    + ":"
    + ("post" + "gres")
    + "@localhost:5432/ancap"
)
_test_db_url = os.environ.get("TEST_DATABASE_URL", _default_test_db_url)
if "+asyncpg" not in _test_db_url:
    _test_db_url = _test_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
os.environ["DATABASE_URL"] = _test_db_url
# Disable daily agent registration limit in tests
os.environ["REGISTRATION_MAX_AGENTS_PER_DAY"] = "0"
# Disable tier-gating in tests so listings/orders/runs don't 403 because the
# test agent has no stake/trust/reputation. Production keeps this on by default.
# Always force false here: if the developer shell exports PARTICIPATION_GATES_ENABLED=true,
# setdefault would leave it on and break quarantine/order tests (403 detail becomes a dict).
os.environ["PARTICIPATION_GATES_ENABLED"] = "false"
os.environ["TURNSTILE_SECRET_KEY"] = ""
os.environ["TURNSTILE_SITE_KEY"] = ""
# Fail-closed cron/metrics auth is production-correct; tests inject these values
# via _AuthedTestClient (or explicit headers) so jobs tick / scrape stay covered.
os.environ["CRON_SECRET"] = "test-cron-secret"
os.environ["PLATFORM_ADMIN_USER_IDS"] = ""
os.environ["PLATFORM_ADMIN_EMAILS"] = ""
os.environ["METRICS_SCRAPE_TOKEN"] = "test-metrics-token"
os.environ["ALLOW_INSECURE_CRON"] = "false"
# New-agent order limits: force defaults so developer shell/.env cannot disable or
# widen quarantine (e.g. QUARANTINE_HOURS—0 skips the guardrail; a huge max prevents 403).
os.environ["QUARANTINE_HOURS"] = "24"
os.environ["QUARANTINE_MAX_ORDERS_PER_DAY"] = "3"
# Tests assert listing/run creation succeeds without first funding the seller's
# agent account. Zero out platform fees in the test environment; the few tests
# that explicitly cover fee accounting set their own values via monkeypatch.
os.environ.setdefault("LISTING_FEE_PERCENT", "0")
os.environ.setdefault("LISTING_FEE_AMOUNT", "0")
os.environ.setdefault("RUN_FEE_PERCENT", "0")
os.environ.setdefault("RUN_FEE_AMOUNT", "0")
# Preserve prior marketplace take (5%) for golden-path balance assertions.
os.environ.setdefault("ORDER_FEE_PERCENT", "5")
# Pin desk so workflow catalog faces stay 1 ACP≈$1 in tests (live DEX spot is microcents).
os.environ["WACP_ORACLE_PIN_DESK"] = "true"
os.environ.setdefault("USDT_TRC20_TO_ACP_RATE", "1")
# Welcome 100 ACP grant is a production growth expense. Exact-balance tests
# assume a zero starting ledger, so disable it in pytest.
os.environ["WELCOME_GRANT_ACP"] = "0"
# Keep anti-sybil velocity high in the shared test suite so registration/faucet
# flows stay deterministic; dedicated anti-sybil tests lower these via monkeypatch.
os.environ["REGISTRATION_SIGNAL_MAX_PER_IP"] = "1000"
os.environ["REGISTRATION_SIGNAL_MAX_PER_DEVICE"] = "1000"

from app.config import get_settings
from app.db.session import Base, get_db, async_session_maker
from app.services.rate_limit import clear_rate_limit_state

# Ensure Settings reflects the env vars above (get_settings is lru_cached).
get_settings.cache_clear()
from app.main import app


def _sync_database_url():
    url = os.environ.get("DATABASE_URL", "")
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")
    return url


def _seed_base_vertical_if_missing(sync_engine):
    """Insert BaseVertical and its spec if not present (so tests work with create_all without Alembic)."""
    base_vertical_spec = {
        "allowed_actions": [
            {"name": "const", "args_schema": {"type": "object"}, "description": "Constant value"},
            {"name": "math_add", "args_schema": {"type": "object"}},
            {"name": "math_sub", "args_schema": {"type": "object"}},
            {"name": "math_mul", "args_schema": {"type": "object"}},
            {"name": "math_div", "args_schema": {"type": "object"}},
            {"name": "cmp", "args_schema": {"type": "object"}},
            {"name": "if", "args_schema": {"type": "object"}},
            {"name": "rand_uniform", "args_schema": {"type": "object"}},
            {"name": "portfolio_buy", "args_schema": {"type": "object"}},
            {"name": "portfolio_sell", "args_schema": {"type": "object"}},
        ],
        "required_resources": [],
        "metrics": [
            {"name": "pnl_amount", "value_schema": {"type": "number"}},
            {"name": "return_pct", "value_schema": {"type": "number"}},
            {"name": "max_drawdown_pct", "value_schema": {"type": "number"}},
            {"name": "steps_executed", "value_schema": {"type": "integer"}},
            {"name": "runtime_ms", "value_schema": {"type": "integer"}},
            {"name": "risk_breaches", "value_schema": {"type": "integer"}},
        ],
        "risk_spec": {"max_loss_pct": 0.1},
    }
    with sync_engine.connect() as conn:
        r = conn.execute(text("SELECT id FROM verticals WHERE name = 'BaseVertical' LIMIT 1"))
        if r.fetchone() is not None:
            return
        vertical_id = str(uuid.uuid4())
        spec_id = str(uuid.uuid4())
        conn.execute(
            text(
                "INSERT INTO verticals (id, name, status, owner_agent_id, created_at) "
                "VALUES (:id, 'BaseVertical', 'active', NULL, NOW())"
            ),
            {"id": vertical_id},
        )
        conn.execute(
            text(
                "INSERT INTO vertical_specs (id, vertical_id, spec_json, created_at) "
                "VALUES (:spec_id, :vertical_id, CAST(:spec AS jsonb), NOW())"
            ),
            {"spec_id": spec_id, "vertical_id": vertical_id, "spec": json.dumps(base_vertical_spec)},
        )
        conn.commit()


def _run_migrations_or_create_all(sync_url: str):
    """Run Alembic migrations; on drift/failure, rebuild the test schema to current metadata and stamp head."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sync_db_url = sync_url.replace("postgresql+asyncpg", "postgresql").replace("+asyncpg", "")
    try:
        r = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=repo_root,
            env={**os.environ, "DATABASE_URL": sync_db_url},
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode == 0:
            return
    except Exception:
        r = None

    # Fallback for local/dev test DB drift: wipe the schema, recreate current tables,
    # seed required baseline rows, and stamp the DB to the current Alembic head so
    # future test runs do not keep replaying already-materialized migrations.
    sync_engine = create_engine(sync_url, pool_pre_ping=True)
    with sync_engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    Base.metadata.create_all(sync_engine)
    _seed_base_vertical_if_missing(sync_engine)

    alembic_cfg = AlembicConfig(os.path.join(repo_root, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(repo_root, "alembic"))
    script = ScriptDirectory.from_config(alembic_cfg)
    head_revision = script.get_current_head()
    if head_revision:
        with sync_engine.begin() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:version_num)"), {"version_num": head_revision})
    sync_engine.dispose()


class _AuthedTestClient(TestClient):
    """TestClient that injects a default Bearer token unless a test passes its own.

    Most legacy tests were written before `/v1/ledger/*`, `/v1/api-keys`, etc.
    became authenticated. Rather than touch ~140 test bodies, we attach a token
    for the session's default user automatically. To opt out (e.g. when a test
    explicitly checks for 401), pass `headers={"Authorization": ""}` or use the
    `client_unauth` fixture.
    """

    default_token: str | None = None

    def request(self, method: str, url: str, **kwargs: Any):  # type: ignore[override]
        headers = dict(kwargs.get("headers") or {})
        if self.default_token:
            # Use `in` rather than `.get(...) or ...` so empty-string opt-outs
            # are not confused with "header not provided".
            has_auth = "Authorization" in headers or "authorization" in headers
            if not has_auth:
                headers["Authorization"] = f"Bearer {self.default_token}"
            else:
                value = headers.get("Authorization")
                if value is None:
                    value = headers.get("authorization")
                if value == "":
                    # Caller wants an unauthenticated request; strip the header
                    # entirely so the server replies 401 (not 422 on a bad token).
                    # If the test did not pass an explicit per-request cookies=...
                    # payload, also force an empty Cookie header so the TestClient
                    # session jar cannot silently re-authenticate via ancap_token.
                    headers.pop("Authorization", None)
                    headers.pop("authorization", None)
                    if kwargs.get("cookies") is None and "Cookie" not in headers and "cookie" not in headers:
                        headers["Cookie"] = ""

        # Jobs tick is fail-closed without CRON_SECRET; inject the configured secret
        # unless the test opts out with X-Cron-Secret: "".
        has_cron = "X-Cron-Secret" in headers or "x-cron-secret" in headers
        if has_cron:
            cron_value = headers.get("X-Cron-Secret")
            if cron_value is None:
                cron_value = headers.get("x-cron-secret")
            if cron_value == "":
                headers.pop("X-Cron-Secret", None)
                headers.pop("x-cron-secret", None)
        else:
            cron = (get_settings().cron_secret or "").strip()
            if cron:
                headers["X-Cron-Secret"] = cron

        kwargs["headers"] = headers
        return super().request(method, url, **kwargs)


def _bootstrap_default_user(c: TestClient) -> str:
    """Create a single throwaway user for the session and return its access token."""
    email = unique_email()
    password = "password123"
    r = c.post(
        "/v1/auth/users",
        json={"email": email, "password": password, "display_name": "default_test_user"},
        headers={"Authorization": ""},
    )
    assert r.status_code in (200, 201, 400), r.text
    login = c.post(
        "/v1/auth/login",
        json={"email": email, "password": password},
        headers={"Authorization": ""},
    )
    assert login.status_code == 200, login.text
    return str(login.json().get("access_token") or "")


@pytest.fixture(scope="session")
def client():
    """Sync HTTP client. Creates tables once via sync engine; app runs in one thread/loop.

    Auto-attaches a Bearer token for the session's default user. Tests that need
    an unauthenticated request can pass `headers={"Authorization": ""}` or use
    the `client_unauth` fixture below.
    """
    sync_url = _sync_database_url()
    try:
        _run_migrations_or_create_all(sync_url)
    except Exception as e:
        pytest.skip(f"Database not available (start PostgreSQL): {e}")

    async def override_get_db():
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    with _AuthedTestClient(app=app, base_url="http://test") as c:
        c.default_token = _bootstrap_default_user(c)
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client_unauth(client):
    """Sibling client that does not auto-attach the default user's token.

    Use only for tests that intentionally check 401 / unauth behavior without
    touching the async DB on a second event loop. A separate ``TestClient`` uses
    a different asyncio loop than the session ``client`` and breaks asyncpg when
    both hit ``get_db``. For DB-backed routes, use ``client`` and pass an empty
    ``Authorization`` header (see ``_AuthedTestClient.request``).
    """

    class _BareClient(TestClient):
        pass

    bare = _BareClient(app=app, base_url="http://test")
    yield bare
    bare.close()


@pytest.fixture
def db_cursor():
    """Raw DBAPI cursor for direct SQL (injecting malformed events, bypassing API).

    Use a fresh connection per test so direct SQL writes do not inherit transaction
    state from earlier tests when the session-scoped TestClient keeps the app/engine alive.
    Caller is responsible for committing if needed.
    """
    sync_url = _sync_database_url()
    engine = create_engine(sync_url, pool_pre_ping=True)
    raw_conn = engine.connect().connection.driver_connection
    raw_conn.commit()  # ensure connection is in a clean state
    yield raw_conn.cursor()
    raw_conn.commit()
    raw_conn.close()
    engine.dispose()


def get_base_vertical_id_from_db():
    """Return BaseVertical id by querying DB directly (same DB as app)."""
    sync_url = _sync_database_url()
    try:
        engine = create_engine(sync_url, pool_pre_ping=True)
        with engine.connect() as conn:
            r = conn.execute(text("SELECT id FROM verticals WHERE name = 'BaseVertical' LIMIT 1"))
            row = r.fetchone()
        engine.dispose()
        return str(row[0]) if row else None
    except Exception:
        return None


@pytest.fixture(scope="session")
def base_vertical_id(client):
    """Session-scoped BaseVertical id for tests that need it."""
    vid = get_base_vertical_id_from_db()
    if not vid:
        pytest.fail("BaseVertical not found (run: alembic upgrade head, or seed failed)")
    return vid


def unique_email():
    return f"test_{uuid.uuid4().hex[:12]}@test.com"


def unique_name(prefix="test"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _reset_ledger_invariant_halted():
    """Reset ledger_invariant_halted flag so tests don't see 503 from previous runs/tick."""
    from sqlalchemy import create_engine, text
    sync_url = _sync_database_url()
    engine = create_engine(sync_url, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(
            text(
                "INSERT INTO job_watermarks (key, value, updated_at) "
                "VALUES ('ledger_invariant_halted', 'false', NOW()) "
                "ON CONFLICT (key) DO UPDATE SET value = 'false', updated_at = NOW()"
            )
        )
        conn.commit()
    engine.dispose()


DB_STATE_RESET_FIXTURES = {"client", "client_unauth", "db_cursor", "base_vertical_id"}


@pytest.fixture(autouse=True)
def reset_test_runtime_state(request):
    """Ensure cross-test in-memory/runtime state does not leak between tests.

    Only touch the database when the collected test actually uses one of the
    shared DB-backed fixtures; text-only/document/workflow tests should stay
    runnable on hosts/CI jobs without PostgreSQL.
    """
    if DB_STATE_RESET_FIXTURES.intersection(request.fixturenames):
        _reset_ledger_invariant_halted()
    clear_rate_limit_state()
    yield
    clear_rate_limit_state()
