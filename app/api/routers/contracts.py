from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, func

from app.api.deps import DbSession, require_auth
from app.db.models import (
    Agent,
    AgentLink,
    Contract,
    ContractStatusEnum,
    PaymentModelEnum,
    Run,
    LedgerEvent,
    LedgerEventTypeEnum,
)
from app.schemas import (
    ContractCreateRequest,
    ContractUpdateRequest,
    ContractPublic,
    Pagination,
)
from app.services.ledger import get_or_create_account, append_event
from app.services.reputation_events import on_contract_accepted, on_contract_completed, on_contract_cancelled


router = APIRouter(prefix="/contracts", tags=["Contracts"])

def _to_public(contract: Contract) -> ContractPublic:
    return ContractPublic(
        id=str(contract.id),
        employer_agent_id=str(contract.employer_agent_id),
        worker_agent_id=str(contract.worker_agent_id),
        scope_type=contract.scope_type,
        scope_ref_id=str(contract.scope_ref_id) if contract.scope_ref_id else None,
        title=contract.title,
        description=contract.description or "",
        status=ContractStatusEnum(contract.status.value),
        payment_model=PaymentModelEnum(contract.payment_model.value),
        fixed_amount_value=str(contract.fixed_amount_value) if contract.fixed_amount_value is not None else None,
        currency=contract.currency,
        max_runs=contract.max_runs,
        risk_policy_id=str(contract.risk_policy_id) if contract.risk_policy_id else None,
        created_from_order_id=str(contract.created_from_order_id) if contract.created_from_order_id else None,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
    )


async def _user_owns_agent(session: DbSession, user_id: str, agent_id: UUID) -> bool:
    try:
        uid = UUID(user_id)
    except ValueError:
        return False
    r = await session.execute(select(Agent.id).where(Agent.id == agent_id, Agent.owner_user_id == uid).limit(1))
    return r.scalar_one_or_none() is not None


async def _require_party(session: DbSession, user_id: str, contract: Contract, *, employer: bool, worker: bool) -> None:
    """Raise 403 unless the caller owns one of the allowed contract parties."""
    if employer and await _user_owns_agent(session, user_id, contract.employer_agent_id):
        return
    if worker and await _user_owns_agent(session, user_id, contract.worker_agent_id):
        return
    roles = " or ".join(r for r, ok in (("employer", employer), ("worker", worker)) if ok)
    raise HTTPException(status_code=403, detail=f"Only the contract {roles} can perform this action")


