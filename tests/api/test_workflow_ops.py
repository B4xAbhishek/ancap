from uuid import uuid4
from decimal import Decimal
from app.config import get_settings
from app.services.llm import LlmExecutionResult


def register(client):
    result = client.post("/v1/auth/users", json={"email": f"ops-{uuid4().hex}@test.com", "password": "test-pass-12345", "display_name": "Operations test"}, headers={"Authorization": ""})
    assert result.status_code == 201, result.text
    headers = {"Authorization": "Bearer "+result.json()["access_token"]}
    return client.get("/v1/users/me", headers=headers).json(), headers


def create(client, headers):
    project = client.post("/v1/workflow-ops/projects", json={"name": "Test team", "context": "Brand context"}, headers=headers)
    assert project.status_code == 201, project.text
    definition = {"name": "Listing report", "project_id": project.json()["id"], "steps": [{"slug": "token-listing-pack"}], "require_review": True, "test_cases": [{"name": "Brand", "required_text": ["context"]}]}
    result = client.post("/v1/workflow-ops/automations", json=definition, headers=headers)
    assert result.status_code == 201, result.text
    return project.json(), result.json(), definition


def publish(client, headers, automation, version=1):
    response = client.post(f"/v1/workflow-ops/automations/{automation['id']}/publish", json={"version": version}, headers=headers)
    assert response.status_code == 200, response.text


def test_paid_queue_review_receipt_and_idempotency(client, monkeypatch):
    from app.services import workflow_ops
    user, headers = register(client)
    deposit = client.post("/v1/ledger/deposit", json={"account_owner_type": "user", "account_owner_id": user["id"], "amount": {"amount": "100", "currency": "ACP"}, "reference": "workflow-ops-test"}, headers=headers)
    assert deposit.status_code == 201, deposit.text
    project, automation, definition = create(client, headers)
    publish(client, headers, automation)
    body = {"idempotency_key": "manual-test-one", "max_cost_acp": "100", "inputs": {"project_name": "Queue test"}}
    response = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json=body, headers=headers)
    assert response.status_code == 202, response.text
    op_id = response.json()["id"]
    again = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json=body, headers=headers)
    assert again.json()["id"] == op_id
    changed = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={**body, "inputs": {"changed": True}}, headers=headers)
    assert changed.status_code == 409
    async def execute(*args, **kwargs):
        assert kwargs["inputs"]["project_context"]["text"] == "Brand context"
        return LlmExecutionResult({"deliverable": {"summary": "Context report"}}, None, "test", "test-model", "succeeded", False)
    monkeypatch.setattr(workflow_ops, "execute_paid_workflow_with_llm", execute)
    monkeypatch.setenv("PLATFORM_ADMIN_USER_IDS", user["id"])
    get_settings.cache_clear()
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    op = client.get(f"/v1/workflow-ops/runs/{op_id}", headers=headers).json()
    assert op["state"] == "awaiting_review", op
    assert Decimal(op["cost_acp"]) > 0
    assert op["progress"]["items"][0]["quality"]["passed"]
    base_id = op["progress"]["items"][0]["run_id"]
    receipt = client.get(f"/v1/workflow-store/runs/{base_id}", headers=headers)
    assert receipt.status_code == 200
    review = client.post(f"/v1/workflow-ops/runs/{op_id}/review", json={"decision": "approve", "edited_output": {"summary": "Human-reviewed"}}, headers=headers)
    assert review.status_code == 200, review.text
    assert review.json()["progress"]["reviewed_output_hash"]
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert client.get(f"/v1/workflow-ops/runs/{op_id}", headers=headers).json()["state"] == "completed"
    metrics = client.get("/v1/workflow-ops/admin/economics", headers=headers).json()
    assert metrics["cash_revenue_eur"] is None
    assert metrics["paid_operations"] >= 1
    assert client.delete(f"/v1/workflow-ops/projects/{project['id']}", headers=headers).status_code == 200
    assert client.get(f"/v1/workflow-ops/runs/{op_id}", headers=headers).json()["state"] == "expired"
    get_settings.cache_clear()


