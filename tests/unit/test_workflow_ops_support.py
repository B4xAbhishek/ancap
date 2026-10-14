from types import SimpleNamespace
from uuid import uuid4
import pytest
from cryptography.exceptions import InvalidTag
from fastapi import HTTPException
from pydantic import ValidationError
from app.schemas.workflow_ops import AutomationWrite, EnqueueRequest, ScheduleWrite
from app.services.workflow_ops_support import seal, unseal, quality_passport, bounded_json, spreadsheet_cell, digest


def test_credential_envelope_is_random_and_bound_to_owner():
    owner = str(uuid4())
    first = seal("test-only-credential", owner)
    assert first != seal("test-only-credential", owner)
    assert "test-only-credential" not in first
    assert unseal(first, owner) == "test-only-credential"
    with pytest.raises(InvalidTag):
        unseal(first, str(uuid4()))


def test_quality_never_claims_fact_verification_and_exposes_fallback():
    output = {"deliverable": {"summary": "Evidence needed"}}
    result = quality_passport(output, {"fallback_used": False, "model": "test"}, [], {"test_cases": [{"name": "Evidence", "required_text": ["evidence"]}]})
    assert result["passed"]
    assert result["output_hash"] == digest(output)
    assert "not_fact_verification" in result["scope"]
    assert not quality_passport(output, {"fallback_used": True}, [], {})["passed"]


@pytest.mark.parametrize("data", [float("nan"), "x"*200001], ids=["nonfinite", "oversized"])
def test_payload_limits_reject_nonfinite_and_oversized_data(data):
    with pytest.raises(HTTPException):
        bounded_json(data)


@pytest.mark.parametrize("value", ["=IMPORTXML('https://bad')", "+1+1", "@SUM(A1)", "\tformula"])
def test_spreadsheet_formula_escape(value):
    assert spreadsheet_cell(value).startswith("'")


def test_batch_and_schedule_limits_are_explicit():
    with pytest.raises(ValidationError):
        ScheduleWrite(interval_minutes=1, monthly_budget_acp=1)
    with pytest.raises(ValidationError):
        EnqueueRequest(idempotency_key="batch-test", max_cost_acp=1, kind="batch")
    with pytest.raises(ValidationError):
        EnqueueRequest(idempotency_key="batch-test", max_cost_acp=1, kind="batch", rows=[{}]*21)
    with pytest.raises(ValidationError):
        AutomationWrite(name="test", project_id=str(uuid4()), steps=[{"slug": "token-listing-pack"}]*6)


@pytest.mark.parametrize("kind", ["webhook", "telegram", "google_sheets", "hubspot"])
def test_delivery_payloads_are_signed_bounded_and_use_expected_destination(kind, monkeypatch):
    import asyncio
    import hashlib
    import hmac
    from app.services import workflow_ops_support as support
    owner = str(uuid4())
    secret = "synthetic-test-secret"
    config = {"url": "https://example.test/report", "chat_id": "12345", "spreadsheet_id": "test-sheet-1234567", "range": "Sheet1!A:D"}
    connection = SimpleNamespace(id=uuid4(), owner_user_id=owner, kind=kind, secret_box=seal(secret, owner), config_json=config)
    run = SimpleNamespace(id=uuid4())
    calls = []
    async def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(status_code=200, json=lambda: {"ok": True})
    monkeypatch.setattr(support, "post_public", fake_post)
    result = asyncio.run(support.deliver(connection, run, {"summary": "<script>example</script>"}))
    assert result["state"] == "delivered"
    assert secret not in str(result)
    assert len(calls) == 1
    url, request = calls[0]
    assert url.startswith("https://")
    if kind == "webhook":
        expected = "sha256=" + hmac.new(secret.encode(), request["content"], hashlib.sha256).hexdigest()
        assert request["headers"]["X-ANCAP-Signature"] == expected
        assert request["headers"]["Idempotency-Key"] == str(run.id)
    if kind == "hubspot":
        assert "<script>" not in request["payload"]["properties"]["hs_note_body"]