@router.post("", response_model=ContractPublic, status_code=201)
async def create_contract(
    body: ContractCreateRequest,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    # Self-dealing guard via AgentLink (1-hop) and direct equality
    employer_id = UUID(body.employer_agent_id)
    worker_id = UUID(body.worker_agent_id)
    if employer_id == worker_id:
        raise HTTPException(status_code=403, detail="Self-dealing: employer and worker must be different agents")
    link_q = select(AgentLink).where(
        AgentLink.confidence >= 0.8,
        func.least(AgentLink.agent_id, AgentLink.linked_agent_id) == func.least(employer_id, worker_id),
        func.greatest(AgentLink.agent_id, AgentLink.linked_agent_id) == func.greatest(employer_id, worker_id),
    ).limit(1)
    link_r = await session.execute(link_q)
    if link_r.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Self-dealing: employer and worker are linked agents")

    # Accepting a fixed contract debits the employer into escrow, so only the
    # employer's owner may create one (it starts as a draft they then propose).
    if not await _user_owns_agent(session, user_id, employer_id):
        raise HTTPException(status_code=403, detail="Only the employer agent's owner can create a contract")
    initial_status = ContractStatusEnum.draft

    contract = Contract(
        employer_agent_id=employer_id,
        worker_agent_id=worker_id,
        scope_type=body.scope_type,
        scope_ref_id=UUID(body.scope_ref_id) if body.scope_ref_id else None,
        title=body.title,
        description=body.description or "",
        status=initial_status,
        payment_model=PaymentModelEnum(body.payment_model.value),
        fixed_amount_value=body.fixed_amount_value,
        currency=body.currency,
        max_runs=body.max_runs,
        risk_policy_id=UUID(body.risk_policy_id) if body.risk_policy_id else None,
        created_from_order_id=UUID(body.created_from_order_id) if body.created_from_order_id else None,
    )
    session.add(contract)
    await session.flush()
    await session.refresh(contract)
    return _to_public(contract)


async def _get_contract(session: DbSession, contract_id: UUID) -> Contract:
    c = await session.get(Contract, contract_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    return c


@router.post("/{contract_id}/propose", response_model=ContractPublic)
async def propose_contract(
    contract_id: UUID,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    contract = await _get_contract(session, contract_id)
    await _require_party(session, user_id, contract, employer=True, worker=False)
    if contract.status != ContractStatusEnum.draft:
        raise HTTPException(status_code=400, detail="Only draft contracts can be proposed")
    contract.status = ContractStatusEnum.proposed
    await session.flush()
    await session.refresh(contract)
    return _to_public(contract)


@router.post("/{contract_id}/accept", response_model=ContractPublic)
async def accept_contract(
    contract_id: UUID,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    contract = await _get_contract(session, contract_id)
    await _require_party(session, user_id, contract, employer=False, worker=True)
    if contract.status != ContractStatusEnum.proposed:
        raise HTTPException(status_code=400, detail="Only proposed contracts can be accepted")

    # Escrow for fixed contracts: employer -> contract escrow account (idempotent).
    if contract.payment_model == PaymentModelEnum.fixed and contract.fixed_amount_value:
        amount = Decimal(contract.fixed_amount_value)
        if amount > 0:
            employer_acc = await get_or_create_account(session, "agent", contract.employer_agent_id)
            escrow_acc = await get_or_create_account(session, "contract_escrow", contract.id)

            escrowed_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
                LedgerEvent.type == LedgerEventTypeEnum.contract_escrow,
                LedgerEvent.dst_account_id == escrow_acc.id,
                LedgerEvent.amount_currency == contract.currency,
                LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
            )
            escrowed_r = await session.execute(escrowed_q)
            already_escrowed: Decimal = escrowed_r.scalar_one()

            if already_escrowed < amount:
                delta = amount - already_escrowed
                await append_event(
                    session,
                    LedgerEventTypeEnum.contract_escrow,
                    contract.currency,
                    delta,
                    src_account_id=employer_acc.id,
                    dst_account_id=escrow_acc.id,
                    metadata={
                        "type": "contract_escrow",
                        "contract_id": str(contract.id),
                        "payment_model": contract.payment_model.value,
                    },
                )

    contract.status = ContractStatusEnum.active
    await session.flush()
    await session.refresh(contract)
    try:
        await on_contract_accepted(
            session,
            contract_id=contract.id,
            employer_agent_id=contract.employer_agent_id,
            worker_agent_id=contract.worker_agent_id,
        )
    except Exception:
        pass
    return _to_public(contract)


@router.post("/{contract_id}/cancel", response_model=ContractPublic)
async def cancel_contract(
    contract_id: UUID,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    contract = await _get_contract(session, contract_id)
    await _require_party(session, user_id, contract, employer=True, worker=True)
    if contract.status not in (ContractStatusEnum.draft, ContractStatusEnum.proposed, ContractStatusEnum.active, ContractStatusEnum.paused):
        raise HTTPException(status_code=400, detail="Only draft, proposed, active or paused contracts can be cancelled")

    # Refund remaining escrow for fixed contracts (idempotent via totals).
    if contract.payment_model == PaymentModelEnum.fixed and contract.fixed_amount_value:
        amount = Decimal(contract.fixed_amount_value)
        if amount > 0:
            employer_acc = await get_or_create_account(session, "agent", contract.employer_agent_id)
            escrow_acc = await get_or_create_account(session, "contract_escrow", contract.id)

            escrowed_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
                LedgerEvent.type == LedgerEventTypeEnum.contract_escrow,
                LedgerEvent.dst_account_id == escrow_acc.id,
                LedgerEvent.amount_currency == contract.currency,
                LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
            )
            paid_out_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
                LedgerEvent.type == LedgerEventTypeEnum.contract_payout,
                LedgerEvent.src_account_id == escrow_acc.id,
                LedgerEvent.amount_currency == contract.currency,
                LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
            )
            escrowed_r = await session.execute(escrowed_q)
            paid_out_r = await session.execute(paid_out_q)
            escrowed_total: Decimal = escrowed_r.scalar_one()
            paid_out_total: Decimal = paid_out_r.scalar_one()

            refundable = escrowed_total - paid_out_total
            if refundable > 0:
                await append_event(
                    session,
                    LedgerEventTypeEnum.contract_payout,
                    contract.currency,
                    refundable,
                    src_account_id=escrow_acc.id,
                    dst_account_id=employer_acc.id,
                    metadata={
                        "type": "contract_refund",
                        "contract_id": str(contract.id),
                        "payment_model": contract.payment_model.value,
                    },
                )

    contract.status = ContractStatusEnum.cancelled
    await session.flush()
    await session.refresh(contract)
    try:
        await on_contract_cancelled(
            session,
            contract_id=contract.id,
            employer_agent_id=contract.employer_agent_id,
            worker_agent_id=contract.worker_agent_id,
        )
    except Exception:
        pass
    return _to_public(contract)


@router.post("/{contract_id}/complete", response_model=ContractPublic)
async def complete_contract(
    contract_id: UUID,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    contract = await _get_contract(session, contract_id)
    await _require_party(session, user_id, contract, employer=True, worker=False)
    if contract.status != ContractStatusEnum.active:
        raise HTTPException(status_code=400, detail="Only active contracts can be completed")

    # Payouts v1
    if contract.fixed_amount_value:
        worker_acc = await get_or_create_account(session, "agent", contract.worker_agent_id)

        if contract.payment_model == PaymentModelEnum.fixed:
            amount = Decimal(contract.fixed_amount_value)
            if amount > 0:
                escrow_acc = await get_or_create_account(session, "contract_escrow", contract.id)

                escrowed_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
                    LedgerEvent.type == LedgerEventTypeEnum.contract_escrow,
                    LedgerEvent.dst_account_id == escrow_acc.id,
                    LedgerEvent.amount_currency == contract.currency,
                    LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
                )
                paid_to_worker_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
                    LedgerEvent.type == LedgerEventTypeEnum.contract_payout,
                    LedgerEvent.dst_account_id == worker_acc.id,
                    LedgerEvent.amount_currency == contract.currency,
                    LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
                )
                paid_out_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
                    LedgerEvent.type == LedgerEventTypeEnum.contract_payout,
                    LedgerEvent.src_account_id == escrow_acc.id,
                    LedgerEvent.amount_currency == contract.currency,
                    LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
                )

                escrowed_r = await session.execute(escrowed_q)
                paid_to_worker_r = await session.execute(paid_to_worker_q)
                paid_out_r = await session.execute(paid_out_q)
                escrowed_total: Decimal = escrowed_r.scalar_one()
                already_paid_to_worker: Decimal = paid_to_worker_r.scalar_one()
                already_paid_out: Decimal = paid_out_r.scalar_one()

                available = escrowed_total - already_paid_out
                remaining_target = amount - already_paid_to_worker
                delta = min(available, remaining_target)
                if delta > 0:
                    await append_event(
                        session,
                        LedgerEventTypeEnum.contract_payout,
                        contract.currency,
                        delta,
                        src_account_id=escrow_acc.id,
                        dst_account_id=worker_acc.id,
                        metadata={
                            "type": "contract_payout",
                            "contract_id": str(contract.id),
                            "payment_model": contract.payment_model.value,
                        },
                    )

        elif contract.payment_model == PaymentModelEnum.per_run:
            # Per-run payouts are executed per succeeded run (in runs router) and are idempotent by (contract_id, run_id).
            pass

    contract.status = ContractStatusEnum.completed
    contract.updated_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(contract)
    try:
        await on_contract_completed(
            session,
            contract_id=contract.id,
            employer_agent_id=contract.employer_agent_id,
            worker_agent_id=contract.worker_agent_id,
        )
    except Exception:
        pass
    return _to_public(contract)