def test_owner_isolation_publish_rollback_limits_and_cancel(client):
    _, headers = register(client)
    _, other = register(client)
    project, automation, definition = create(client, headers)
    assert client.put(f"/v1/workflow-ops/projects/{project['id']}", json={"name": "Stolen"}, headers=other).status_code == 404
    assert client.post(f"/v1/workflow-ops/automations/{automation['id']}/publish", json={"version": 1}, headers=other).status_code == 404
    updated = client.post(f"/v1/workflow-ops/automations/{automation['id']}/versions", json={**definition, "name": "Version two"}, headers=headers)
    assert updated.status_code == 201
    publish(client, headers, automation, 2)
    publish(client, headers, automation, 1)
    assert client.put(f"/v1/workflow-ops/automations/{automation['id']}/schedule", json={"enabled": True, "interval_minutes": 1, "monthly_budget_acp": "100"}, headers=headers).status_code == 422
    insufficient = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "too-low-test", "max_cost_acp": "0.001"}, headers=headers)
    assert insufficient.status_code == 409
    run = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "cancel-test", "max_cost_acp": "100"}, headers=headers).json()
    assert client.get(f"/v1/workflow-ops/runs/{run['id']}", headers=other).status_code == 404
    assert client.post(f"/v1/workflow-ops/runs/{run['id']}/cancel", headers=headers).json()["state"] == "cancelled"
    invalid = client.post("/v1/workflow-ops/automations", json={**definition, "steps": [{"slug": "invented"}]}, headers=headers)
    assert invalid.status_code == 422


def test_connections_no_secret_echo_and_ssrf_denied(client):
    _, headers = register(client)
    _, other = register(client)
    response = client.post("/v1/workflow-ops/connections", json={"name": "Model key", "kind": "anthropic", "secret": "test-only-provider-credential", "config": {"model": "test-model"}}, headers=headers)
    assert response.status_code == 201, response.text
    assert "test-only-provider-credential" not in response.text
    assert "secret_box" not in response.text
    assert client.delete(f"/v1/workflow-ops/connections/{response.json()['id']}", headers=other).status_code == 404
    blocked = client.post("/v1/workflow-ops/connections", json={"name": "Unsafe", "kind": "webhook", "config": {"url": "http://127.0.0.1:5432/"}}, headers=headers)
    assert blocked.status_code == 422
    blocked_tls = client.post("/v1/workflow-ops/connections", json={"name": "Unsafe TLS", "kind": "webhook", "config": {"url": "https://127.0.0.1/"}}, headers=headers)
    assert blocked_tls.status_code == 422


def test_trial_once_nontransferable_and_degraded_visible(client, monkeypatch):
    from app.services import workflow_ops
    _, headers = register(client)
    calls = []
    async def execute(*args, **kwargs):
        calls.append(True)
        return LlmExecutionResult({"deliverable": {"summary": "Template only"}}, None, "disabled", "none", "degraded", True)
    monkeypatch.setattr(workflow_ops, "execute_paid_workflow_with_llm", execute)
    body = {"project_name": "Trial Project", "description": "This is our test project description"}
    first = client.post("/v1/workflow-ops/trial", json=body, headers=headers)
    assert first.status_code == 200, first.text
    assert first.json()["state"] == "degraded"
    assert first.json()["progress"]["voucher"]["transferable"] is False
    assert Decimal(first.json()["cost_acp"]) == 0
    again = client.post("/v1/workflow-ops/trial", json=body, headers=headers)
    assert again.json()["id"] == first.json()["id"]
    assert len(calls) == 1


def test_unauthenticated_and_admin_gates(client):
    assert client.get("/v1/workflow-ops", headers={"Authorization": ""}).status_code == 401
    assert client.get("/v1/workflow-ops/admin/economics", headers={"Authorization": ""}).status_code == 401
    _, headers = register(client)
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code in (403, 503)


def funded_setup(client, monkeypatch, *, review=True):
    from app.services import workflow_ops
    user, headers = register(client)
    response = client.post("/v1/ledger/deposit", json={"account_owner_type": "user", "account_owner_id": user["id"], "amount": {"amount": "1000", "currency": "ACP"}, "reference": "operations-test-fixture"}, headers=headers)
    assert response.status_code == 201
    project, automation, definition = create(client, headers)
    calls = []
    async def execute(*args, **kwargs):
        calls.append(kwargs)
        return LlmExecutionResult({"deliverable": {"summary": "Context evidence"}}, None, "test", "model", "succeeded", False)
    monkeypatch.setattr(workflow_ops, "execute_paid_workflow_with_llm", execute)
    monkeypatch.setenv("PLATFORM_ADMIN_USER_IDS", user["id"])
    get_settings.cache_clear()
    return user, headers, project, automation, definition, calls


def db_edit(model, row_id, update):
    import asyncio
    from app.db.session import SessionLocal
    async def task():
        async with SessionLocal() as session:
            row = await session.get(model, row_id)
            update(row)
            await session.commit()
    asyncio.run(task())


