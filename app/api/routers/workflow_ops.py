"""Authenticated project, workflow and execution management."""
from uuid import uuid4
from datetime import timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func, or_
from app.api.deps import DbSession, require_auth, require_platform_admin
from app.db.models import WorkflowProject, WorkflowConnection, WorkflowAutomation, WorkflowOperationRun
from app.schemas.workflow_ops import ProjectWrite, ConnectionWrite, AutomationWrite, ScheduleWrite, EnqueueRequest, ReviewWrite, TrialWrite, VersionSelect, DeliveryRetry, ProjectMemberWrite
from app.services import workflow_ops as ops
from app.services.workflow_ops_support import now, seal, digest, bounded_json, validate_connection, secret_key
from app.services.rate_limit import enforce_rate_limit, get_request_ip

router = APIRouter(prefix="/workflow-ops", tags=["Workflow operations"])


@router.get("/capabilities")
async def capabilities():
    from app.config import get_settings
    from app.services.workflow_execution import find_workflow_template
    return {"workflow_slugs": sorted(slug for slug in ops.OPS_SLUGS if find_workflow_template(slug)), "steps_limit": 5, "batch_rows_limit": 20, "schedule_min_minutes": 60, "trial": {"per_account": 1, "platform_daily_limit": 20, "transferable": False}, "connectors": ["webhook", "telegram", "google_sheets", "hubspot", "anthropic"], "private_execution": "Self-hosted deployment profile; hosting is supplied by the customer", "quality_scope": "Structure and declared tests; not independent fact verification", "worker": {"enabled": get_settings().workflow_operations_worker_enabled, **ops.WORKER_HEALTH}}


@router.get("")
async def index(session: DbSession, user_id: str = Depends(require_auth)):
    result = {}
    projects = (await session.execute(select(WorkflowProject).where(or_(WorkflowProject.owner_user_id == user_id, WorkflowProject.members_json.has_key(user_id))).limit(100))).scalars().all()
    project_ids = [row.id for row in projects]
    shared_automations = (await session.execute(select(WorkflowAutomation.id).where(WorkflowAutomation.project_id.in_(project_ids)))).scalars().all()
    for key, model, serialize in [("projects", WorkflowProject, ops.public_project), ("connections", WorkflowConnection, ops.public_connection), ("automations", WorkflowAutomation, ops.public_automation), ("runs", WorkflowOperationRun, ops.public_run)]:
        if model is WorkflowProject:
            result[key] = [serialize(row) for row in projects]
            continue
        predicate = model.owner_user_id == user_id
        if model is WorkflowAutomation:
            predicate = or_(predicate, model.project_id.in_(project_ids))
        if model is WorkflowOperationRun:
            predicate = or_(predicate, model.automation_id.in_(shared_automations))
        rows = (await session.execute(select(model).where(predicate).order_by(model.created_at.desc()).limit(100))).scalars().all()
        result[key] = [serialize(row) for row in rows]
    result["user_id"] = user_id
    from app.api.deps import is_platform_admin_user
    result["is_operator"] = await is_platform_admin_user(session, user_id)
    return result


@router.post("/projects", status_code=201)
async def create_project(body: ProjectWrite, session: DbSession, user_id: str = Depends(require_auth)):
    count = await session.scalar(select(func.count()).select_from(WorkflowProject).where(WorkflowProject.owner_user_id == user_id))
    if count >= 30:
        raise HTTPException(409, "Project limit reached")
    row = WorkflowProject(id=uuid4(), owner_user_id=user_id, name=body.name, context_json=bounded_json({"text": body.context, "documents": [doc.model_dump() for doc in body.documents]}), retention_days=body.retention_days, created_at=now())
    session.add(row)
    await session.flush()
    return ops.public_project(row)


@router.put("/projects/{row_id}")
async def update_project(row_id: str, body: ProjectWrite, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.project_access(session, user_id, row_id, write=True)
    await session.execute(select(WorkflowProject.id).where(WorkflowProject.id == row.id).with_for_update())
    row.name, row.retention_days = body.name, body.retention_days
    row.context_json = bounded_json({"text": body.context, "documents": [doc.model_dump() for doc in body.documents]})
    row.created_at = now()  # The disclosed retention window starts at the last context update.
    return ops.public_project(row)


@router.delete("/projects/{row_id}")
async def remove_project(row_id: str, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowProject, user_id, row_id, lock=True)
    automations = (await session.execute(select(WorkflowAutomation).where(WorkflowAutomation.project_id == row.id))).scalars().all()
    for automation in automations:
        runs = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.automation_id == automation.id).with_for_update())).scalars().all()
        for run in runs:
            await ops.scrub_operation(session, run)
    await session.delete(row)
    return {"deleted": True, "financial_records": "Retained without project content"}


