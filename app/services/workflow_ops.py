"""Durable, bounded workflow orchestration over the existing ACP checkout engine."""
from __future__ import annotations
from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert
from fastapi import HTTPException
from app.db.models import WorkflowProject, WorkflowConnection, WorkflowAutomation, WorkflowOperationRun, WorkflowRunRecord
from app.db.session import async_session_maker
from app.schemas.workflow_ops import AutomationWrite, EnqueueRequest
from app.schemas.workflow_store import WorkflowRunPaymentIntentCreateRequest
from app.services.workflow_execution import find_workflow_template
from app.services.workflow_ops_support import now, digest, bounded_json, unseal, quality_passport, market_snapshot, deliver
from app.services.llm import execute_paid_workflow_with_llm, workflow_provider_credentials

OPS_SLUGS = frozenset({"token-listing-pack", "crypto-campaign-builder", "telegram-growth-kit", "airdrop-bounty-builder", "token-risk-report", "token-launch-audit-pack", "exchange-listing-submission-pack", "kol-telegram-campaign-builder", "token-risk-report-pro", "agent-api-readiness-pack", "ai-iso-governance-readiness-pack", "market-direction-brief", "crypto-cycle-momentum-scan", "commodity-price-outlook"})
WORKER_HEALTH = {"last_tick": None, "last_error_type": None}


async def owned(session, model, owner, row_id, lock=False):
    try:
        row_id = str(UUID(str(row_id)))
    except ValueError:
        raise HTTPException(404, "Not found") from None
    query = select(model).where(model.id == row_id, model.owner_user_id == str(owner))
    if lock:
        query = query.with_for_update()
    row = (await session.execute(query)).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "Not found")
    return row


async def validate_definition(session, owner, body: AutomationWrite):
    await project_access(session, owner, body.project_id, write=True)
    value = bounded_json(body.model_dump())
    if any(find_workflow_template(step.slug) is None or step.slug not in OPS_SLUGS for step in body.steps):
        raise HTTPException(422, "Unknown workflow step")
    from app.services.llm import _COMPLIANCE_LOCKED_SLUGS
    if any(step.slug in _COMPLIANCE_LOCKED_SLUGS for step in body.steps):
        raise HTTPException(422, "This sensitive template is not available for unattended automation")
    for connection_id in body.connection_ids:
        connection = await owned(session, WorkflowConnection, owner, connection_id)
        if connection.kind == "anthropic" or not connection.allow_delivery:
            raise HTTPException(422, "Delivery connection needs explicit authorization")
    if body.provider_connection_id:
        connection = await owned(session, WorkflowConnection, owner, body.provider_connection_id)
        if connection.kind != "anthropic":
            raise HTTPException(422, "Model connection required")
    import re
    if any(not re.fullmatch(r"[a-z0-9-]{1,80}", coin) for coin in body.coin_ids):
        raise HTTPException(422, "Invalid market coin ID")
    return value


def public_project(row):
    return {"id": str(row.id), "owner_user_id": str(row.owner_user_id), "members": row.members_json, "name": row.name, "context": row.context_json, "retention_days": row.retention_days, "created_at": row.created_at}


def public_connection(row):
    return {"id": str(row.id), "name": row.name, "kind": row.kind, "config": row.config_json, "credential_stored": bool(row.secret_box), "allow_delivery": row.allow_delivery, "status": "configured_not_live_verified"}


def public_automation(row):
    return {"id": str(row.id), "owner_user_id": str(row.owner_user_id), "project_id": str(row.project_id), "name": row.name, "versions": row.versions_json, "published_version": row.published_version, "enabled": row.enabled, "interval_minutes": row.interval_minutes, "monthly_budget_acp": str(row.monthly_budget_acp), "spent_acp": str(row.spent_acp), "budget_month": row.budget_month, "next_run_at": row.next_run_at}


def public_run(row):
    return {"id": str(row.id), "owner_user_id": str(row.owner_user_id), "automation_id": str(row.automation_id) if row.automation_id else None, "kind": row.kind, "state": row.state, "progress": row.progress_json, "cost_acp": str(row.cost_acp), "max_cost_acp": str(row.max_cost_acp), "created_at": row.created_at, "expires_at": row.expires_at}


