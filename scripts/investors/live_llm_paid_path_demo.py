#!/usr/bin/env python3
"""Staging demo: paid workflow with live LLM (fallback_used=false).

Uses a disposable TEST_DATABASE_URL only. Test ACP ledger credits — no Stripe,
no chain broadcast, no production funds.

Evidence JSON written under tmp/investor-live-llm-<date>/.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from sqlalchemy.engine import make_url

REPO = Path(__file__).resolve().parents[2]
DEMO_DB = "ancap_investor_demo_20261014"
# Local docker-compose volume often keeps password auth from first init.
DEFAULT_TEST_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5432/{DEMO_DB}"


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except Exception:
        return "unknown"


def _prepare_env() -> dict[str, str]:
    env = os.environ.copy()
    # Disposable DB only — never default production DB name.
    test_url = env.get("TEST_DATABASE_URL") or DEFAULT_TEST_URL
    try:
        url = make_url(test_url)
    except Exception:
        raise SystemExit("Invalid TEST_DATABASE_URL; credentials are not logged.") from None
    if (url.drivername not in {"postgresql", "postgresql+asyncpg"}
        or url.host not in {"localhost", "127.0.0.1", "::1"}
        or not re.fullmatch(r"ancap_investor_demo_[0-9]{8}(?:_[a-z0-9_]+)?", url.database or "")):
        raise SystemExit("Refusing database: only a named local disposable investor-demo database is permitted.")
    env["TEST_DATABASE_URL"] = test_url
    env["DATABASE_URL"] = test_url
    # Live local Ollama — real model call, no template fallback.
    env["LLM_PROVIDER"] = env.get("LLM_PROVIDER") or "ollama"
    env["LLM_MODEL"] = env.get("LLM_MODEL") or "qwen2.5:3b"
    env["OLLAMA_BASE_URL"] = env.get("OLLAMA_BASE_URL") or "http://localhost:11434"
    env["LLM_FALLBACK_TO_TEMPLATE"] = "false"
    env["LLM_TIMEOUT_SECONDS"] = env.get("LLM_TIMEOUT_SECONDS") or "120"
    env["LLM_MAX_TOKENS"] = env.get("LLM_MAX_TOKENS") or "1200"
    # Platform fee proof (~10%).
    env["WORKFLOW_PLATFORM_FEE_PERCENT"] = env.get("WORKFLOW_PLATFORM_FEE_PERCENT") or "10"
    # Keep gates/open for demo user path.
    env["PARTICIPATION_GATES_ENABLED"] = "false"
    env["WELCOME_GRANT_ACP"] = "0"
    env["REGISTRATION_MAX_AGENTS_PER_DAY"] = "0"
    return env


def _acp_balance(client, headers: dict, user_id: str) -> Decimal:
    res = client.get(
        "/v1/ledger/balance",
        params={"owner_type": "user", "owner_id": user_id},
        headers=headers,
    )
    if res.status_code != 200:
        return Decimal("0")
    for item in res.json().get("balances") or []:
        if str(item.get("currency") or "").upper() == "ACP":
            return Decimal(str(item.get("amount") or "0"))
    return Decimal("0")


def main() -> int:
    env = _prepare_env()
    for key, value in env.items():
        os.environ[key] = value

    sys.path.insert(0, str(REPO))
    # Import conftest after env so it pins DATABASE_URL to the disposable DB.
    import tests.conftest as conftest

    from app.config import get_settings

    get_settings.cache_clear()
    sync_url = conftest._sync_database_url()
    conftest._run_migrations_or_create_all(sync_url)

    from starlette.testclient import TestClient
    from app.main import app
    from app.db.session import get_db, async_session_maker

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

    sha = _git_sha()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = REPO / "tmp" / f"investor-live-llm-{stamp}-{uuid4().hex[:8]}"
    out_dir.mkdir(parents=True, exist_ok=False)

    settings = get_settings()
    evidence: dict = {
        "started_at": stamp,
        "git_sha": sha,
        "environment": "disposable_test_db",
        "database": make_url(env["TEST_DATABASE_URL"]).database,
        "source_sha256": {
            str(path.relative_to(REPO)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted([*REPO.glob("app/**/*.py"), REPO / "tests/conftest.py", Path(__file__).resolve()])
        },
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "llm_fallback_to_template": settings.llm_fallback_to_template,
        "workflow_platform_fee_percent": str(
            getattr(settings, "workflow_platform_fee_percent", "10")
        ),
        "funds": "test_ledger_credits_only",
        "stripe": False,
        "chain_broadcast": False,
    }

    try:
        with TestClient(app, base_url="http://test") as client:
            email = f"investor_live_{uuid4().hex[:10]}@test.com"
            reg = client.post(
                "/v1/auth/users",
                json={
                    "email": email,
                    "password": "password123",
                    "display_name": "investor live llm",
                },
                headers={"Authorization": ""},
            )
            assert reg.status_code in (200, 201), reg.text
            token = reg.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            user = client.get("/v1/users/me", headers=headers).json()
            user_id = user["id"]

            before_amount = _acp_balance(client, headers, user_id)

            deposit = client.post(
                "/v1/ledger/deposit",
                json={
                    "account_owner_type": "user",
                    "account_owner_id": user_id,
                    "amount": {"amount": "50", "currency": "ACP"},
                    "reference": "investor-live-llm-demo",
                },
                headers=headers,
            )
            assert deposit.status_code == 201, deposit.text
            after_deposit = _acp_balance(client, headers, user_id)

            run = client.post(
                "/v1/workflow-store/runs",
                json={
                    "workflow_slug": "token-risk-report",
                    "payment_currency": "ACP",
                    "unlock_full_result": True,
                    "inputs": {
                        "project_name": "Investor Live LLM Token",
                        "token_symbol": "ILLM",
                        "chain": "Base",
                    },
                },
                headers=headers,
            )
            assert run.status_code == 201, run.text
            run_payload = run.json()
            run_id = run_payload["id"]
            price = Decimal(str(run_payload["price"]["amount"]))
            assert price > 0

            pay = client.post(
                f"/v1/workflow-store/runs/{run_id}/payment-intents",
                json={"payment_method": "credits", "note": "investor live llm demo"},
                headers=headers,
            )
            assert pay.status_code == 201, pay.text
            assert pay.json()["run"]["status"] == "paid"

            execute = client.post(
                f"/v1/workflow-store/runs/{run_id}/execute",
                headers=headers,
                timeout=180.0,
            )
            assert execute.status_code == 200, execute.text
            executed = execute.json()["item"]
            assert executed["status"] == "completed", executed

            receipt = executed.get("receipt") or {}
            proof = receipt.get("proof") or {}
            result = executed.get("result") or {}
            llm_usage = proof.get("llm_usage") or result.get("llm_usage") or {}
            summary = result.get("execution_summary") or {}

            fallback_used = llm_usage.get("fallback_used") is not False

            fee = proof.get("platform_fee") or proof.get("margin_snapshot")
            fee_amount = Decimal("0")
            if isinstance(fee, dict):
                fee_amount = Decimal(
                    str(fee.get("amount") or fee.get("platform_fee_amount") or 0)
                )

            after_pay = _acp_balance(client, headers, user_id)

            evidence.update(
                {
                    "email": email,
                    "user_id": user_id,
                    "run_id": run_id,
                    "price_acp": str(price),
                    "balance_before_deposit": str(before_amount),
                    "balance_after_deposit": str(after_deposit),
                    "balance_after_pay": str(after_pay),
                    "credits_moved": str(after_deposit - after_pay),
                    "payment_intent_status": proof.get("payment_intent_status"),
                    "payment_intent_id": proof.get("payment_intent_id"),
                    "platform_fee": fee,
                    "platform_fee_amount": str(fee_amount),
                    "llm_usage": llm_usage,
                    "execution_summary": summary,
                    "fallback_used": fallback_used,
                    "artifact_keys": sorted(result.keys()) if isinstance(result, dict) else [],
                    "artifact_preview": {
                        "status": result.get("status"),
                        "workflow_slug": result.get("workflow_slug"),
                        "deliverable_type": type(result.get("deliverable")).__name__,
                        "summary_mode": summary.get("mode") if isinstance(summary, dict) else None,
                    },
                    "receipt_proof_keys": sorted(proof.keys()) if isinstance(proof, dict) else [],
                }
            )

            (out_dir / "artifact.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            (out_dir / "receipt.json").write_text(
                json.dumps(receipt, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

            ok = (
                not fallback_used
                and llm_usage.get("status") == "succeeded"
                and bool(result)
                and proof.get("payment_intent_status") == "captured"
                and fee_amount > 0
                and after_deposit - before_amount == Decimal("50")
                and after_deposit - after_pay == price
            )
            evidence["ok"] = ok
            evidence["checks"] = {
                "fallback_used_false": not fallback_used,
                "llm_succeeded": llm_usage.get("status") == "succeeded",
                "artifact_present": bool(result),
                "receipt_captured": proof.get("payment_intent_status") == "captured",
                "platform_fee_positive": fee_amount > 0,
                "deposit_exact": after_deposit - before_amount == Decimal("50"),
                "credits_match_price": after_deposit - after_pay == price,
            }
    finally:
        app.dependency_overrides.clear()

    (out_dir / "EVIDENCE.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (out_dir / "GIT_SHA.txt").write_text(sha + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": evidence.get("ok"),
                "path": str(out_dir),
                "sha": sha,
                "checks": evidence.get("checks"),
                "llm_usage": evidence.get("llm_usage"),
            },
            indent=2,
            default=str,
        )
    )
    return 0 if evidence.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