def test_members_view_edit_revoke_and_cannot_spend_owners_credits(client, monkeypatch):
    _, headers, project, automation, definition, _ = funded_setup(client, monkeypatch)
    member, member_headers = register(client)
    path = f"/v1/workflow-ops/projects/{project['id']}/members"
    assert client.post(path, json={"email": member["email"], "role": "viewer"}, headers=headers).status_code == 200
    visible = client.get("/v1/workflow-ops", headers=member_headers).json()
    assert any(p["id"] == project["id"] for p in visible["projects"])
    assert client.put(f"/v1/workflow-ops/projects/{project['id']}", json={"name": "No"}, headers=member_headers).status_code == 404
    assert client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "member-cannot-spend", "max_cost_acp": "100"}, headers=member_headers).status_code == 404
    assert client.post(path, json={"email": member["email"], "role": "editor"}, headers=headers).status_code == 200
    assert client.put(f"/v1/workflow-ops/projects/{project['id']}", json={"name": "Shared", "context": "Shared context"}, headers=member_headers).status_code == 200
    assert client.delete(f"/v1/workflow-ops/projects/{project['id']}", headers=member_headers).status_code == 404
    assert client.post(path, json={"email": member["email"], "role": "remove"}, headers=headers).status_code == 200
    assert not any(p["id"] == project["id"] for p in client.get("/v1/workflow-ops", headers=member_headers).json()["projects"])


def test_batch_charges_per_finished_row_and_cancel_stops_remaining(client, monkeypatch):
    _, headers, _, automation, _, calls = funded_setup(client, monkeypatch)
    publish(client, headers, automation)
    queued = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "batch-cancel-test", "max_cost_acp": "100", "kind": "batch", "rows": [{"project_name": "One"}, {"project_name": "Two"}, {"project_name": "Three"}]}, headers=headers)
    assert queued.status_code == 202, queued.text
    op_id = queued.json()["id"]
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    partial = client.get(f"/v1/workflow-ops/runs/{op_id}", headers=headers).json()
    assert partial["state"] == "queued"
    assert len(partial["progress"]["items"]) == 2
    assert client.post(f"/v1/workflow-ops/runs/{op_id}/cancel", headers=headers).status_code == 200
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert len(calls) == 2
    assert client.get(f"/v1/workflow-ops/runs/{op_id}", headers=headers).json()["cost_acp"] == partial["cost_acp"]


def test_fallback_refunds_current_step_and_never_delivers(client, monkeypatch):
    from app.services import workflow_ops
    _, headers, _, automation, _, _ = funded_setup(client, monkeypatch)
    async def degraded(*args, **kwargs):
        return LlmExecutionResult({"deliverable": {"summary": "Template"}}, None, "disabled", "none", "failed", True)
    monkeypatch.setattr(workflow_ops, "execute_paid_workflow_with_llm", degraded)
    publish(client, headers, automation)
    queued = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "fallback-refund-test", "max_cost_acp": "100"}, headers=headers).json()
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    result = client.get(f"/v1/workflow-ops/runs/{queued['id']}", headers=headers).json()
    assert result["state"] == "failed"
    assert Decimal(result["cost_acp"]) == 0
    assert not result["progress"]["deliveries"]
    base_id = result["progress"]["items"][0]["run_id"]
    trail = client.get(f"/v1/workflow-store/runs/{base_id}/evidence-export", headers=headers)
    assert trail.status_code == 200
    assert "refunded" in trail.text