@router.post("/connections", status_code=201)
async def create_connection(body: ConnectionWrite, session: DbSession, user_id: str = Depends(require_auth)):
    await validate_connection(body)
    count = await session.scalar(select(func.count()).select_from(WorkflowConnection).where(WorkflowConnection.owner_user_id == user_id))
    if count >= 20:
        raise HTTPException(409, "Connection limit reached")
    row = WorkflowConnection(id=uuid4(), owner_user_id=user_id, name=body.name, kind=body.kind, config_json=body.config, secret_box=seal(body.secret, user_id), allow_delivery=body.allow_delivery, created_at=now())
    session.add(row)
    await session.flush()
    return ops.public_connection(row)


@router.delete("/connections/{row_id}")
async def remove_connection(row_id: str, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowConnection, user_id, row_id, lock=True)
    await session.delete(row)
    return {"deleted": True}


@router.post("/automations", status_code=201)
async def create_automation(body: AutomationWrite, session: DbSession, user_id: str = Depends(require_auth)):
    definition = await ops.validate_definition(session, user_id, body)
    count = await session.scalar(select(func.count()).select_from(WorkflowAutomation).where(WorkflowAutomation.owner_user_id == user_id))
    if count >= 30:
        raise HTTPException(409, "Automation limit reached")
    row = WorkflowAutomation(id=uuid4(), owner_user_id=user_id, project_id=body.project_id, name=body.name, versions_json=[{"version": 1, "definition": definition, "hash": digest(definition), "created_at": now().isoformat(), "validation": "structure_only"}], enabled=False, spent_acp=0, monthly_budget_acp=0, interval_minutes=1440, created_at=now())
    session.add(row)
    await session.flush()
    return ops.public_automation(row)


@router.post("/automations/{row_id}/versions", status_code=201)
async def new_version(row_id: str, body: AutomationWrite, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowAutomation, user_id, row_id, lock=True)
    if body.project_id != str(row.project_id):
        raise HTTPException(422, "Version cannot change the project")
    definition = await ops.validate_definition(session, user_id, body)
    if len(row.versions_json) >= 50:
        raise HTTPException(409, "Version limit reached")
    row.versions_json = [*row.versions_json, {"version": row.versions_json[-1]["version"]+1, "definition": definition, "hash": digest(definition), "created_at": now().isoformat(), "validation": "structure_only"}]
    row.name = body.name
    return ops.public_automation(row)


@router.post("/automations/{row_id}/publish")
async def publish(row_id: str, body: VersionSelect, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowAutomation, user_id, row_id, lock=True)
    revision = next((v for v in row.versions_json if v["version"] == body.version), None)
    if revision is None:
        raise HTTPException(404, "Version not found")
    await ops.validate_definition(session, user_id, AutomationWrite.model_validate(revision["definition"]))
    row.published_version = body.version
    # Rollback changes future snapshots only; prior receipts stay immutable.
    return ops.public_automation(row)


@router.put("/automations/{row_id}/schedule")
async def schedule(row_id: str, body: ScheduleWrite, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowAutomation, user_id, row_id, lock=True)
    if body.enabled and not row.published_version:
        raise HTTPException(409, "Publish first")
    row.enabled, row.interval_minutes = body.enabled, body.interval_minutes
    row.monthly_budget_acp = body.monthly_budget_acp
    row.next_run_at = now()+timedelta(minutes=body.interval_minutes) if body.enabled else None
    return ops.public_automation(row)


@router.post("/automations/{row_id}/runs", status_code=202)
async def enqueue_run(row_id: str, body: EnqueueRequest, session: DbSession, user_id: str = Depends(require_auth)):
    await enforce_rate_limit(key=f"workflow-ops-enqueue:{user_id}", limit=15, window_seconds=60)
    row = await ops.owned(session, WorkflowAutomation, user_id, row_id, lock=True)
    pending = await session.scalar(select(func.count()).select_from(WorkflowOperationRun).where(WorkflowOperationRun.owner_user_id == user_id, WorkflowOperationRun.state == "queued"))
    if pending >= 5:
        existing = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.owner_user_id == user_id, WorkflowOperationRun.request_key == body.idempotency_key))).scalar_one_or_none()
        if existing is None:
            raise HTTPException(429, "Wait for queued work to complete")
    return ops.public_run(await ops.enqueue(session, user_id, row, body))


@router.get("/runs/{row_id}")
async def get_run(row_id: str, session: DbSession, user_id: str = Depends(require_auth)):
    return ops.public_run(await ops.run_access(session, user_id, row_id))


@router.post("/runs/{row_id}/cancel")
async def cancel_run(row_id: str, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowOperationRun, user_id, row_id, lock=True)
    if row.state != "queued":
        raise HTTPException(409, "Only queued work can be cancelled")
    row.state = "cancelled"
    return ops.public_run(row)