async def enqueue(session, owner, automation, body: EnqueueRequest, *, scheduled=False):
    version_number = (automation.versions_json[-1]["version"] if body.kind == "test" else automation.published_version)
    if not version_number:
        raise HTTPException(409, "Publish a version before running")
    revision = next(v for v in automation.versions_json if v["version"] == version_number)
    project = await project_access(session, owner, automation.project_id)
    if project.created_at + timedelta(days=project.retention_days) <= now():
        project.context_json = {}
    request_hash = digest({"automation_id": str(automation.id), **body.model_dump(mode="json")})
    existing = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.owner_user_id == str(owner), WorkflowOperationRun.request_key == body.idempotency_key))).scalar_one_or_none()
    if existing:
        if existing.request_hash != request_hash:
            raise HTTPException(409, "Idempotency key used for different inputs")
        return existing
    from app.services.market_economy import get_wacp_usd_oracle
    await get_wacp_usd_oracle()
    # Use the same live quote construction as direct purchases, never an assumed FX rate.
    from app.api.routers.workflow_store import _build_workflow_run_record
    expected = sum(Decimal(_build_workflow_run_record(owner_user_id=owner, template=find_workflow_template(step["slug"]), payment_currency="ACP", unlock_full_result=True, inputs={}).quoted_amount) for step in revision["definition"]["steps"])
    expected *= max(1, len(body.rows))
    if expected > body.max_cost_acp:
        raise HTTPException(409, {"message": "Maximum cost below current quote", "required_acp": str(expected)})
    snapshot = bounded_json({"definition": revision["definition"], "version": revision["version"], "context": project.context_json, "inputs": body.inputs, "rows": body.rows or [{}], "scheduled": scheduled, "estimated_acp": str(expected)})
    row_id = uuid4()
    await session.execute(insert(WorkflowOperationRun).values(id=row_id, owner_user_id=owner, automation_id=automation.id, request_key=body.idempotency_key, request_hash=request_hash, kind=body.kind, state="queued", snapshot_json=snapshot, progress_json={"cursor": 0, "items": [], "deliveries": []}, cost_acp=0, max_cost_acp=body.max_cost_acp, created_at=now(), expires_at=now()+timedelta(days=project.retention_days)).on_conflict_do_nothing(index_elements=["owner_user_id", "request_key"]))
    row = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.owner_user_id == str(owner), WorkflowOperationRun.request_key == body.idempotency_key))).scalar_one()
    if row.request_hash != request_hash:
        raise HTTPException(409, "Idempotency key conflict")
    return row