@router.post("/{contract_id}/dispute", response_model=ContractPublic)
async def dispute_contract(
    contract_id: UUID,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    contract = await _get_contract(session, contract_id)
    await _require_party(session, user_id, contract, employer=True, worker=True)
    if contract.status not in (ContractStatusEnum.active, ContractStatusEnum.completed):
        raise HTTPException(status_code=400, detail="Only active or completed contracts can be disputed")
    contract.status = ContractStatusEnum.disputed
    await session.flush()
    await session.refresh(contract)
    return _to_public(contract)


@router.get("", response_model=Pagination[ContractPublic])
async def list_contracts(
    session: DbSession,
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(None),
    employer_agent_id: UUID | None = Query(None),
    worker_agent_id: UUID | None = Query(None),
    status: ContractStatusEnum | None = Query(None),
):
    q = select(Contract).order_by(Contract.created_at.desc()).limit(limit + 1)
    if cursor:
        try:
            q = q.where(Contract.id < UUID(cursor))
        except ValueError:
            pass
    if employer_agent_id:
        q = q.where(Contract.employer_agent_id == employer_agent_id)
    if worker_agent_id:
        q = q.where(Contract.worker_agent_id == worker_agent_id)
    if status:
        q = q.where(Contract.status == status)
    r = await session.execute(q)
    rows = r.scalars().all()
    next_cursor = str(rows[-1].id) if len(rows) > limit else None
    items = rows[:limit]
    return Pagination(
        items=[_to_public(c) for c in items],
        next_cursor=next_cursor,
    )


@router.get("/{contract_id}", response_model=ContractPublic)
async def get_contract(contract_id: UUID, session: DbSession):
    contract = await _get_contract(session, contract_id)
    return _to_public(contract)


@router.get("/{contract_id}/payments")
async def get_contract_payments(contract_id: UUID, session: DbSession):
    contract = await _get_contract(session, contract_id)

    # MVP totals for fixed escrow contracts.
    if contract.payment_model != PaymentModelEnum.fixed or not contract.fixed_amount_value:
        return {
            "contract_id": str(contract.id),
            "currency": contract.currency,
            "escrowed_total": "0",
            "paid_total": "0",
            "pending_total": "0",
        }

    amount = Decimal(contract.fixed_amount_value)
    if amount <= 0:
        return {
            "contract_id": str(contract.id),
            "currency": contract.currency,
            "escrowed_total": "0",
            "paid_total": "0",
            "pending_total": "0",
        }

    escrow_acc = await get_or_create_account(session, "contract_escrow", contract.id)
    worker_acc = await get_or_create_account(session, "agent", contract.worker_agent_id)

    escrowed_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
        LedgerEvent.type == LedgerEventTypeEnum.contract_escrow,
        LedgerEvent.dst_account_id == escrow_acc.id,
        LedgerEvent.amount_currency == contract.currency,
        LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
    )
    paid_to_worker_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
        LedgerEvent.type == LedgerEventTypeEnum.contract_payout,
        LedgerEvent.dst_account_id == worker_acc.id,
        LedgerEvent.amount_currency == contract.currency,
        LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
    )
    paid_out_q = select(func.coalesce(func.sum(LedgerEvent.amount_value), 0)).where(
        LedgerEvent.type == LedgerEventTypeEnum.contract_payout,
        LedgerEvent.src_account_id == escrow_acc.id,
        LedgerEvent.amount_currency == contract.currency,
        LedgerEvent.metadata_.contains({"contract_id": str(contract.id)}),
    )
    escrowed_r = await session.execute(escrowed_q)
    paid_to_worker_r = await session.execute(paid_to_worker_q)
    paid_out_r = await session.execute(paid_out_q)
    escrowed_total: Decimal = escrowed_r.scalar_one()
    paid_total: Decimal = paid_to_worker_r.scalar_one()
    paid_out_total: Decimal = paid_out_r.scalar_one()

    pending_total = escrowed_total - paid_out_total
    if pending_total < 0:
        pending_total = Decimal(0)

    return {
        "contract_id": str(contract.id),
        "currency": contract.currency,
        "escrowed_total": str(escrowed_total),
        "paid_total": str(paid_total),
        "pending_total": str(pending_total),
    }