@router.post("/runs/{row_id}/review")
async def review(row_id: str, body: ReviewWrite, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.run_access(session, user_id, row_id, write=True)
    if row.state != "awaiting_review":
        raise HTTPException(409, "Run is not awaiting review")
    progress = dict(row.progress_json)
    progress["review"] = {"decision": body.decision, "note": body.note, "reviewer_user_id": user_id, "at": now().isoformat()}
    if body.edited_output is not None:
        progress["reviewed_output"] = bounded_json(body.edited_output, 100000)
        progress["reviewed_output_hash"] = digest(body.edited_output)
    row.progress_json = progress
    row.state = "approved" if body.decision == "approve" else "rejected"
    return ops.public_run(row)


@router.post("/projects/{row_id}/members")
async def share_project(row_id: str, body: ProjectMemberWrite, session: DbSession, user_id: str = Depends(require_auth)):
    from app.db.models import User
    row = await ops.owned(session, WorkflowProject, user_id, row_id, lock=True)
    member = (await session.execute(select(User).where(func.lower(User.email) == body.email.strip().lower()))).scalar_one_or_none()
    if member is None:
        raise HTTPException(404, "Registered account not found; no invitation was sent")
    if str(member.id) == user_id:
        raise HTTPException(422, "Owner access cannot be changed")
    members = dict(row.members_json or {})
    if body.role == "remove":
        members.pop(str(member.id), None)
    else:
        if len(members) >= 20 and str(member.id) not in members:
            raise HTTPException(409, "Project member limit reached")
        members[str(member.id)] = body.role
    row.members_json = members
    return ops.public_project(row)


@router.post("/runs/{row_id}/retry-delivery")
async def retry_delivery(row_id: str, body: DeliveryRetry, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowOperationRun, user_id, row_id, lock=True)
    if row.state != "completed" or not body.confirm_retry:
        raise HTTPException(409, "Explicit retry confirmation required after completion")
    progress = dict(row.progress_json)
    found = [d for d in progress.get("deliveries", []) if d["connection_id"] == body.connection_id and d["state"] == "unknown_or_failed"]
    if not found:
        raise HTTPException(409, "No failed delivery to retry")
    progress["delivery_history"] = [*progress.get("delivery_history", []), *found]
    progress["deliveries"] = [d for d in progress.get("deliveries", []) if d["connection_id"] != body.connection_id]
    row.progress_json = progress
    row.state = "approved"
    return ops.public_run(row)


@router.post("/trial")
async def run_trial(body: TrialWrite, request: Request, session: DbSession, user_id: str = Depends(require_auth)):
    import hmac, hashlib
    await enforce_rate_limit(key=f"workflow-ops-trial:{get_request_ip(request)}", limit=5, window_seconds=600)
    ip_hash = hmac.new(secret_key(), get_request_ip(request).encode(), hashlib.sha256).hexdigest()
    return ops.public_run(await ops.trial(session, user_id, body, ip_hash))


@router.post("/tick")
async def tick(user_id: str = Depends(require_platform_admin)):
    return await ops.workflow_ops_tick()


@router.get("/admin/economics")
async def economics(session: DbSession, user_id: str = Depends(require_platform_admin)):
    rows = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.created_at >= now()-timedelta(days=60)))).scalars().all()
    paid = [r for r in rows if r.kind not in {"trial", "test"} and Decimal(r.cost_acp) > 0]
    users = {str(r.owner_user_id) for r in paid}
    repeat_users = sum(1 for uid in users if len([r for r in paid if str(r.owner_user_id) == uid]) > 1)
    return {"window_days": 60, "paid_operations": len(paid), "paid_users": len(users), "repeat_users": repeat_users, "trial_operations": sum(r.kind == "trial" for r in rows), "test_operations": sum(r.kind == "test" for r in rows), "captured_platform_credits_acp": str(sum((Decimal(r.cost_acp) for r in paid), Decimal(0))), "actual_provider_invoice_cost": None, "actual_margin": None, "cash_revenue_eur": None, "basis": "Platform-credit accounting; not confirmed fiat sales. Provider cost and cash margin require invoices."}


@router.get("/automations/{row_id}/export")
async def export_automation(row_id: str, session: DbSession, user_id: str = Depends(require_auth)):
    row = await ops.owned(session, WorkflowAutomation, user_id, row_id)
    definition = dict(row.versions_json[-1]["definition"])
    definition["connection_ids"] = []
    definition["provider_connection_id"] = None
    return {"format": "ancap-workflow-plan/v1", "definition": definition, "note": "Reconnect credentials and select a project on import"}


@router.get("/private-profile")
async def private_profile(user_id: str = Depends(require_auth)):
    return {"format": "ancap-private-deployment/v1", "repository": "https://github.com/ancapcloud/ancap", "compose_file": "docker-compose.prod.yml", "required_secrets": ["SECRET_KEY", "CURSOR_SECRET", "CRON_SECRET", "POSTGRES_PASSWORD", "ACP_RPC_TOKEN"], "llm_options": ["Tenant Anthropic credentials", "Customer Anthropic BYOK", "Self-hosted Ollama configured by operator"], "documentation": "/docs/workflow-operations", "includes_hosting": False, "warning": "Deploy into your own infrastructure; generate fresh secrets and use separate database/ledger. This export does not provision a hosted private instance."}