async def _process_item(session, operation):
    from app.api.routers.workflow_store import _build_workflow_run_record, _do_create_workflow_run_payment_intent, _capture_reserved_workflow_payment, _refund_reserved_workflow_payment
    automation = await owned(session, WorkflowAutomation, operation.owner_user_id, operation.automation_id, lock=True)
    await project_access(session, str(operation.owner_user_id), automation.project_id)
    # Serialize new automation spend per owner; the checkout engine owns ledger accounting.
    await session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int(digest(str(operation.owner_user_id))[:15], 16)})
    data = operation.snapshot_json
    definition = data["definition"]
    progress = dict(operation.progress_json)
    steps = definition["steps"]
    cursor = int(progress.get("cursor", 0))
    total = len(steps)*len(data["rows"])
    if cursor >= total:
        operation.state = "awaiting_review" if definition.get("require_review", True) else "approved"
        operation.progress_json = progress
        return
    if automation.budget_month != now().strftime("%Y-%m"):
        automation.spent_acp = 0
        automation.budget_month = now().strftime("%Y-%m")
    step = steps[cursor % len(steps)]
    row_index = cursor // len(steps)
    inputs = {**definition.get("inputs", {}), **step.get("inputs", {}), **data.get("inputs", {}), **data["rows"][row_index], "project_context": data.get("context", {})}
    sources = []
    if definition.get("coin_ids"):
        if "market" not in progress:
            market, sources = await market_snapshot(definition["coin_ids"])
            previous = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.automation_id == automation.id, WorkflowOperationRun.id != operation.id, WorkflowOperationRun.state.in_(["completed", "awaiting_review", "approved"])).order_by(WorkflowOperationRun.created_at.desc()).limit(1))).scalar_one_or_none()
            progress["market"] = market
            progress["sources"] = sources
            progress["previous_market"] = (previous.progress_json or {}).get("market", {}) if previous else {}
        sources = progress.get("sources", [])
        inputs.update(market_snapshot=progress["market"], previous_market_snapshot=progress.get("previous_market", {}))
    if cursor % len(steps):
        inputs["previous_step_output"] = progress["items"][-1]["output"]
    bounded_json(inputs)
    template = find_workflow_template(step["slug"])
    if template is None:
        raise HTTPException(409, "Published workflow is no longer available")
    from app.services.market_economy import get_wacp_usd_oracle
    await get_wacp_usd_oracle()
    run = _build_workflow_run_record(owner_user_id=str(operation.owner_user_id), template=template, payment_currency="ACP", unlock_full_result=True, inputs=inputs)
    price = Decimal(run.quoted_amount)
    if Decimal(operation.cost_acp)+price > Decimal(operation.max_cost_acp):
        raise HTTPException(409, "Operation spending limit reached")
    if data.get("scheduled") and Decimal(automation.spent_acp)+price > Decimal(automation.monthly_budget_acp):
        raise HTTPException(409, "Monthly schedule spending limit reached")
    session.add(run)
    await session.flush()
    await _do_create_workflow_run_payment_intent(session, str(operation.owner_user_id), str(run.id), WorkflowRunPaymentIntentCreateRequest(payment_method="credits", note=f"workflow-ops:{operation.kind}:{operation.id}"))
    credentials = None
    if definition.get("provider_connection_id"):
        connection = await owned(session, WorkflowConnection, operation.owner_user_id, definition["provider_connection_id"])
        credentials = {"provider": "teneta_claude", "api_key": unseal(connection.secret_box, connection.owner_user_id), "model": connection.config_json.get("model", "claude-sonnet-4-6")}
    token = workflow_provider_credentials.set(credentials)
    try:
        result = await execute_paid_workflow_with_llm(session, template=template, inputs=inputs, owner_user_id=operation.owner_user_id, workflow_run_id=run.id)
    finally:
        workflow_provider_credentials.reset(token)
    usage = {"provider": result.provider, "model": result.model, "fallback_used": result.fallback_used, "usage_event_id": result.usage_event_id}
    quality = quality_passport(result.result, usage, sources, definition)
    receipt = dict(run.receipt_json or {})
    receipt["workflow_operation"] = {"id": str(operation.id), "version": data["version"], "kind": operation.kind, "quality": quality}
    run.receipt_json = receipt
    run.result_json = result.result
    if result.fallback_used:
        run.status = "failed"
        await _refund_reserved_workflow_payment(session, run, "Automation refused degraded model output")
        operation.state = "failed"
        progress["error"] = "Model output unavailable; credits refunded for this step"
    else:
        run.status = "completed"
        await _capture_reserved_workflow_payment(session, run)
        operation.cost_acp = Decimal(operation.cost_acp)+price
        if data.get("scheduled"):
            automation.spent_acp = Decimal(automation.spent_acp)+price
        progress["cursor"] = cursor+1
        if progress["cursor"] >= total:
            operation.state = "awaiting_review" if definition.get("require_review", True) or not quality["passed"] or any(not item["quality"]["passed"] for item in progress.get("items", [])) else "approved"
    progress["items"] = [*progress.get("items", []), {"row": row_index, "step": cursor % len(steps), "run_id": str(run.id), "slug": step["slug"], "output": result.result, "quality": quality, "price_acp": str(price) if not result.fallback_used else "0"}]
    operation.progress_json = progress


async def _process_delivery(session, operation):
    progress = dict(operation.progress_json)
    definition = operation.snapshot_json["definition"]
    completed = {entry["connection_id"] for entry in progress.get("deliveries", [])}
    pending = [cid for cid in definition.get("connection_ids", []) if cid not in completed]
    if not pending:
        operation.state = "completed"
        return None
    cid = pending[0]
    attempt_id = str(uuid4())
    progress["deliveries"] = [*progress.get("deliveries", []), {"connection_id": cid, "attempt_id": attempt_id, "state": "attempting", "at": now().isoformat()}]
    operation.progress_json = progress
    if len(progress["deliveries"]) >= len(definition.get("connection_ids", [])):
        operation.state = "completed"
    # Persist the outbox claim BEFORE any network side effect. A crash never retries it.
    return {"operation_id": str(operation.id), "connection_id": cid, "attempt_id": attempt_id}