def test_byok_request_local_and_delivery_only_after_review(client, monkeypatch):
    from app.services import workflow_ops
    from app.services.llm import workflow_provider_credentials
    _, headers, _, automation, definition, _ = funded_setup(client, monkeypatch)
    key = "test-only-private-provider-token"
    byok = client.post("/v1/workflow-ops/connections", json={"name": "Own model", "kind": "anthropic", "secret": key, "config": {"model": "test-model"}}, headers=headers).json()
    telegram = client.post("/v1/workflow-ops/connections", json={"name": "Team channel", "kind": "telegram", "secret": "123456:test_only_not_a_real_bot_token", "config": {"chat_id": "12345"}, "allow_delivery": True}, headers=headers)
    assert telegram.status_code == 201, telegram.text
    revision = client.post(f"/v1/workflow-ops/automations/{automation['id']}/versions", json={**definition, "provider_connection_id": byok["id"], "connection_ids": [telegram.json()["id"]]}, headers=headers)
    assert revision.status_code == 201, revision.text
    publish(client, headers, automation, 2)
    observed = []
    async def execute(*args, **kwargs):
        observed.append(dict(workflow_provider_credentials.get()))
        return LlmExecutionResult({"deliverable": {"summary": "Context evidence"}}, None, "teneta_claude", "test-model", "succeeded", False)
    deliveries = []
    async def fake_deliver(connection, operation, output):
        assert operation.progress_json["deliveries"][0]["state"] == "attempting"
        deliveries.append(output)
        return {"connection_id": str(connection.id), "state": "delivered", "http_status": 200}
    monkeypatch.setattr(workflow_ops, "execute_paid_workflow_with_llm", execute)
    monkeypatch.setattr(workflow_ops, "deliver", fake_deliver)
    queued = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "byok-review-test", "max_cost_acp": "100"}, headers=headers).json()
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert observed[0]["api_key"] == key
    assert workflow_provider_credentials.get() is None
    assert not deliveries
    assert client.post(f"/v1/workflow-ops/runs/{queued['id']}/review", json={"decision": "approve"}, headers=headers).status_code == 200
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert len(deliveries) == 1
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert len(deliveries) == 1
    result = client.get(f"/v1/workflow-ops/runs/{queued['id']}", headers=headers)
    assert key not in result.text
    assert result.json()["progress"]["deliveries"][0]["state"] == "delivered"


def test_schedule_due_idempotency_spending_cap_and_expired_content(client, monkeypatch):
    from datetime import timedelta
    from app.db.models import WorkflowAutomation, WorkflowOperationRun
    from app.services.workflow_ops_support import now
    _, headers, _, automation, _, calls = funded_setup(client, monkeypatch)
    publish(client, headers, automation)
    response = client.put(f"/v1/workflow-ops/automations/{automation['id']}/schedule", json={"enabled": True, "interval_minutes": 60, "monthly_budget_acp": "10"}, headers=headers)
    assert response.status_code == 200
    db_edit(WorkflowAutomation, automation["id"], lambda row: setattr(row, "next_run_at", now()-timedelta(seconds=1)))
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert len(calls) == 1
    db_edit(WorkflowAutomation, automation["id"], lambda row: setattr(row, "next_run_at", now()-timedelta(minutes=2)))
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    assert len(calls) == 1, "Budget must stop a second model call"
    workspace = client.get("/v1/workflow-ops", headers=headers).json()
    runs = [r for r in workspace["runs"] if r["automation_id"] == automation["id"]]
    assert len(runs) == 2
    assert any(r["state"] == "failed" and Decimal(r["cost_acp"]) == 0 for r in runs)
    first = next(r for r in runs if Decimal(r["cost_acp"]) > 0)
    db_edit(WorkflowOperationRun, first["id"], lambda row: setattr(row, "expires_at", now()-timedelta(seconds=1)))
    assert client.post("/v1/workflow-ops/tick", headers=headers).status_code == 200
    expired = client.get(f"/v1/workflow-ops/runs/{first['id']}", headers=headers).json()
    assert expired["state"] == "expired"
    assert "items" not in expired["progress"]


def test_first_step_quality_failure_requires_review_even_if_last_passes(client, monkeypatch):
    from app.services import workflow_ops
    _, headers, _, automation, definition, _ = funded_setup(client, monkeypatch)
    revision = {**definition, "require_review": False, "steps": [{"slug": "token-listing-pack"}] * 2}
    assert client.post(f"/v1/workflow-ops/automations/{automation['id']}/versions", json=revision, headers=headers).status_code == 201
    publish(client, headers, automation, 2)
    calls = []
    async def execute(*args, **kwargs):
        calls.append(True)
        summary = "Missing criterion" if len(calls) == 1 else "Context evidence"
        return LlmExecutionResult({"deliverable": {"summary": summary}}, None, "test", "model", "succeeded", False)
    monkeypatch.setattr(workflow_ops, "execute_paid_workflow_with_llm", execute)
    queued = client.post(f"/v1/workflow-ops/automations/{automation['id']}/runs", json={"idempotency_key": "chain-quality-test", "max_cost_acp": "100"}, headers=headers).json()
    client.post("/v1/workflow-ops/tick", headers=headers)
    result = client.get(f"/v1/workflow-ops/runs/{queued['id']}", headers=headers).json()
    assert len(calls) == 2
    assert result["state"] == "awaiting_review"
    assert not result["progress"]["items"][0]["quality"]["passed"]
    assert result["progress"]["items"][1]["quality"]["passed"]