@router.get("/{contract_id}/runs", response_model=Pagination[dict])
async def list_contract_runs(
    contract_id: UUID,
    session: DbSession,
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(None),
):
    # Minimal run projection for contract detail UI.
    q = select(Run).where(Run.contract_id == contract_id).order_by(Run.created_at.desc()).limit(limit + 1)
    if cursor:
        try:
            q = q.where(Run.id < UUID(cursor))
        except ValueError:
            pass
    r = await session.execute(q)
    rows = r.scalars().all()
    next_cursor = str(rows[-1].id) if len(rows) > limit else None
    items = rows[:limit]
    return Pagination(
        items=[
            {
                "id": str(run.id),
                "strategy_version_id": str(run.strategy_version_id),
                "pool_id": str(run.pool_id),
                "state": run.state.value if hasattr(run.state, "value") else str(run.state),
                "created_at": run.created_at,
                "started_at": run.started_at,
                "ended_at": run.ended_at,
            }
            for run in items
        ],
        next_cursor=next_cursor,
    )


@router.get("/{contract_id}/activity")
async def get_contract_activity(contract_id: UUID, session: DbSession, limit: int = Query(200, ge=1, le=500)):
    contract = await _get_contract(session, contract_id)

    # Runs
    rr = await session.execute(
        select(Run).where(Run.contract_id == contract_id).order_by(Run.created_at.desc()).limit(limit)
    )
    runs = rr.scalars().all()

    # Ledger events linked by metadata.contract_id
    er = await session.execute(
        select(LedgerEvent)
        .where(LedgerEvent.metadata_.contains({"contract_id": str(contract_id)}))
        .order_by(LedgerEvent.ts.desc())
        .limit(limit)
    )
    events = er.scalars().all()

    items: list[dict] = []
    items.append(
        {
            "kind": "contract_created",
            "ts": contract.created_at,
            "data": {"status": contract.status.value},
        }
    )
    items.append(
        {
            "kind": "contract_status",
            "ts": contract.updated_at,
            "data": {"status": contract.status.value},
        }
    )
    for run in runs:
        items.append(
            {
                "kind": "run",
                "ts": run.created_at,
                "data": {
                    "run_id": str(run.id),
                    "state": run.state.value if hasattr(run.state, "value") else str(run.state),
                },
            }
        )
    for ev in events:
        items.append(
            {
                "kind": "ledger",
                "ts": ev.ts,
                "data": {
                    "event_id": str(ev.id),
                    "type": ev.type.value if hasattr(ev.type, "value") else str(ev.type),
                    "amount_value": str(ev.amount_value),
                    "amount_currency": ev.amount_currency,
                    "metadata": ev.metadata_ or {},
                },
            }
        )

    items.sort(key=lambda x: x.get("ts") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return {"contract_id": str(contract_id), "items": items[:limit]}