async def _send_prepared_delivery(claim):
    async with async_session_maker() as session:
        operation = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.id == claim["operation_id"]).with_for_update())).scalar_one_or_none()
        if operation is None or operation.state not in {"approved", "completed"}:
            return
        progress = dict(operation.progress_json)
        attempts = progress.get("deliveries", [])
        if not any(d.get("attempt_id") == claim["attempt_id"] and d["state"] == "attempting" for d in attempts):
            return
        cid = claim["connection_id"]
        try:
            connection = await owned(session, WorkflowConnection, operation.owner_user_id, cid)
            if not connection.allow_delivery:
                raise HTTPException(409, "Delivery permission revoked")
            output = progress["reviewed_output"] if "reviewed_output" in progress else {"items": [item["output"] for item in progress.get("items", [])]}
            delivery = await deliver(connection, operation, output)
        except Exception:
            delivery = {"connection_id": cid, "state": "unknown_or_failed", "at": now().isoformat(), "message": "Check destination before explicitly retrying"}
        delivery["attempt_id"] = claim["attempt_id"]
        progress["deliveries"] = [delivery if d.get("attempt_id") == claim["attempt_id"] else d for d in attempts]
        operation.progress_json = progress
        await session.commit()


async def workflow_ops_tick(max_items=2):
    summary = {"scheduled": 0, "processed": 0, "expired": 0}
    async with async_session_maker() as session:
        due = (await session.execute(select(WorkflowAutomation).where(WorkflowAutomation.enabled.is_(True), WorkflowAutomation.next_run_at <= now()).order_by(WorkflowAutomation.next_run_at).limit(5).with_for_update(skip_locked=True))).scalars().all()
        for automation in due:
            try:
                async with session.begin_nested():
                    await enqueue(session, str(automation.owner_user_id), automation, EnqueueRequest(idempotency_key=f"schedule:{automation.id}:{int(automation.next_run_at.timestamp())}", max_cost_acp=automation.monthly_budget_acp), scheduled=True)
                    summary["scheduled"] += 1
            except HTTPException:
                automation.enabled = False
            automation.next_run_at = now()+timedelta(minutes=automation.interval_minutes)
        await session.commit()
    # One transaction per work item bounds locks and makes restart recovery automatic.
    for _ in range(max_items):
        delivery_claim = None
        async with async_session_maker() as session:
            operation = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.state.in_(["queued", "approved"])).order_by(WorkflowOperationRun.created_at).limit(1).with_for_update(skip_locked=True))).scalar_one_or_none()
            if operation is None:
                break
            if operation.expires_at and operation.expires_at <= now():
                await scrub_operation(session, operation)
                await session.commit()
                continue
            try:
                async with session.begin_nested():
                    if operation.state == "approved":
                        delivery_claim = await _process_delivery(session, operation)
                    else:
                        await _process_item(session, operation)
            except Exception as exc:
                # Savepoint rolls back the current step and payment, not prior paid steps.
                await session.refresh(operation)
                operation.state = "failed"
                operation.progress_json = {**operation.progress_json, "error": (str(exc.detail)[:250] if isinstance(exc, HTTPException) else "Execution failed; current step was not charged")}
            await session.commit()
            summary["processed"] += 1
        if delivery_claim:
            await _send_prepared_delivery(delivery_claim)
    async with async_session_maker() as session:
        expired = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.expires_at <= now(), WorkflowOperationRun.state != "expired").limit(100).with_for_update(skip_locked=True))).scalars().all()
        for operation in expired:
            await scrub_operation(session, operation)
            summary["expired"] += 1
        # Recover uncertain outbox claims without re-sending them.
        candidates = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.state.in_(["approved", "completed"])).order_by(WorkflowOperationRun.created_at.desc()).limit(100).with_for_update(skip_locked=True))).scalars().all()
        from datetime import datetime
        for candidate in candidates:
            progress = dict(candidate.progress_json)
            changed = False
            for delivery in progress.get("deliveries", []):
                if delivery["state"] == "attempting" and datetime.fromisoformat(delivery["at"]) < now()-timedelta(minutes=2):
                    delivery["state"] = "unknown_or_failed"
                    delivery["message"] = "Interrupted delivery; check destination before retrying"
                    changed = True
            if changed:
                candidate.progress_json = progress
        projects = (await session.execute(select(WorkflowProject).where(WorkflowProject.created_at + WorkflowProject.retention_days*text("interval '1 day'") <= now(), WorkflowProject.context_json != {}).limit(100).with_for_update(skip_locked=True))).scalars().all()
        for project in projects:
            if project.created_at + timedelta(days=project.retention_days) <= now() and project.context_json:
                project.context_json = {}
        await session.commit()
    WORKER_HEALTH.update(last_tick=now().isoformat(), last_error_type=None)
    return summary


async def scrub_operation(session, operation):
    for item in operation.progress_json.get("items", []):
        base = await session.get(WorkflowRunRecord, item.get("run_id"))
        if base and str(base.owner_user_id) == str(operation.owner_user_id):
            base.inputs_json = {}
            base.result_json = None
            base.preview_json = {}
    operation.snapshot_json = {}
    operation.progress_json = {"retention": "Content deleted; billing totals retained"}
    operation.state = "expired"


async def project_access(session, user_id, project_id, write=False):
    try:
        project_id = str(UUID(str(project_id)))
    except ValueError:
        raise HTTPException(404, "Not found") from None
    row = (await session.execute(select(WorkflowProject).where(WorkflowProject.id == project_id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "Not found")
    role = "owner" if str(row.owner_user_id) == str(user_id) else (row.members_json or {}).get(str(user_id))
    if role not in ({"owner", "editor"} if write else {"owner", "editor", "viewer"}):
        raise HTTPException(404, "Not found")
    return row


async def run_access(session, user_id, run_id, write=False):
    try:
        run_id = str(UUID(str(run_id)))
    except ValueError:
        raise HTTPException(404, "Not found") from None
    query = select(WorkflowOperationRun).where(WorkflowOperationRun.id == run_id)
    if write:
        query = query.with_for_update()
    row = (await session.execute(query)).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, "Not found")
    if str(row.owner_user_id) != str(user_id):
        automation = await session.get(WorkflowAutomation, row.automation_id) if row.automation_id else None
        if automation is None:
            raise HTTPException(404, "Not found")
        await project_access(session, user_id, automation.project_id, write=write)
    return row


async def trial(session, owner, body, ip_hash):
    key = "trial-v1"
    existing = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.owner_user_id == owner, WorkflowOperationRun.request_key == key))).scalar_one_or_none()
    if existing:
        return existing
    # A nonblocking global slot protects the hard daily quota across workers/IPs.
    slot = await session.scalar(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": int(digest("workflow-trial-platform-quota")[:15], 16)})
    if not slot:
        raise HTTPException(429, "Trial worker busy; retry later")
    daily = await session.scalar(select(func.count()).select_from(WorkflowOperationRun).where(WorkflowOperationRun.kind == "trial", WorkflowOperationRun.created_at >= now().replace(hour=0, minute=0, second=0, microsecond=0)))
    same_ip = await session.scalar(select(func.count()).select_from(WorkflowOperationRun).where(WorkflowOperationRun.kind == "trial", WorkflowOperationRun.snapshot_json.contains({"ip_hash": ip_hash}), WorkflowOperationRun.created_at >= now()-timedelta(days=1)))
    if daily >= 20 or same_ip >= 3:
        raise HTTPException(429, "Trial capacity reached; try later")
    await session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int(digest("trial:"+owner)[:15], 16)})
    existing = (await session.execute(select(WorkflowOperationRun).where(WorkflowOperationRun.owner_user_id == owner, WorkflowOperationRun.request_key == key))).scalar_one_or_none()
    if existing:
        return existing
    template = find_workflow_template("token-listing-pack")
    token = workflow_provider_credentials.set({"max_tokens": 800})
    try:
        result = await execute_paid_workflow_with_llm(session, template=template, inputs=body.model_dump(), owner_user_id=owner, workflow_run_id=None)
    finally:
        workflow_provider_credentials.reset(token)
    usage = {"provider": result.provider, "model": result.model, "fallback_used": result.fallback_used}
    row = WorkflowOperationRun(id=uuid4(), owner_user_id=owner, request_key=key, request_hash=digest(body.model_dump()), kind="trial", state="degraded" if result.fallback_used else "completed", snapshot_json={"ip_hash": ip_hash}, progress_json={"output": result.result, "quality": quality_passport(result.result, usage, [], {"steps": [{"slug": template.slug}]}), "voucher": {"transferable": False, "acp_charge": "0", "limit": "one per account"}}, cost_acp=0, max_cost_acp=0, created_at=now(), expires_at=now()+timedelta(days=7))
    session.add(row)
    await session.flush()
    return row
