from __future__ import annotations

import asyncio
import csv
import io
from datetime import datetime, UTC, timedelta
from uuid import UUID
from uuid import uuid4

import hashlib
import json
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import desc, select

from app.api.deps import DbSession, get_current_user_id, require_platform_admin
from app.services.idempotency import get_idempotency_hit, store_idempotency_result
from app.config import get_settings
from app.constants import PLATFORM_ACCOUNT_OWNER_ID
from app.db.models import ChainReceipt, LedgerEventTypeEnum, PaymentIntent, PaymentIntentStatusEnum, ReferralRewardEvent, SettlementIntent, User, WorkflowRunRecord
from app.schemas import (
    ChainReceiptPublic,
    Money,
    SettlementIntentPublic,
    WorkflowRunCreateRequest,
    WorkflowRunExecuteResponse,
    WorkflowBundleCheckoutRequest,
    WorkflowBundleCheckoutResponse,
    WorkflowBundlePublic,
    WorkflowBundlesResponse,
    WorkflowCreditPackagePublic,
    WorkflowCreditPackagesResponse,
    WorkflowCreditTopUpIntentConfirmRequest,
    WorkflowCreditTopUpIntentCreateRequest,
    WorkflowCreditTopUpIntentsResponse,
    WorkflowCreditTopUpIntentResponse,
    WorkflowRunPaymentConfirmRequest,
    WorkflowRunPaymentConfirmResponse,
    WorkflowRunPaymentIntentCreateRequest,
    WorkflowRunPaymentIntentCreateResponse,
    WorkflowRunPaymentIntentPublic,
    WorkflowRevenueCurrencyTotalPublic,
    WorkflowRevenueMoneyPublic,
    WorkflowRevenueSkuPublic,
    WorkflowRevenueSummaryPublic,
    WorkflowRunProofBundlePublic,
    WorkflowRunProofBundleSummaryPublic,
    WorkflowRunPublic,
    WorkflowRunReceiptPublic,
    WorkflowRunReceiptTrailPublic,
    WorkflowRunsResponse,
    WorkflowRunStatus,
    WorkflowRunStatusUpdateRequest,
    WorkflowRunStatusUpdateResponse,
    WorkflowTemplatePublic,
    WorkflowTemplatesResponse,
)
from app.services.ledger import append_event, balance_for_account, get_or_create_account, is_ledger_invariant_halted
from app.services.llm import execute_paid_workflow_with_llm
from app.services.mail import can_receive_system_email, send_email
from app.services.notifications import create_notification
from app.services.referrals import issue_referral_rewards_for_order
from app.services.settlements import build_correlation_id, execute_settlement_intent
from app.services.auth import decode_token
from app.services.pubsub import publish_workflow_run_event
from app.services.webhook_dispatcher import (
    emit_run_completed, emit_payment_captured, emit_payment_refunded,
    emit_receipt_ready, emit_user_registered,
)
from app.services.workflow_execution import (
    WORKFLOW_BUNDLES,
    WORKFLOW_CREDIT_PACKAGES,
    WORKFLOW_TEMPLATES,
    build_workflow_preview,
    build_workflow_result_shell,
    execute_workflow_template,
    find_credit_package,
    find_workflow_bundle,
    find_workflow_template,
    quote_bundle_amount,
    quote_credit_package_amount,
    quote_workflow_amount,
)

router = APIRouter(prefix="/workflow-store", tags=["Workflow Store"])


ALLOWED_TRANSITIONS: dict[WorkflowRunStatus, set[WorkflowRunStatus]] = {
    WorkflowRunStatus.quoted: {WorkflowRunStatus.paid, WorkflowRunStatus.cancelled},
    WorkflowRunStatus.paid: {WorkflowRunStatus.queued, WorkflowRunStatus.cancelled},
    WorkflowRunStatus.queued: {WorkflowRunStatus.running, WorkflowRunStatus.cancelled},
    WorkflowRunStatus.running: {WorkflowRunStatus.completed, WorkflowRunStatus.failed, WorkflowRunStatus.cancelled},
    WorkflowRunStatus.completed: set(),
    WorkflowRunStatus.failed: set(),
    WorkflowRunStatus.cancelled: set(),
}


def _serialize_run(row: WorkflowRunRecord) -> WorkflowRunPublic:
    receipt_json = row.receipt_json or {}
    quoted_price = receipt_json.get("quoted_price") or {
        "amount": str(row.quoted_amount),
        "currency": row.payment_currency,
    }
    # Phase 4: extract degraded signals from result_json
    result_json = row.result_json or {}
    degraded_run = bool(result_json.get("degraded_run", False)) if isinstance(result_json, dict) else False
    degraded_reason = result_json.get("degraded_reason") if isinstance(result_json, dict) else None
    return WorkflowRunPublic(
        id=str(row.id),
        workflow_slug=row.workflow_slug,
        title=row.title,
        category=row.category,
        status=WorkflowRunStatus(row.status),
        price=Money(amount=str(row.quoted_amount), currency=row.payment_currency),
        payment_currency=row.payment_currency,
        unlock_full_result=row.unlock_full_result,
        inputs=row.inputs_json or {},
        preview=row.preview_json or {},
        result=row.result_json,
        receipt=WorkflowRunReceiptPublic(
            workflow_slug=row.workflow_slug,
            payment_currency=row.payment_currency,
            quoted_price=Money(
                amount=str(quoted_price.get("amount", row.quoted_amount)),
                currency=str(quoted_price.get("currency", row.payment_currency)),
            ),
            status=str(receipt_json.get("status", row.status)),
            receipt_items=list(receipt_json.get("receipt_items", [])),
            proof=receipt_json.get("proof", {}),
        ),
        created_at=row.created_at,
        owner_user_id=str(row.owner_user_id),
        degraded_run=degraded_run,
        degraded_reason=degraded_reason,
    )


def _serialize_payment_intent(row: PaymentIntent) -> WorkflowRunPaymentIntentPublic:
    return WorkflowRunPaymentIntentPublic(
        id=str(row.id),
        workflow_run_id=str(row.workflow_run_id) if row.workflow_run_id else None,
        owner_user_id=str(row.owner_user_id),
        intent_type=row.intent_type,
        status=row.status,
        payment_method=row.payment_method,
        amount=Money(amount=str(row.amount_value), currency=row.amount_currency),
        payment_reference=row.payment_reference,
        reserved_ledger_event_id=str(row.reserved_ledger_event_id) if row.reserved_ledger_event_id else None,
        capture_ledger_event_id=str(row.capture_ledger_event_id) if row.capture_ledger_event_id else None,
        refund_ledger_event_id=str(row.refund_ledger_event_id) if row.refund_ledger_event_id else None,
        provider_payload=row.provider_payload_json or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _parse_run_id(run_id: str) -> str:
    try:
        return str(UUID(run_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Workflow run not found")


async def _get_owned_run(session: DbSession, user_id: str, run_id: str) -> WorkflowRunRecord:
    parsed_id = _parse_run_id(run_id)
    q = select(WorkflowRunRecord).where(
        WorkflowRunRecord.id == parsed_id,
        WorkflowRunRecord.owner_user_id == user_id,
    )
    r = await session.execute(q)
    row = r.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return row


def _append_status_transition(row: WorkflowRunRecord, from_status: WorkflowRunStatus | None, to_status: WorkflowRunStatus) -> None:
    receipt_json = dict(row.receipt_json or {})
    proof = dict(receipt_json.get("proof", {}))
    status_timeline = list(proof.get("status_timeline", []))
    transition = {
        "from": from_status.value if from_status else None,
        "to": to_status.value,
        "changed_at": datetime.now(UTC).isoformat(),
    }
    status_timeline.append(transition)
    proof["status_timeline"] = status_timeline
    proof["last_status_change"] = transition
    receipt_json["status"] = to_status.value
    receipt_json["proof"] = proof
    row.status = to_status.value
    row.receipt_json = receipt_json
    row.updated_at = datetime.now(UTC)


async def _append_status_transition_and_broadcast(
    row: WorkflowRunRecord,
    from_status: WorkflowRunStatus | None,
    to_status: WorkflowRunStatus,
) -> None:
    _append_status_transition(row, from_status, to_status)
    await publish_workflow_run_event(
        run_id=row.id,
        event_type=f"status_change.{to_status.value}",
        data={
            "workflow_run_id": str(row.id),
            "workflow_slug": row.workflow_slug,
            "title": row.title,
            "status": to_status.value,
            "previous_status": from_status.value if from_status else None,
            "receipt_ready": to_status in {WorkflowRunStatus.completed, WorkflowRunStatus.failed, WorkflowRunStatus.cancelled},
        },
    )


def _set_receipt_payment_intent_proof(
    row: WorkflowRunRecord,
    intent: PaymentIntent,
    *,
    proof_status: str,
    ledger_event_id: str | None = None,
    note: str | None = None,
) -> None:
    receipt_json = dict(row.receipt_json or {})
    proof = dict(receipt_json.get("proof", {}))
    payment_intents = list(proof.get("payment_intents", [])) if isinstance(proof.get("payment_intents"), list) else []
    event = {
        "payment_intent_id": str(intent.id),
        "status": proof_status,
        "payment_method": intent.payment_method,
        "amount": {"amount": str(intent.amount_value), "currency": intent.amount_currency},
        "ledger_event_id": ledger_event_id,
        "changed_at": datetime.now(UTC).isoformat(),
    }
    if note:
        event["note"] = note
    payment_intents.append(event)
    proof["payment_intent_id"] = str(intent.id)
    proof["payment_intent_status"] = proof_status
    proof["payment_intents"] = payment_intents
    proof["payment_confirmation"] = {
        "reference": intent.payment_reference or f"{intent.payment_method}:{intent.id}",
        "method": intent.payment_method,
        "confirmed_at": datetime.now(UTC).isoformat(),
        "note": note,
        "payment_amount": {"amount": str(intent.amount_value), "currency": intent.amount_currency},
    }
    proof["settlement_status"] = proof_status
    receipt_json["proof"] = proof
    row.receipt_json = receipt_json
    row.updated_at = datetime.now(UTC)


async def _latest_payment_intent(
    session: DbSession,
    row: WorkflowRunRecord,
    statuses: set[str] | None = None,
) -> PaymentIntent | None:
    q = (
        select(PaymentIntent)
        .where(PaymentIntent.workflow_run_id == row.id)
        .order_by(desc(PaymentIntent.created_at))
        .limit(1)
    )
    if statuses:
        q = q.where(PaymentIntent.status.in_(statuses))
    return (await session.execute(q)).scalar_one_or_none()


async def _capture_reserved_workflow_payment(session: DbSession, row: WorkflowRunRecord) -> PaymentIntent | None:
    intent = await _latest_payment_intent(session, row, {PaymentIntentStatusEnum.reserved.value})
    if intent is None or intent.capture_ledger_event_id:
        return intent

    from app.services.market_economy import workflow_platform_fee_percent

    escrow_acc = await get_or_create_account(session, "workflow_run", UUID(str(row.id)))
    platform_acc = await get_or_create_account(session, "system", PLATFORM_ACCOUNT_OWNER_ID)
    gross = Decimal(intent.amount_value)
    fee_pct = workflow_platform_fee_percent()
    platform_fee = (gross * fee_pct / Decimal("100")).quantize(Decimal("0.00000001"))
    operator_share = (gross - platform_fee).quantize(Decimal("0.00000001"))

    # Single ledger move of gross → platform; fee split is recorded in metadata for treasury.
    ev = await append_event(
        session,
        LedgerEventTypeEnum.fee,
        intent.amount_currency,
        gross,
        src_account_id=escrow_acc.id,
        dst_account_id=platform_acc.id,
        metadata={
            "type": "workflow_payment_capture",
            "payment_intent_id": str(intent.id),
            "workflow_run_id": str(row.id),
            "workflow_slug": row.workflow_slug,
            "platform_fee_percent": str(fee_pct),
            "platform_fee_amount": str(platform_fee),
            "operator_share_amount": str(operator_share),
            "gross_amount": str(gross),
        },
    )
    intent.status = PaymentIntentStatusEnum.captured.value
    intent.capture_ledger_event_id = ev.id
    intent.updated_at = datetime.now(UTC)
    intent.provider_payload_json = {
        **(intent.provider_payload_json or {}),
        "platform_fee_percent": str(fee_pct),
        "platform_fee_amount": str(platform_fee),
        "operator_share_amount": str(operator_share),
    }
    referral_result: dict[str, str] | None = None
    try:
        referral_result = await issue_referral_rewards_for_order(
            session,
            order_id=UUID(str(row.id)),
            buyer_type="user",
            buyer_id=UUID(str(row.owner_user_id)),
            amount_currency=intent.amount_currency,
            amount_value=Decimal(intent.amount_value),
        )
    except Exception as exc:
        referral_result = {
            "status": "skipped",
            "reason": "workflow_referral_reward_error",
            "error": str(exc)[:240],
        }
    if referral_result is not None:
        intent.provider_payload_json = {
            **(intent.provider_payload_json or {}),
            "referral_rewards": referral_result,
        }
    _set_receipt_payment_intent_proof(
        row,
        intent,
        proof_status="captured",
        ledger_event_id=str(ev.id),
        note=f"Workflow payment captured (platform fee {fee_pct}%).",
    )
    if referral_result is not None:
        receipt_json = row.receipt_json or {}
        proof = receipt_json.get("proof") or {}
        proof["referral_rewards"] = referral_result
        proof["platform_fee"] = {
            "percent": str(fee_pct),
            "amount": str(platform_fee),
            "currency": intent.amount_currency,
            "operator_share": str(operator_share),
        }
        receipt_json["proof"] = proof
        row.receipt_json = receipt_json
    else:
        receipt_json = row.receipt_json or {}
        proof = receipt_json.get("proof") or {}
        proof["platform_fee"] = {
            "percent": str(fee_pct),
            "amount": str(platform_fee),
            "currency": intent.amount_currency,
            "operator_share": str(operator_share),
        }
        receipt_json["proof"] = proof
        row.receipt_json = receipt_json
    return intent


async def _refund_reserved_workflow_payment(session: DbSession, row: WorkflowRunRecord, reason: str) -> PaymentIntent | None:
    intent = await _latest_payment_intent(session, row, {PaymentIntentStatusEnum.reserved.value})
    if intent is None or intent.refund_ledger_event_id:
        return intent

    escrow_acc = await get_or_create_account(session, "workflow_run", UUID(str(row.id)))
    user_acc = await get_or_create_account(session, "user", UUID(str(row.owner_user_id)))
    ev = await append_event(
        session,
        LedgerEventTypeEnum.refund,
        intent.amount_currency,
        Decimal(intent.amount_value),
        src_account_id=escrow_acc.id,
        dst_account_id=user_acc.id,
        metadata={
            "type": "workflow_payment_refund",
            "payment_intent_id": str(intent.id),
            "workflow_run_id": str(row.id),
            "workflow_slug": row.workflow_slug,
            "reason": reason,
        },
    )
    intent.status = PaymentIntentStatusEnum.refunded.value
    intent.refund_ledger_event_id = ev.id
    intent.updated_at = datetime.now(UTC)
    _set_receipt_payment_intent_proof(row, intent, proof_status="refunded", ledger_event_id=str(ev.id), note=reason)
    return intent


async def _reserve_workflow_run_credits(
    session: DbSession,
    row: WorkflowRunRecord,
    *,
    note: str | None = None,
    payment_reference: str | None = None,
    provider_payload: dict | None = None,
) -> PaymentIntent:
    amount_value = Decimal(row.quoted_amount)
    if amount_value <= 0:
        raise HTTPException(status_code=400, detail="Workflow run quote must be positive")

    user_acc = await get_or_create_account(session, "user", UUID(str(row.owner_user_id)))
    balances = await balance_for_account(session, user_acc.id, row.payment_currency)
    available = balances.get(row.payment_currency) or Decimal(0)
    if available < amount_value:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Insufficient credits for workflow payment",
                "currency": row.payment_currency,
                "required": str(amount_value),
                "available": str(available),
            },
        )

    intent = PaymentIntent(
        owner_user_id=UUID(str(row.owner_user_id)),
        workflow_run_id=UUID(str(row.id)),
        intent_type="workflow_run",
        status=PaymentIntentStatusEnum.requires_payment.value,
        payment_method="credits",
        amount_currency=row.payment_currency,
        amount_value=amount_value,
        payment_reference=payment_reference,
        provider_payload_json={"note": note, "mode": "ledger_credits", **(provider_payload or {})},
    )
    session.add(intent)
    await session.flush()

    escrow_acc = await get_or_create_account(session, "workflow_run", UUID(str(row.id)))
    ev = await append_event(
        session,
        LedgerEventTypeEnum.transfer,
        row.payment_currency,
        amount_value,
        src_account_id=user_acc.id,
        dst_account_id=escrow_acc.id,
        metadata={
            "type": "workflow_payment_reserve",
            "payment_intent_id": str(intent.id),
            "workflow_run_id": str(row.id),
            "workflow_slug": row.workflow_slug,
            **(provider_payload or {}),
        },
    )
    intent.status = PaymentIntentStatusEnum.reserved.value
    intent.payment_reference = payment_reference or f"credits:{intent.id}"
    intent.reserved_ledger_event_id = ev.id
    intent.provider_payload_json = {
        **(intent.provider_payload_json or {}),
        "reserved_ledger_event_id": str(ev.id),
        "reserved_at": datetime.now(UTC).isoformat(),
    }
    intent.updated_at = datetime.now(UTC)
    _set_receipt_payment_intent_proof(row, intent, proof_status="reserved", ledger_event_id=str(ev.id), note=note or "Credits reserved for workflow execution.")
    if WorkflowRunStatus(row.status) == WorkflowRunStatus.quoted:
        _append_status_transition(row, WorkflowRunStatus.quoted, WorkflowRunStatus.paid)
    await session.flush()
    await session.refresh(intent)
    await session.refresh(row)
    return intent


def _intent_public(row: SettlementIntent) -> SettlementIntentPublic:
    return SettlementIntentPublic(
        id=str(row.id),
        intent_type=row.intent_type,
        source_owner_type=row.source_owner_type,
        source_owner_id=str(row.source_owner_id),
        target_owner_type=row.target_owner_type,
        target_owner_id=str(row.target_owner_id),
        amount_currency=row.amount_currency,
        amount_value=str(row.amount_value),
        status=row.status,
        correlation_id=row.correlation_id,
        metadata_json=row.metadata_json,
        error_message=row.error_message,
        executed_at=row.executed_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _chain_receipt_public(row: ChainReceipt) -> ChainReceiptPublic:
    return ChainReceiptPublic(
        id=str(row.id),
        settlement_intent_id=str(row.settlement_intent_id),
        chain_id=row.chain_id,
        tx_hash=row.tx_hash,
        node_signature=row.node_signature,
        node_public_key=row.node_public_key,
        status=row.status,
        correlation_id=row.correlation_id,
        payload_hash=row.payload_hash,
        receipt_json=row.receipt_json,
        error_message=row.error_message,
        finalized_at=row.finalized_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _build_workflow_run_proof_bundle(
    row: WorkflowRunRecord,
    settlement_intent: SettlementIntent | None,
    receipts: list[ChainReceipt],
) -> WorkflowRunProofBundlePublic:
    run_public = _serialize_run(row)
    receipt_json = row.receipt_json or {}
    proof = dict(receipt_json.get("proof", {})) if isinstance(receipt_json, dict) else {}
    chain_receipts_public = [_chain_receipt_public(item) for item in receipts]
    receipt_items = list(receipt_json.get("receipt_items", [])) if isinstance(receipt_json, dict) else []
    payment_confirmation = proof.get("payment_confirmation") if isinstance(proof.get("payment_confirmation"), dict) else None
    execution = {
        "mode": proof.get("execution_mode"),
        "executed_at": proof.get("executed_at"),
        "template_title": proof.get("template_title"),
        "artifact_kind": proof.get("artifact_kind"),
        "sections_generated": proof.get("sections_generated"),
    }
    status_timeline = list(proof.get("status_timeline", [])) if isinstance(proof.get("status_timeline"), list) else []
    finalized_receipt_count = sum(1 for item in chain_receipts_public if item.status == "finalized")
    failed_receipt_count = sum(1 for item in chain_receipts_public if item.status == "failed")
    submitted_receipt_count = sum(1 for item in chain_receipts_public if item.status == "submitted")
    latest_chain_receipt_status = chain_receipts_public[0].status if chain_receipts_public else None
    generated_at = datetime.now(UTC)
    settlement_intent_public = _intent_public(settlement_intent) if settlement_intent else None
    summary = WorkflowRunProofBundleSummaryPublic(
        payment_confirmed=payment_confirmation is not None,
        settlement_status=str(proof.get("settlement_status")) if proof.get("settlement_status") is not None else None,
        chain_receipt_count=len(chain_receipts_public),
        finalized_receipt_count=finalized_receipt_count,
        failed_receipt_count=failed_receipt_count,
        submitted_receipt_count=submitted_receipt_count,
        execution_mode=str(proof.get("execution_mode")) if proof.get("execution_mode") is not None else None,
        executed_at=run_public.receipt.proof.get("executed_at"),
        latest_chain_receipt_status=latest_chain_receipt_status,
    )
    bundle_payload = {
        "bundle_version": "workflow-run-proof-bundle/v1",
        "workflow_run_id": str(row.id),
        "run": run_public.model_dump(mode="json"),
        "receipt_items": receipt_items,
        "payment_confirmation": payment_confirmation,
        "execution": execution,
        "settlement_intent": settlement_intent_public.model_dump(mode="json") if settlement_intent_public else None,
        "chain_receipts": [item.model_dump(mode="json") for item in chain_receipts_public],
        "status_timeline": status_timeline,
        "summary": summary.model_dump(mode="json"),
    }
    proof_hash = hashlib.sha256(
        json.dumps(bundle_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return WorkflowRunProofBundlePublic(
        generated_at=generated_at,
        workflow_run_id=str(row.id),
        proof_hash=proof_hash,
        run=run_public,
        receipt_items=receipt_items,
        payment_confirmation=payment_confirmation,
        execution=execution,
        settlement_intent=settlement_intent_public,
        chain_receipts=chain_receipts_public,
        status_timeline=status_timeline,
        summary=summary,
    )


def _resolved_payment_amount(row: WorkflowRunRecord, body: WorkflowRunPaymentConfirmRequest) -> dict[str, str]:
    if body.payment_amount:
        return {
            "amount": str(body.payment_amount.amount),
            "currency": str(body.payment_amount.currency),
        }
    return {
        "amount": str(row.quoted_amount),
        "currency": row.payment_currency,
    }


def _payment_confirmation_matches(existing: dict | None, body: WorkflowRunPaymentConfirmRequest, payment_amount: dict[str, str]) -> bool:
    if not isinstance(existing, dict):
        return False
    existing_amount = existing.get("payment_amount") if isinstance(existing.get("payment_amount"), dict) else {}
    return (
        str(existing.get("reference") or "") == body.payment_reference
        and str(existing.get("method") or "manual") == (body.payment_method or "manual")
        and str(existing.get("note") or "") == str(body.note or "")
        and str(existing_amount.get("amount") or "") == str(payment_amount.get("amount") or "")
        and str(existing_amount.get("currency") or "") == str(payment_amount.get("currency") or "")
    )


async def _get_settlement_intent_by_correlation_id(session: DbSession, correlation_id: str) -> SettlementIntent | None:
    return (
        await session.execute(
            select(SettlementIntent).where(SettlementIntent.correlation_id == correlation_id).limit(1)
        )
    ).scalar_one_or_none()


def _build_workflow_run_record(
    *,
    owner_user_id: str,
    template: WorkflowTemplatePublic,
    payment_currency: str,
    unlock_full_result: bool,
    inputs: dict,
    repeated_from_run_id: str | None = None,
    repeated_from_status: str | None = None,
) -> WorkflowRunRecord:
    from app.services.market_economy import quote_catalog_acp

    quoted_amount, usd_sticker, oracle_spot = quote_catalog_acp(
        template.price.amount,
        payment_currency=payment_currency,
    )
    created_at = datetime.now(UTC)
    estimated_provider_cost = (quoted_amount * Decimal("0.18")).quantize(Decimal("0.01"))
    estimated_margin = (quoted_amount - estimated_provider_cost).quantize(Decimal("0.01"))
    proof: dict[str, object] = {
        "pricing_basis": template.price.model_dump(),
        "usd_sticker": {"amount": str(usd_sticker), "currency": "USD"},
        "oracle_wacp_usd": format(oracle_spot, "f"),
        "accepted_currencies": template.accepted_currencies,
        "billing_mode": "market_aligned_quote",
        "template_slug": template.slug,
        "provider_cost_estimate": {
            "amount": str(estimated_provider_cost),
            "currency": payment_currency,
            "basis": "default 18% fulfillment reserve until provider costs are connected",
        },
        "margin_snapshot": {
            "gross": {"amount": str(quoted_amount), "currency": payment_currency},
            "estimated_cost": {"amount": str(estimated_provider_cost), "currency": payment_currency},
            "estimated_margin": {"amount": str(estimated_margin), "currency": payment_currency},
            "usd_sticker": {"amount": str(usd_sticker), "currency": "USD"},
            "oracle_wacp_usd": format(oracle_spot, "f"),
        },
        "status_timeline": [
            {
                "from": None,
                "to": WorkflowRunStatus.quoted.value,
                "changed_at": created_at.isoformat(),
            }
        ],
    }
    if repeated_from_run_id:
        proof["repeated_from_run_id"] = repeated_from_run_id
        proof["repeated_from_status"] = repeated_from_status
        proof["repeat_created_at"] = created_at.isoformat()

    receipt_json = {
        "workflow_slug": template.slug,
        "payment_currency": payment_currency,
        "quoted_price": {
            "amount": str(quoted_amount),
            "currency": payment_currency,
        },
        "usd_sticker": {"amount": str(usd_sticker), "currency": "USD"},
        "oracle_wacp_usd": format(oracle_spot, "f"),
        "status": WorkflowRunStatus.quoted.value,
        "receipt_items": template.receipt_items,
        "proof": proof,
    }

    return WorkflowRunRecord(
        owner_user_id=owner_user_id,
        workflow_slug=template.slug,
        title=template.title,
        category=template.category,
        status=WorkflowRunStatus.quoted.value,
        quoted_amount=quoted_amount,
        quoted_currency=template.price.currency,
        payment_currency=payment_currency,
        unlock_full_result=unlock_full_result,
        inputs_json=inputs,
        preview_json=build_workflow_preview(template),
        result_json=build_workflow_result_shell(template) if unlock_full_result else None,
        receipt_json=receipt_json,
        created_at=created_at,
        updated_at=created_at,
    )


def _allocate_bundle_run_amounts(
    templates: list[WorkflowTemplatePublic],
    *,
    payment_currency: str,
    bundle_total: Decimal,
) -> list[tuple[WorkflowTemplatePublic, Decimal, Decimal]]:
    original_amounts = [quote_workflow_amount(template, payment_currency) for template in templates]
    original_total = sum(original_amounts, Decimal(0))
    if original_total <= 0:
        raise HTTPException(status_code=400, detail="Bundle original total must be positive")

    allocated: list[tuple[WorkflowTemplatePublic, Decimal, Decimal]] = []
    distributed = Decimal(0)
    for idx, template in enumerate(templates):
        original = original_amounts[idx]
        if idx == len(templates) - 1:
            amount = (bundle_total - distributed).quantize(Decimal("0.01"))
        else:
            amount = (bundle_total * original / original_total).quantize(Decimal("0.01"))
            distributed += amount
        allocated.append((template, original, amount))
    return allocated


def _apply_bundle_pricing_to_run(
    row: WorkflowRunRecord,
    *,
    bundle: WorkflowBundlePublic,
    bundle_checkout_id: str,
    original_amount: Decimal,
    allocated_amount: Decimal,
    original_total: Decimal,
    bundle_total: Decimal,
    bundle_index: int,
) -> None:
    receipt_json = dict(row.receipt_json or {})
    proof = dict(receipt_json.get("proof", {}))
    row.quoted_amount = allocated_amount
    receipt_json["quoted_price"] = {"amount": str(allocated_amount), "currency": row.payment_currency}
    proof["billing_mode"] = "bundle_quote"
    proof["bundle_slug"] = bundle.slug
    proof["bundle_title"] = bundle.title
    proof["bundle_checkout_id"] = bundle_checkout_id
    proof["bundle_index"] = bundle_index
    proof["bundle_discount_percent"] = bundle.discount_percent
    proof["bundle_original_run_price"] = {"amount": str(original_amount), "currency": row.payment_currency}
    proof["bundle_original_total"] = {"amount": str(original_total), "currency": row.payment_currency}
    proof["bundle_total"] = {"amount": str(bundle_total), "currency": row.payment_currency}
    proof["bundle_allocated_price"] = {"amount": str(allocated_amount), "currency": row.payment_currency}
    receipt_json["proof"] = proof
    row.receipt_json = receipt_json
    row.updated_at = datetime.now(UTC)


@router.get("/templates", response_model=WorkflowTemplatesResponse)
async def list_workflow_templates(
    category: str | None = Query(None),
    q: str | None = Query(None),
):
    from app.services.market_economy import get_wacp_usd_oracle, quote_catalog_acp

    spot, _src = await get_wacp_usd_oracle()
    items = WORKFLOW_TEMPLATES
    if category:
        category_l = category.strip().lower()
        items = [item for item in items if item.category.lower() == category_l]
    if q:
        ql = q.strip().lower()
        items = [
            item
            for item in items
            if ql in item.slug.lower()
            or ql in item.title.lower()
            or ql in item.summary.lower()
            or any(ql in tag.lower() for tag in item.tags)
        ]
    enriched: list[WorkflowTemplatePublic] = []
    for item in items:
        acp, sticker, _ = quote_catalog_acp(item.price.amount, wacp_usd=spot)
        enriched.append(
            item.model_copy(
                update={
                    "usd_sticker": Money(amount=str(sticker), currency="USD"),
                    "price_acp": Money(amount=str(acp), currency="ACP"),
                    "oracle_wacp_usd": format(spot, "f"),
                    "price": Money(amount=str(acp), currency="ACP"),
                }
            )
        )
    return WorkflowTemplatesResponse(items=enriched)


@router.get("/templates/{workflow_slug}", response_model=WorkflowTemplatePublic)
async def get_workflow_template(workflow_slug: str):
    from app.services.market_economy import get_wacp_usd_oracle, quote_catalog_acp

    item = find_workflow_template(workflow_slug)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    spot, _src = await get_wacp_usd_oracle()
    acp, sticker, _ = quote_catalog_acp(item.price.amount, wacp_usd=spot)
    return item.model_copy(
        update={
            "usd_sticker": Money(amount=str(sticker), currency="USD"),
            "price_acp": Money(amount=str(acp), currency="ACP"),
            "oracle_wacp_usd": format(spot, "f"),
            "price": Money(amount=str(acp), currency="ACP"),
        }
    )


@router.get("/bundles", response_model=WorkflowBundlesResponse)
async def list_workflow_bundles():
    from app.services.market_economy import get_wacp_usd_oracle, quote_catalog_acp

    spot, _src = await get_wacp_usd_oracle()
    enriched: list[WorkflowBundlePublic] = []
    for item in WORKFLOW_BUNDLES:
        acp, sticker, _ = quote_catalog_acp(item.price.amount, wacp_usd=spot)
        enriched.append(
            item.model_copy(
                update={
                    "usd_sticker": Money(amount=str(sticker), currency="USD"),
                    "price_acp": Money(amount=str(acp), currency="ACP"),
                    "oracle_wacp_usd": format(spot, "f"),
                    "price": Money(amount=str(acp), currency="ACP"),
                }
            )
        )
    return WorkflowBundlesResponse(items=enriched)


@router.get("/bundles/{bundle_slug}", response_model=WorkflowBundlePublic)
async def get_workflow_bundle(bundle_slug: str):
    from app.services.market_economy import get_wacp_usd_oracle, quote_catalog_acp

    item = find_workflow_bundle(bundle_slug)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow bundle not found")
    spot, _src = await get_wacp_usd_oracle()
    acp, sticker, _ = quote_catalog_acp(item.price.amount, wacp_usd=spot)
    return item.model_copy(
        update={
            "usd_sticker": Money(amount=str(sticker), currency="USD"),
            "price_acp": Money(amount=str(acp), currency="ACP"),
            "oracle_wacp_usd": format(spot, "f"),
            "price": Money(amount=str(acp), currency="ACP"),
        }
    )


@router.get("/credit-packages", response_model=WorkflowCreditPackagesResponse)
async def list_workflow_credit_packages():
    return WorkflowCreditPackagesResponse(items=WORKFLOW_CREDIT_PACKAGES)


@router.get("/credit-packages/{package_slug}", response_model=WorkflowCreditPackagePublic)
async def get_workflow_credit_package(package_slug: str):
    item = find_credit_package(package_slug)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Credit package not found")


@router.post("/credit-packages/{package_slug}/top-up-intents", response_model=WorkflowCreditTopUpIntentResponse, status_code=201)
async def create_credit_top_up_intent(
    package_slug: str,
    body: WorkflowCreditTopUpIntentCreateRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    package = find_credit_package(package_slug)
    if package is None:
        raise HTTPException(status_code=404, detail="Credit package not found")
    if body.payment_currency not in package.accepted_currencies:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported payment currency for credit package",
                "accepted_currencies": package.accepted_currencies,
            },
        )

    quoted_amount = quote_credit_package_amount(package, body.payment_currency)
    intent = PaymentIntent(
        owner_user_id=UUID(user_id),
        workflow_run_id=None,
        intent_type="credit_topup",
        status=PaymentIntentStatusEnum.requires_payment.value,
        payment_method=(body.payment_method or "manual").strip().lower(),
        amount_currency=body.payment_currency,
        amount_value=quoted_amount,
        payment_reference=f"topup:{package.slug}:{uuid4().hex[:12]}",
        provider_payload_json={
            "package_slug": package.slug,
            "package_title": package.title,
            "credit_amount": package.credit_amount.model_dump(),
            "price": {"amount": str(quoted_amount), "currency": body.payment_currency},
            "note": body.note,
            "mode": "manual_topup_invoice",
        },
    )
    session.add(intent)
    await session.flush()
    await session.refresh(intent)
    return WorkflowCreditTopUpIntentResponse(
        item=_serialize_payment_intent(intent),
        package=package,
        credited=False,
    )


def _package_for_top_up_intent(intent: PaymentIntent) -> WorkflowCreditPackagePublic:
    package_slug = str((intent.provider_payload_json or {}).get("package_slug") or "")
    package = find_credit_package(package_slug)
    if package is None:
        raise HTTPException(status_code=400, detail="Credit package metadata is invalid")
    return package


async def _capture_credit_top_up_intent(
    session: DbSession,
    intent: PaymentIntent,
    package: WorkflowCreditPackagePublic,
    body: WorkflowCreditTopUpIntentConfirmRequest,
    *,
    approved_by_user_id: str | None = None,
) -> WorkflowCreditTopUpIntentResponse:
    if await is_ledger_invariant_halted(session):
        raise HTTPException(status_code=503, detail="Ledger invariant violated; operations temporarily blocked")

    if intent.status == PaymentIntentStatusEnum.captured.value and intent.capture_ledger_event_id:
        return WorkflowCreditTopUpIntentResponse(
            item=_serialize_payment_intent(intent),
            package=package,
            credited=True,
        )
    if intent.status != PaymentIntentStatusEnum.requires_payment.value:
        raise HTTPException(status_code=400, detail="Top-up intent is not confirmable")

    user_acc = await get_or_create_account(session, "user", UUID(str(intent.owner_user_id)))
    credit_amount = Decimal(package.credit_amount.amount)
    ev = await append_event(
        session,
        LedgerEventTypeEnum.deposit,
        package.credit_amount.currency,
        credit_amount,
        dst_account_id=user_acc.id,
        metadata={
            "type": "credit_package_topup",
            "payment_intent_id": str(intent.id),
            "package_slug": package.slug,
            "package_title": package.title,
            "payment_amount": str(intent.amount_value),
            "payment_currency": intent.amount_currency,
            "payment_reference": body.payment_reference,
            "note": body.note,
            "approved_by_user_id": approved_by_user_id,
        },
    )
    intent.status = PaymentIntentStatusEnum.captured.value
    intent.payment_reference = body.payment_reference
    intent.capture_ledger_event_id = ev.id
    intent.provider_payload_json = {
        **(intent.provider_payload_json or {}),
        "confirmed_at": datetime.now(UTC).isoformat(),
        "confirmed_reference": body.payment_reference,
        "confirm_note": body.note,
        "credited_ledger_event_id": str(ev.id),
        "approved_by_user_id": approved_by_user_id,
    }
    intent.updated_at = datetime.now(UTC)
    await session.flush()
    await session.refresh(intent)
    return WorkflowCreditTopUpIntentResponse(
        item=_serialize_payment_intent(intent),
        package=package,
        credited=True,
    )


@router.get("/admin/top-up-intents", response_model=WorkflowCreditTopUpIntentsResponse)
async def list_admin_credit_top_up_intents(
    session: DbSession,
    admin_user_id: str = Depends(require_platform_admin),
    status: str | None = Query(PaymentIntentStatusEnum.requires_payment.value),
    limit: int = Query(50, ge=1, le=200),
):
    q = (
        select(PaymentIntent)
        .where(PaymentIntent.intent_type == "credit_topup")
        .order_by(desc(PaymentIntent.created_at))
        .limit(limit)
    )
    if status:
        q = q.where(PaymentIntent.status == status)
    rows = (await session.execute(q)).scalars().all()
    items: list[WorkflowCreditTopUpIntentResponse] = []
    for intent in rows:
        package = _package_for_top_up_intent(intent)
        items.append(
            WorkflowCreditTopUpIntentResponse(
                item=_serialize_payment_intent(intent),
                package=package,
                credited=intent.status == PaymentIntentStatusEnum.captured.value,
            )
        )
    return WorkflowCreditTopUpIntentsResponse(items=items)


@router.post("/admin/top-up-intents/{intent_id}/confirm", response_model=WorkflowCreditTopUpIntentResponse)
async def admin_confirm_credit_top_up_intent(
    intent_id: str,
    body: WorkflowCreditTopUpIntentConfirmRequest,
    session: DbSession,
    admin_user_id: str = Depends(require_platform_admin),
):
    try:
        parsed_intent_id = UUID(intent_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Top-up intent not found")

    intent = (
        await session.execute(
            select(PaymentIntent).where(
                PaymentIntent.id == parsed_intent_id,
                PaymentIntent.intent_type == "credit_topup",
            ).limit(1)
        )
    ).scalar_one_or_none()
    if intent is None:
        raise HTTPException(status_code=404, detail="Top-up intent not found")
    package = _package_for_top_up_intent(intent)
    return await _capture_credit_top_up_intent(
        session,
        intent,
        package,
        body,
        approved_by_user_id=admin_user_id,
    )


@router.post("/top-up-intents/{intent_id}/confirm", response_model=WorkflowCreditTopUpIntentResponse)
async def confirm_credit_top_up_intent(
    intent_id: str,
    body: WorkflowCreditTopUpIntentConfirmRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    raise HTTPException(status_code=403, detail="Top-up confirmation requires admin approval")


@router.post("/bundles/{bundle_slug}/checkout", response_model=WorkflowBundleCheckoutResponse, status_code=201)
async def checkout_workflow_bundle(
    bundle_slug: str,
    body: WorkflowBundleCheckoutRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if await is_ledger_invariant_halted(session):
        raise HTTPException(status_code=503, detail="Ledger invariant violated; operations temporarily blocked")

    bundle = find_workflow_bundle(bundle_slug)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Workflow bundle not found")
    if body.payment_currency not in bundle.accepted_currencies:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported payment currency for workflow bundle",
                "accepted_currencies": bundle.accepted_currencies,
            },
        )

    templates: list[WorkflowTemplatePublic] = []
    for workflow_slug in bundle.workflow_slugs:
        template = find_workflow_template(workflow_slug)
        if template is None:
            raise HTTPException(status_code=500, detail=f"Workflow bundle template missing: {workflow_slug}")
        if body.payment_currency not in template.accepted_currencies:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Unsupported payment currency for workflow in bundle",
                    "workflow_slug": workflow_slug,
                    "accepted_currencies": template.accepted_currencies,
                },
            )
        templates.append(template)

    bundle_total = quote_bundle_amount(bundle, body.payment_currency)
    original_total = sum((quote_workflow_amount(template, body.payment_currency) for template in templates), Decimal(0)).quantize(Decimal("0.01"))
    allocations = _allocate_bundle_run_amounts(templates, payment_currency=body.payment_currency, bundle_total=bundle_total)
    payment_method = (body.payment_method or "credits").strip().lower()

    if body.reserve_credits and payment_method not in {"credits", "ledger_credits"}:
        raise HTTPException(status_code=400, detail="Bundle checkout currently supports credit reservation only")

    if body.reserve_credits:
        user_acc = await get_or_create_account(session, "user", UUID(user_id))
        balances = await balance_for_account(session, user_acc.id, body.payment_currency)
        available = balances.get(body.payment_currency) or Decimal(0)
        if available < bundle_total:
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "Insufficient credits for workflow bundle",
                    "currency": body.payment_currency,
                    "required": str(bundle_total),
                    "available": str(available),
                },
            )

    bundle_checkout_id = uuid4().hex
    runs: list[WorkflowRunRecord] = []
    intents: list[PaymentIntent] = []
    for idx, (template, original_amount, allocated_amount) in enumerate(allocations):
        provided_inputs = dict(body.inputs_by_workflow.get(template.slug) or {})
        if body.project_name and not provided_inputs.get("project_name"):
            provided_inputs["project_name"] = body.project_name
        row = _build_workflow_run_record(
            owner_user_id=user_id,
            template=template,
            payment_currency=body.payment_currency,
            unlock_full_result=body.unlock_full_result,
            inputs=provided_inputs,
        )
        _apply_bundle_pricing_to_run(
            row,
            bundle=bundle,
            bundle_checkout_id=bundle_checkout_id,
            original_amount=original_amount,
            allocated_amount=allocated_amount,
            original_total=original_total,
            bundle_total=bundle_total,
            bundle_index=idx,
        )
        session.add(row)
        await session.flush()
        if body.reserve_credits:
            intent = await _reserve_workflow_run_credits(
                session,
                row,
                note=body.note or f"Reserved via bundle checkout: {bundle.title}",
                provider_payload={
                    "bundle_slug": bundle.slug,
                    "bundle_checkout_id": bundle_checkout_id,
                    "bundle_index": idx,
                    "bundle_total": str(bundle_total),
                    "bundle_original_total": str(original_total),
                },
            )
            intents.append(intent)
        runs.append(row)

    await session.flush()
    for row in runs:
        await session.refresh(row)
    for intent in intents:
        await session.refresh(intent)

    discount_amount = max(original_total - bundle_total, Decimal("0")).quantize(Decimal("0.01"))
    return WorkflowBundleCheckoutResponse(
        bundle=bundle,
        bundle_checkout_id=bundle_checkout_id,
        payment_currency=body.payment_currency,
        quoted_total=Money(amount=str(bundle_total), currency=body.payment_currency),
        original_total=Money(amount=str(original_total), currency=body.payment_currency),
        discount_amount=Money(amount=str(discount_amount), currency=body.payment_currency),
        reserved=body.reserve_credits,
        runs=[_serialize_run(row) for row in runs],
        payment_intents=[_serialize_payment_intent(intent) for intent in intents],
    )


@router.get("/admin/revenue", response_model=WorkflowRevenueSummaryPublic)
async def get_workflow_store_revenue_summary(
    session: DbSession,
    admin_user_id: str = Depends(require_platform_admin),
    days: int = Query(30, ge=1, le=365),
):
    generated_at = datetime.now(UTC)
    since = generated_at - timedelta(days=days)
    run_rows = (
        await session.execute(
            select(WorkflowRunRecord)
            .where(WorkflowRunRecord.created_at >= since)
            .order_by(desc(WorkflowRunRecord.created_at))
        )
    ).scalars().all()

    referral_reward_rows = (
        await session.execute(
            select(ReferralRewardEvent)
            .where(
                ReferralRewardEvent.trigger_type == "referral_commission_share",
                ReferralRewardEvent.trigger_ref_type == "order",
                ReferralRewardEvent.created_at >= since,
            )
        )
    ).scalars().all()

    referral_commission_by_run_id: dict[str, Decimal] = {}
    for reward in referral_reward_rows:
        run_id = str(reward.trigger_ref_id)
        referral_commission_by_run_id[run_id] = referral_commission_by_run_id.get(run_id, Decimal(0)) + Decimal(reward.amount_value)

    run_status_counts: dict[str, int] = {}
    sku_map: dict[tuple[str, str], dict[str, object]] = {}
    gross_captured_totals: dict[str, Decimal] = {}
    estimated_cost_totals: dict[str, Decimal] = {}
    estimated_margin_totals: dict[str, Decimal] = {}
    referral_commission_totals: dict[str, Decimal] = {}
    for row in run_rows:
        run_status_counts[row.status] = run_status_counts.get(row.status, 0) + 1
        key = (row.workflow_slug, row.payment_currency)
        if key not in sku_map:
            sku_map[key] = {
                "workflow_slug": row.workflow_slug,
                "title": row.title,
                "category": row.category,
                "currency": row.payment_currency,
                "quote_count": 0,
                "payment_intent_count": 0,
                "requires_payment_count": 0,
                "reserved_count": 0,
                "captured_count": 0,
                "refunded_count": 0,
                "failed_count": 0,
                "cancelled_count": 0,
                "open_reserved_amount": Decimal(0),
                "captured_amount": Decimal(0),
                "refunded_amount": Decimal(0),
                "estimated_cost_amount": Decimal(0),
                "estimated_margin_amount": Decimal(0),
                "referral_commission_amount": Decimal(0),
            }
        sku = sku_map[key]
        sku["quote_count"] = int(sku["quote_count"]) + 1
        proof = (row.receipt_json or {}).get("proof", {}) if isinstance(row.receipt_json, dict) else {}
        provider_cost = ((proof.get("provider_cost_estimate") or {}) if isinstance(proof, dict) else {})
        margin_snapshot = ((proof.get("margin_snapshot") or {}) if isinstance(proof, dict) else {})
        estimated_cost = ((margin_snapshot.get("estimated_cost") or provider_cost) if isinstance(margin_snapshot, dict) else provider_cost)
        estimated_margin = (margin_snapshot.get("estimated_margin") if isinstance(margin_snapshot, dict) else None) or {}
        try:
            if estimated_cost:
                sku["estimated_cost_amount"] = Decimal(sku["estimated_cost_amount"]) + Decimal(str(estimated_cost.get("amount", "0")))
                estimated_cost_totals[row.payment_currency] = estimated_cost_totals.get(row.payment_currency, Decimal(0)) + Decimal(str(estimated_cost.get("amount", "0")))
        except Exception:
            pass
        try:
            if estimated_margin:
                sku["estimated_margin_amount"] = Decimal(sku["estimated_margin_amount"]) + Decimal(str(estimated_margin.get("amount", "0")))
                estimated_margin_totals[row.payment_currency] = estimated_margin_totals.get(row.payment_currency, Decimal(0)) + Decimal(str(estimated_margin.get("amount", "0")))
        except Exception:
            pass
        commission_amount = referral_commission_by_run_id.get(str(row.id), Decimal(0))
        if commission_amount > 0:
            sku["referral_commission_amount"] = Decimal(sku["referral_commission_amount"]) + commission_amount
            referral_commission_totals[row.payment_currency] = referral_commission_totals.get(row.payment_currency, Decimal(0)) + commission_amount

    payment_rows = (
        await session.execute(
            select(PaymentIntent, WorkflowRunRecord)
            .join(WorkflowRunRecord, WorkflowRunRecord.id == PaymentIntent.workflow_run_id)
            .where(PaymentIntent.created_at >= since)
            .order_by(desc(PaymentIntent.created_at))
        )
    ).all()

    payment_status_counts: dict[str, int] = {}
    totals_map: dict[tuple[str, str], dict[str, object]] = {}
    for intent, run in payment_rows:
        status = str(intent.status)
        currency = str(intent.amount_currency)
        amount = Decimal(intent.amount_value)
        payment_status_counts[status] = payment_status_counts.get(status, 0) + 1

        total_key = (currency, status)
        if total_key not in totals_map:
            totals_map[total_key] = {"currency": currency, "status": status, "amount": Decimal(0), "count": 0}
        totals_map[total_key]["amount"] = Decimal(totals_map[total_key]["amount"]) + amount
        totals_map[total_key]["count"] = int(totals_map[total_key]["count"]) + 1

        sku_key = (run.workflow_slug, currency)
        if sku_key not in sku_map:
            sku_map[sku_key] = {
                "workflow_slug": run.workflow_slug,
                "title": run.title,
                "category": run.category,
                "currency": currency,
                "quote_count": 0,
                "payment_intent_count": 0,
                "requires_payment_count": 0,
                "reserved_count": 0,
                "captured_count": 0,
                "refunded_count": 0,
                "failed_count": 0,
                "cancelled_count": 0,
                "open_reserved_amount": Decimal(0),
                "captured_amount": Decimal(0),
                "refunded_amount": Decimal(0),
                "estimated_cost_amount": Decimal(0),
                "estimated_margin_amount": Decimal(0),
                "referral_commission_amount": Decimal(0),
            }
        sku = sku_map[sku_key]
        sku["payment_intent_count"] = int(sku["payment_intent_count"]) + 1
        if status == PaymentIntentStatusEnum.requires_payment.value:
            sku["requires_payment_count"] = int(sku["requires_payment_count"]) + 1
        elif status == PaymentIntentStatusEnum.reserved.value:
            sku["reserved_count"] = int(sku["reserved_count"]) + 1
            sku["open_reserved_amount"] = Decimal(sku["open_reserved_amount"]) + amount
        elif status == PaymentIntentStatusEnum.captured.value:
            sku["captured_count"] = int(sku["captured_count"]) + 1
            sku["captured_amount"] = Decimal(sku["captured_amount"]) + amount
            gross_captured_totals[currency] = gross_captured_totals.get(currency, Decimal(0)) + amount
        elif status == PaymentIntentStatusEnum.refunded.value:
            sku["refunded_count"] = int(sku["refunded_count"]) + 1
            sku["refunded_amount"] = Decimal(sku["refunded_amount"]) + amount
        elif status == PaymentIntentStatusEnum.failed.value:
            sku["failed_count"] = int(sku["failed_count"]) + 1
        elif status == PaymentIntentStatusEnum.cancelled.value:
            sku["cancelled_count"] = int(sku["cancelled_count"]) + 1

    totals = [
        WorkflowRevenueCurrencyTotalPublic(
            currency=str(item["currency"]),
            status=str(item["status"]),
            amount=str(item["amount"]),
            count=int(item["count"]),
        )
        for item in totals_map.values()
    ]
    skus = [
        WorkflowRevenueSkuPublic(
            workflow_slug=str(item["workflow_slug"]),
            title=str(item["title"]),
            category=str(item["category"]),
            currency=str(item["currency"]),
            quote_count=int(item["quote_count"]),
            payment_intent_count=int(item["payment_intent_count"]),
            requires_payment_count=int(item["requires_payment_count"]),
            reserved_count=int(item["reserved_count"]),
            captured_count=int(item["captured_count"]),
            refunded_count=int(item["refunded_count"]),
            failed_count=int(item["failed_count"]),
            cancelled_count=int(item["cancelled_count"]),
            open_reserved_amount=str(item["open_reserved_amount"]),
            captured_amount=str(item["captured_amount"]),
            refunded_amount=str(item["refunded_amount"]),
            estimated_cost_amount=str(item["estimated_cost_amount"]),
            estimated_margin_amount=str(item["estimated_margin_amount"]),
            referral_commission_amount=str(item["referral_commission_amount"]),
        )
        for item in sorted(
            sku_map.values(),
            key=lambda x: (Decimal(x["captured_amount"]), int(x["payment_intent_count"]), int(x["quote_count"])),
            reverse=True,
        )
    ]

    return WorkflowRevenueSummaryPublic(
        generated_at=generated_at,
        since=since,
        window_days=days,
        quote_count=len(run_rows),
        run_status_counts=run_status_counts,
        payment_status_counts=payment_status_counts,
        totals=totals,
        skus=skus,
        gross_captured_totals=[WorkflowRevenueMoneyPublic(currency=currency, amount=str(amount)) for currency, amount in gross_captured_totals.items()],
        estimated_cost_totals=[WorkflowRevenueMoneyPublic(currency=currency, amount=str(amount)) for currency, amount in estimated_cost_totals.items()],
        estimated_margin_totals=[WorkflowRevenueMoneyPublic(currency=currency, amount=str(amount)) for currency, amount in estimated_margin_totals.items()],
        referral_commission_totals=[WorkflowRevenueMoneyPublic(currency=currency, amount=str(amount)) for currency, amount in referral_commission_totals.items()],
    )


@router.get("/admin/revenue/export")
async def export_workflow_store_revenue_csv(
    session: DbSession,
    admin_user_id: str = Depends(require_platform_admin),
    days: int = Query(30, ge=1, le=365),
):
    """Export workflow store revenue data as CSV."""
    generated_at = datetime.now(UTC)
    since = generated_at - timedelta(days=days)

    run_rows = (
        await session.execute(
            select(WorkflowRunRecord)
            .where(WorkflowRunRecord.created_at >= since)
            .order_by(desc(WorkflowRunRecord.created_at))
        )
    ).scalars().all()

    payment_rows = (
        await session.execute(
            select(PaymentIntent, WorkflowRunRecord)
            .join(WorkflowRunRecord, WorkflowRunRecord.id == PaymentIntent.workflow_run_id)
            .where(PaymentIntent.created_at >= since)
            .order_by(desc(PaymentIntent.created_at))
        )
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "type", "run_id", "workflow_slug", "title", "category", "status",
        "payment_status", "currency", "amount", "referral_commission",
        "created_at", "updated_at",
    ])

    for row in run_rows:
        proof = (row.receipt_json or {}).get("proof", {}) if isinstance(row.receipt_json, dict) else {}
        margin_snapshot = (proof.get("margin_snapshot") or {}) if isinstance(proof, dict) else {}
        referral_commission = margin_snapshot.get("referral_commission_amount", "0")

        writer.writerow([
            "run",
            str(row.id),
            row.workflow_slug,
            row.title,
            row.category,
            row.status,
            "",
            row.payment_currency,
            str(row.quoted_amount),
            str(referral_commission),
            row.created_at.isoformat() if row.created_at else "",
            row.updated_at.isoformat() if row.updated_at else "",
        ])

    for intent, run in payment_rows:
        writer.writerow([
            "payment_intent",
            str(run.id),
            run.workflow_slug,
            run.title,
            run.category,
            run.status,
            str(intent.status),
            str(intent.amount_currency),
            str(intent.amount_value),
            "",
            intent.created_at.isoformat() if intent.created_at else "",
            intent.updated_at.isoformat() if intent.updated_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=workflow-revenue-{since.strftime('%Y-%m-%d')}-to-{generated_at.strftime('%Y-%m-%d')}.csv"
        },
    )


@router.get("/runs", response_model=WorkflowRunsResponse)
async def list_workflow_runs(
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100),
    # Phase 4: filter by degraded status
    degraded: bool | None = Query(None, description="Filter runs by degraded status"),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    q = (
        select(WorkflowRunRecord)
        .where(WorkflowRunRecord.owner_user_id == user_id)
        .order_by(desc(WorkflowRunRecord.created_at))
        .limit(limit)
    )
    r = await session.execute(q)
    items = [_serialize_run(row) for row in r.scalars().all()]

    # Phase 4: filter in-memory by degraded_run signal from result_json
    if degraded is not None:
        items = [run for run in items if run.degraded_run == degraded]

    return WorkflowRunsResponse(items=items)


@router.get("/runs/{run_id}", response_model=WorkflowRunPublic)
async def get_workflow_run(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    row = await _get_owned_run(session, user_id, run_id)
    return _serialize_run(row)


@router.get("/runs/{run_id}/events")
async def stream_workflow_run_events(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
    token: str | None = Query(default=None),
):
    if user_id is None and token:
        user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    initial_status = row.status

    async def event_stream():
        last_status = ""
        last_timeline_len = -1
        for _ in range(60):
            current = (
                await session.execute(
                    select(WorkflowRunRecord).where(
                        WorkflowRunRecord.id == UUID(run_id),
                        WorkflowRunRecord.owner_user_id == UUID(user_id),
                    )
                )
            ).scalar_one_or_none()
            if current is None:
                yield "event: error\ndata: {\"message\":\"Workflow run not found\"}\n\n"
                return
            proof = (current.receipt_json or {}).get("proof", {}) if isinstance(current.receipt_json, dict) else {}
            timeline = proof.get("status_timeline") if isinstance(proof, dict) else []
            timeline_len = len(timeline) if isinstance(timeline, list) else 0
            if current.status != last_status or timeline_len != last_timeline_len:
                payload = {
                    "workflow_run_id": str(current.id),
                    "status": current.status,
                    "receipt_status": (current.receipt_json or {}).get("status"),
                    "payment_confirmed": bool(proof.get("payment_confirmation")) if isinstance(proof, dict) else False,
                    "receipt_ready": current.status in {"completed", "failed", "cancelled"},
                    "execution_mode": proof.get("execution_mode") if isinstance(proof, dict) else None,
                    "llm_usage": proof.get("llm_usage") if isinstance(proof, dict) else None,
                    "timeline_length": timeline_len,
                    "updated_at": current.updated_at.isoformat() if current.updated_at else None,
                }
                yield f"event: workflow_run\ndata: {json.dumps(payload, default=str)}\n\n"
                last_status = current.status
                last_timeline_len = timeline_len
            if current.status in {"completed", "failed", "cancelled"} and current.status != initial_status:
                return
            await asyncio.sleep(2)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/runs/{run_id}/payment-intents", response_model=WorkflowRunPaymentIntentCreateResponse, status_code=201)
async def create_workflow_run_payment_intent(
    run_id: str,
    body: WorkflowRunPaymentIntentCreateRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if await is_ledger_invariant_halted(session):
        raise HTTPException(status_code=503, detail="Ledger invariant violated; operations temporarily blocked")

    # Idempotency: return cached response for duplicate requests with the same key.
    if idempotency_key:
        hit = await get_idempotency_hit(
            session, scope="workflow_store.create_payment_intent", key=idempotency_key,
            request_payload={"run_id": run_id, **body.model_dump()},
        )
        if hit:
            return JSONResponse(status_code=200, content=hit.response_json)

    result = await _do_create_workflow_run_payment_intent(
        session, user_id, run_id, body,
    )

    # Store idempotency result if key was provided
    if idempotency_key:
        await store_idempotency_result(
            session, scope="workflow_store.create_payment_intent", key=idempotency_key,
            request_payload={"run_id": run_id, **body.model_dump()},
            status_code=201, response_json=result.model_dump(),
        )

    return result


async def _do_create_workflow_run_payment_intent(
    session: DbSession,
    user_id: str,
    run_id: str,
    body: WorkflowRunPaymentIntentCreateRequest,
) -> WorkflowRunPaymentIntentCreateResponse:
    """Core logic for creating a payment intent for a workflow run. No idempotency handling."""
    if await is_ledger_invariant_halted(session):
        raise HTTPException(status_code=503, detail="Ledger invariant violated; operations temporarily blocked")
    row = await _get_owned_run(session, user_id, run_id)
    current_status = WorkflowRunStatus(row.status)
    existing = await _latest_payment_intent(
        session,
        row,
        {
            PaymentIntentStatusEnum.reserved.value,
            PaymentIntentStatusEnum.captured.value,
            PaymentIntentStatusEnum.refunded.value,
        },
    )
    if existing is not None:
        if existing.status == PaymentIntentStatusEnum.reserved.value and current_status == WorkflowRunStatus.quoted:
            _append_status_transition(row, WorkflowRunStatus.quoted, WorkflowRunStatus.paid)
            await session.flush()
            await session.refresh(row)
        return WorkflowRunPaymentIntentCreateResponse(
            item=_serialize_payment_intent(existing),
            run=_serialize_run(row),
            reserved=existing.status in {PaymentIntentStatusEnum.reserved.value, PaymentIntentStatusEnum.captured.value},
        )

    if current_status != WorkflowRunStatus.quoted:
        raise HTTPException(status_code=400, detail="Payment intent can only be created for quoted workflow runs")

    payment_method = (body.payment_method or "credits").strip().lower()
    amount_value = Decimal(row.quoted_amount)
    if amount_value <= 0:
        raise HTTPException(status_code=400, detail="Workflow run quote must be positive")

    if payment_method not in {"credits", "ledger_credits"}:
        intent = PaymentIntent(
            owner_user_id=UUID(str(row.owner_user_id)),
            workflow_run_id=UUID(str(row.id)),
            intent_type="workflow_run",
            status=PaymentIntentStatusEnum.requires_payment.value,
            payment_method=payment_method,
            amount_currency=row.payment_currency,
            amount_value=amount_value,
            payment_reference=body.payment_reference,
            provider_payload_json={"note": body.note, "mode": "external_manual"},
        )
        session.add(intent)
        await session.flush()
        await session.refresh(intent)
        return WorkflowRunPaymentIntentCreateResponse(
            item=_serialize_payment_intent(intent),
            run=_serialize_run(row),
            reserved=False,
        )

    user_acc = await get_or_create_account(session, "user", UUID(str(row.owner_user_id)))
    from app.db.models import Account
    await session.execute(select(Account.id).where(Account.id == user_acc.id).with_for_update())
    balances = await balance_for_account(session, user_acc.id, row.payment_currency)
    available = balances.get(row.payment_currency) or Decimal(0)
    if available < amount_value:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Insufficient credits for workflow payment",
                "currency": row.payment_currency,
                "required": str(amount_value),
                "available": str(available),
            },
        )

    intent = PaymentIntent(
        owner_user_id=UUID(str(row.owner_user_id)),
        workflow_run_id=UUID(str(row.id)),
        intent_type="workflow_run",
        status=PaymentIntentStatusEnum.requires_payment.value,
        payment_method="credits",
        amount_currency=row.payment_currency,
        amount_value=amount_value,
        payment_reference=body.payment_reference,
        provider_payload_json={"note": body.note, "mode": "ledger_credits"},
    )
    session.add(intent)
    await session.flush()

    escrow_acc = await get_or_create_account(session, "workflow_run", UUID(str(row.id)))
    ev = await append_event(
        session,
        LedgerEventTypeEnum.transfer,
        row.payment_currency,
        amount_value,
        src_account_id=user_acc.id,
        dst_account_id=escrow_acc.id,
        metadata={
            "type": "workflow_payment_reserve",
            "payment_intent_id": str(intent.id),
            "workflow_run_id": str(row.id),
            "workflow_slug": row.workflow_slug,
        },
    )
    intent.status = PaymentIntentStatusEnum.reserved.value
    intent.payment_reference = body.payment_reference or f"credits:{intent.id}"
    intent.reserved_ledger_event_id = ev.id
    intent.provider_payload_json = {
        **(intent.provider_payload_json or {}),
        "reserved_ledger_event_id": str(ev.id),
        "reserved_at": datetime.now(UTC).isoformat(),
    }
    intent.updated_at = datetime.now(UTC)
    _set_receipt_payment_intent_proof(row, intent, proof_status="reserved", ledger_event_id=str(ev.id), note=body.note or "Credits reserved for workflow execution.")
    _append_status_transition(row, WorkflowRunStatus.quoted, WorkflowRunStatus.paid)

    await session.flush()
    await session.refresh(intent)
    await session.refresh(row)
    return WorkflowRunPaymentIntentCreateResponse(
        item=_serialize_payment_intent(intent),
        run=_serialize_run(row),
        reserved=True,
    )


@router.get("/runs/{run_id}/receipt-trail", response_model=WorkflowRunReceiptTrailPublic)
async def get_workflow_run_receipt_trail(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    proof = (row.receipt_json or {}).get("proof", {}) if isinstance(row.receipt_json, dict) else {}
    settlement_intent_id = proof.get("settlement_intent_id")

    if not settlement_intent_id:
        return WorkflowRunReceiptTrailPublic(workflow_run_id=str(row.id), settlement_intent=None, chain_receipts=[])

    try:
        parsed_intent_id = UUID(str(settlement_intent_id))
    except ValueError:
        return WorkflowRunReceiptTrailPublic(workflow_run_id=str(row.id), settlement_intent=None, chain_receipts=[])

    intent = (
        await session.execute(select(SettlementIntent).where(SettlementIntent.id == parsed_intent_id).limit(1))
    ).scalar_one_or_none()
    if intent is None:
        return WorkflowRunReceiptTrailPublic(workflow_run_id=str(row.id), settlement_intent=None, chain_receipts=[])

    receipts = (
        await session.execute(
            select(ChainReceipt)
            .where(ChainReceipt.settlement_intent_id == intent.id)
            .order_by(desc(ChainReceipt.created_at))
        )
    ).scalars().all()

    return WorkflowRunReceiptTrailPublic(
        workflow_run_id=str(row.id),
        settlement_intent=_intent_public(intent),
        chain_receipts=[_chain_receipt_public(item) for item in receipts],
    )


@router.get("/runs/{run_id}/proof-bundle", response_model=WorkflowRunProofBundlePublic)
async def get_workflow_run_proof_bundle(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    proof = (row.receipt_json or {}).get("proof", {}) if isinstance(row.receipt_json, dict) else {}
    settlement_intent_id = proof.get("settlement_intent_id")
    settlement_intent: SettlementIntent | None = None
    receipts: list[ChainReceipt] = []

    if settlement_intent_id:
        try:
            parsed_intent_id = UUID(str(settlement_intent_id))
        except ValueError:
            parsed_intent_id = None

        if parsed_intent_id is not None:
            settlement_intent = (
                await session.execute(select(SettlementIntent).where(SettlementIntent.id == parsed_intent_id).limit(1))
            ).scalar_one_or_none()
            if settlement_intent is not None:
                receipts = (
                    await session.execute(
                        select(ChainReceipt)
                        .where(ChainReceipt.settlement_intent_id == settlement_intent.id)
                        .order_by(desc(ChainReceipt.created_at))
                    )
                ).scalars().all()

    return _build_workflow_run_proof_bundle(row, settlement_intent, receipts)


@router.get("/runs/{run_id}/evidence-export")
async def export_workflow_run_evidence(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    """Phase 4: Export full evidence bundle for B2B buyers and governance audits.

    Returns a structured JSON evidence package containing:
    - Run metadata and identity
    - Input hash (inputs_json)
    - Output hash (result_json)
    - Proof bundle (settlement, chain receipts)
    - LLM usage signals (degraded_run, degraded_reason, llm_usage)
    - Owner and timestamps
    """
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)

    result_json = row.result_json or {}
    llm_usage = result_json.get("llm_usage", {}) if isinstance(result_json, dict) else {}
    receipt_json = row.receipt_json or {}
    proof = receipt_json.get("proof", {}) if isinstance(receipt_json, dict) else {}

    import hashlib, json as _json
    inputs_str = _json.dumps(row.inputs_json or {}, sort_keys=True, default=str, ensure_ascii=False)
    inputs_hash = hashlib.sha256(inputs_str.encode("utf-8")).hexdigest()
    outputs_str = _json.dumps(result_json, sort_keys=True, default=str, ensure_ascii=False)
    outputs_hash = hashlib.sha256(outputs_str.encode("utf-8")).hexdigest()
    prompt_str = llm_usage.get("prompt", "") if isinstance(llm_usage, dict) else ""
    prompt_hash = hashlib.sha256(prompt_str.encode("utf-8")).hexdigest() if prompt_str else ""

    evidence = {
        "evidence_package_version": "v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "workflow_run": {
            "id": str(row.id),
            "slug": row.workflow_slug,
            "title": row.title,
            "category": row.category,
            "status": row.status,
            "inputs_hash": inputs_hash,
            "outputs_hash": outputs_hash,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        },
        "pricing": {
            "quoted_amount": str(row.quoted_amount),
            "payment_currency": row.payment_currency,
        },
        "llm_execution": {
            "provider": llm_usage.get("provider"),
            "model": llm_usage.get("model"),
            "status": llm_usage.get("status"),
            "provider_status": llm_usage.get("provider_status"),
            "failure_reason": llm_usage.get("failure_reason"),
            "retry_count": llm_usage.get("retry_count"),
            "degraded_run": bool(result_json.get("degraded_run", False)) if isinstance(result_json, dict) else False,
            "degraded_reason": result_json.get("degraded_reason") if isinstance(result_json, dict) else None,
            "prompt_hash": prompt_hash,
        },
        "receipt": receipt_json,
        "proof_bundle": proof,
    }

    return JSONResponse(
        content=evidence,
        headers={"Content-Disposition": f'attachment; filename="workflow-evidence-{row.workflow_slug}-{row.id}.json"'},
    )


@router.post("/runs/{run_id}/retry-settlement", response_model=WorkflowRunPaymentConfirmResponse)
async def retry_workflow_run_settlement(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    receipt_json = dict(row.receipt_json or {})
    proof = dict(receipt_json.get("proof", {}))
    settlement_intent_id = proof.get("settlement_intent_id")
    settlement_status = str(proof.get("settlement_status") or "")

    if row.status != WorkflowRunStatus.quoted.value:
        raise HTTPException(status_code=400, detail="Settlement retry is only allowed while workflow run remains quoted")
    if not settlement_intent_id:
        raise HTTPException(status_code=400, detail="No settlement intent linked to this workflow run")
    if settlement_status != "failed":
        raise HTTPException(status_code=400, detail="Settlement retry is only allowed for failed settlement state")

    try:
        parsed_intent_id = UUID(str(settlement_intent_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid settlement intent id on workflow run")

    intent = (
        await session.execute(select(SettlementIntent).where(SettlementIntent.id == parsed_intent_id).limit(1))
    ).scalar_one_or_none()
    if intent is None:
        raise HTTPException(status_code=404, detail="Settlement intent not found")

    await execute_settlement_intent(session, intent)
    await session.refresh(intent)

    proof["settlement_status"] = intent.status
    if intent.error_message:
        proof["settlement_error"] = intent.error_message
    else:
        proof.pop("settlement_error", None)
    proof["settlement_retried_at"] = datetime.now(UTC).isoformat()
    receipt_json["proof"] = proof
    row.receipt_json = receipt_json

    previous_status = WorkflowRunStatus.quoted
    if intent.status == "executed":
        _append_status_transition(row, WorkflowRunStatus.quoted, WorkflowRunStatus.paid)
        await session.flush()
        await session.refresh(row)
        return WorkflowRunPaymentConfirmResponse(
            item=_serialize_run(row),
            previous_status=previous_status,
            payment_confirmed=True,
        )

    await session.commit()
    await session.refresh(row)
    raise HTTPException(
        status_code=409,
        detail={
            "message": "Workflow run settlement retry failed",
            "workflow_run_id": str(row.id),
            "settlement_intent_id": str(intent.id),
            "settlement_status": intent.status,
            "settlement_error": intent.error_message,
        },
    )


@router.post("/runs/{run_id}/confirm-payment", response_model=WorkflowRunPaymentConfirmResponse)
async def confirm_workflow_run_payment(
    run_id: str,
    body: WorkflowRunPaymentConfirmRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    current_status = WorkflowRunStatus(row.status)
    receipt_json = dict(row.receipt_json or {})
    proof = dict(receipt_json.get("proof", {}))
    payment_amount = _resolved_payment_amount(row, body)
    existing_confirmation = proof.get("payment_confirmation") if isinstance(proof.get("payment_confirmation"), dict) else None

    if current_status == WorkflowRunStatus.paid and _payment_confirmation_matches(existing_confirmation, body, payment_amount):
        return WorkflowRunPaymentConfirmResponse(
            item=_serialize_run(row),
            previous_status=WorkflowRunStatus.paid,
            payment_confirmed=True,
        )

    if current_status != WorkflowRunStatus.quoted:
        raise HTTPException(status_code=400, detail="Workflow run payment can only be confirmed from quoted status")

    confirmed_at = datetime.now(UTC).isoformat()
    proof["payment_confirmation"] = {
        "reference": body.payment_reference,
        "method": body.payment_method,
        "confirmed_at": confirmed_at,
        "note": body.note,
        "payment_amount": payment_amount,
    }

    correlation_id = build_correlation_id(f"workflow-run:{row.id}:payment")
    intent = await _get_settlement_intent_by_correlation_id(session, correlation_id)
    if intent is None:
        intent = SettlementIntent(
            intent_type="escrow_open",
            source_owner_type="user",
            source_owner_id=UUID(str(row.owner_user_id)),
            target_owner_type="workflow_run",
            target_owner_id=UUID(str(row.id)),
            amount_currency=str(payment_amount.get("currency") or row.payment_currency).upper(),
            amount_value=Decimal(str(payment_amount.get("amount") or row.quoted_amount)),
            correlation_id=correlation_id,
            metadata_json={
                "workflow_run_id": str(row.id),
                "workflow_slug": row.workflow_slug,
                "payment_reference": body.payment_reference,
                "payment_method": body.payment_method,
                "confirmed_at": confirmed_at,
                "note": body.note,
            },
        )
        session.add(intent)
        await session.flush()
        await execute_settlement_intent(session, intent)
        await session.refresh(intent)

    proof["settlement_correlation_id"] = correlation_id
    proof["settlement_intent_id"] = str(intent.id)
    proof["settlement_status"] = intent.status
    if intent.error_message:
        proof["settlement_error"] = intent.error_message
    receipt_json["proof"] = proof
    row.receipt_json = receipt_json

    if intent.status != "executed":
        await session.commit()
        await session.refresh(row)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Workflow run payment settlement failed",
                "workflow_run_id": str(row.id),
                "settlement_intent_id": str(intent.id),
                "settlement_status": intent.status,
                "settlement_error": intent.error_message,
            },
        )

    _append_status_transition(row, WorkflowRunStatus.quoted, WorkflowRunStatus.paid)

    await session.flush()
    await session.refresh(row)

    return WorkflowRunPaymentConfirmResponse(
        item=_serialize_run(row),
        previous_status=WorkflowRunStatus.quoted,
        payment_confirmed=True,
    )


@router.post("/runs/{run_id}/status", response_model=WorkflowRunStatusUpdateResponse)
async def update_workflow_run_status(
    run_id: str,
    body: WorkflowRunStatusUpdateRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    current_status = WorkflowRunStatus(row.status)
    target_status = body.status

    if target_status == current_status:
        return WorkflowRunStatusUpdateResponse(item=_serialize_run(row), previous_status=current_status)

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid workflow run status transition",
                "current_status": current_status.value,
                "target_status": target_status.value,
                "allowed": [status.value for status in sorted(allowed, key=lambda x: x.value)],
            },
        )

    if current_status == WorkflowRunStatus.quoted and target_status == WorkflowRunStatus.paid:
        raise HTTPException(
            status_code=400,
            detail="Use /confirm-payment to move a workflow run from quoted to paid",
        )

    await _append_status_transition_and_broadcast(row, current_status, target_status)

    if target_status == WorkflowRunStatus.completed and not row.result_json:
        template = find_workflow_template(row.workflow_slug)
        if template:
            row.result_json = execute_workflow_template(template, row.inputs_json or {})
    elif target_status in {WorkflowRunStatus.failed, WorkflowRunStatus.cancelled} and row.result_json is None:
        row.result_json = {
            "status": target_status.value,
            "note": f"Workflow run marked as {target_status.value}.",
        }

    if target_status == WorkflowRunStatus.completed:
        await _capture_reserved_workflow_payment(session, row)
        try:
            owner_id = str(row.owner_user_id)
            await emit_run_completed(session, str(row.id), row.title, owner_id)
            await emit_payment_captured(
                session,
                str(row.id),
                str(row.quoted_amount),
                row.payment_currency,
                str(row.id),
                owner_user_id=owner_id,
            )
        except Exception:
            pass
    elif target_status in {WorkflowRunStatus.failed, WorkflowRunStatus.cancelled}:
        await _refund_reserved_workflow_payment(session, row, f"Workflow run moved to {target_status.value}.")
        try:
            intent = await _latest_payment_intent(session, row, {PaymentIntentStatusEnum.reserved.value})
            if intent:
                await emit_payment_refunded(
                    session,
                    str(intent.id),
                    str(intent.amount_value),
                    intent.amount_currency,
                    target_status.value,
                    owner_user_id=str(row.owner_user_id),
                )
        except Exception:
            pass

    await session.flush()
    await session.refresh(row)

    return WorkflowRunStatusUpdateResponse(
        item=_serialize_run(row),
        previous_status=current_status,
    )


@router.post("/runs/{run_id}/execute", response_model=WorkflowRunExecuteResponse)
async def execute_workflow_run(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    row = await _get_owned_run(session, user_id, run_id)
    template = find_workflow_template(row.workflow_slug)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    current_status = WorkflowRunStatus(row.status)
    if current_status in {WorkflowRunStatus.completed, WorkflowRunStatus.failed, WorkflowRunStatus.cancelled}:
        raise HTTPException(status_code=400, detail="Workflow run is already terminal")
    if current_status == WorkflowRunStatus.quoted:
        raise HTTPException(status_code=400, detail="Payment must be confirmed before execution")

    if current_status == WorkflowRunStatus.paid:
        await _append_status_transition_and_broadcast(row, WorkflowRunStatus.paid, WorkflowRunStatus.queued)
        current_status = WorkflowRunStatus.queued
    if current_status == WorkflowRunStatus.queued:
        await _append_status_transition_and_broadcast(row, WorkflowRunStatus.queued, WorkflowRunStatus.running)
        current_status = WorkflowRunStatus.running
    if current_status != WorkflowRunStatus.running:
        raise HTTPException(status_code=400, detail="Workflow run is not executable from current status")

    llm_result = await execute_paid_workflow_with_llm(
        session,
        template=template,
        inputs=row.inputs_json or {},
        owner_user_id=user_id,
        workflow_run_id=row.id,
    )
    row.result_json = llm_result.result
    await _append_status_transition_and_broadcast(row, WorkflowRunStatus.running, WorkflowRunStatus.completed)

    execution_summary = row.result_json.get("execution_summary", {}) if isinstance(row.result_json, dict) else {}
    if not isinstance(execution_summary, dict):
        execution_summary = {}
    execution_mode = str(execution_summary.get("mode") or "template_stub")

    receipt_json = dict(row.receipt_json or {})
    proof = dict(receipt_json.get("proof", {}))
    proof["execution_mode"] = execution_mode
    proof["executed_at"] = datetime.now(UTC).isoformat()
    proof["template_title"] = template.title
    proof["artifact_kind"] = execution_summary.get("artifact_kind")
    proof["sections_generated"] = execution_summary.get("sections_generated")
    proof["llm_usage"] = {
        "event_id": llm_result.usage_event_id,
        "provider": llm_result.provider,
        "model": llm_result.model,
        "status": llm_result.status,
        "fallback_used": llm_result.fallback_used,
    }
    receipt_json["proof"] = proof
    row.receipt_json = receipt_json
    await _capture_reserved_workflow_payment(session, row)

    await create_notification(
        session,
        recipient_user_id=UUID(user_id),
        recipient_agent_id=None,
        type="workflow.completed",
        priority="high",
        payload={
            "workflow_run_id": str(row.id),
            "workflow_slug": row.workflow_slug,
            "title": row.title,
            "status": WorkflowRunStatus.completed.value,
            "proof_url": f"/proof-center?run={row.id}",
            "llm_usage_event_id": llm_result.usage_event_id,
        },
    )
    user_row = (await session.execute(select(User).where(User.id == UUID(user_id)))).scalar_one_or_none()
    if user_row and can_receive_system_email(user_row.email):
        proof_url = f"{get_settings().public_app_url.rstrip('/')}/proof-center?run={row.id}"
        send_email(
            to_email=user_row.email,
            subject=f"ANCAP workflow completed: {row.title}",
            text_body=(
                f"Your ANCAP workflow run is complete.\n\n"
                f"Workflow: {row.title}\n"
                f"Run: {row.id}\n"
                f"Proof: {proof_url}\n"
            ),
            html_body=(
                f"<p>Your ANCAP workflow run is complete.</p>"
                f"<p><strong>Workflow:</strong> {row.title}</p>"
                f"<p><strong>Run:</strong> {row.id}</p>"
                f"<p><a href=\"{proof_url}\">Open proof receipt</a></p>"
            ),
        )

    await session.flush()
    await session.refresh(row)

    # Emit webhooks after successful completion
    try:
        captured_intent = await _latest_payment_intent(session, row, {PaymentIntentStatusEnum.captured.value})
        payment_id = str(captured_intent.id) if captured_intent else str(row.id)
        owner_id = str(user_id)
        await emit_run_completed(session, str(row.id), row.title, owner_id)
        await emit_payment_captured(
            session,
            payment_id,
            str(row.quoted_amount),
            row.payment_currency,
            str(row.id),
            owner_user_id=owner_id,
        )
        proof_url = f"{get_settings().public_app_url.rstrip('/')}/proof-center?run={row.id}"
        await emit_receipt_ready(session, str(row.id), proof_url, owner_user_id=owner_id)
    except Exception:
        pass  # webhooks are non-blocking

    return WorkflowRunExecuteResponse(
        item=_serialize_run(row),
        execution_mode=execution_mode,
    )


@router.post("/runs/{run_id}/repeat", response_model=WorkflowRunPublic, status_code=201)
async def repeat_workflow_run(
    run_id: str,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    source_row = await _get_owned_run(session, user_id, run_id)
    template = find_workflow_template(source_row.workflow_slug)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    payment_currency = source_row.payment_currency
    if payment_currency not in template.accepted_currencies:
        payment_currency = template.accepted_currencies[0] if template.accepted_currencies else template.price.currency

    row = _build_workflow_run_record(
        owner_user_id=user_id,
        template=template,
        payment_currency=payment_currency,
        unlock_full_result=source_row.unlock_full_result,
        inputs=source_row.inputs_json or {},
        repeated_from_run_id=str(source_row.id),
        repeated_from_status=source_row.status,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)

    return _serialize_run(row)


@router.post("/runs", response_model=WorkflowRunPublic, status_code=201)
async def create_workflow_run(
    body: WorkflowRunCreateRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Idempotency: if key provided, check for a prior hit with the same request payload.
    if idempotency_key:
        hit = await get_idempotency_hit(
            session, scope="workflow_store.create_run", key=idempotency_key,
            request_payload=body.model_dump(),
        )
        if hit:
            return JSONResponse(status_code=200, content=hit.response_json)

    template = find_workflow_template(body.workflow_slug)
    if template is None:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    if body.payment_currency not in template.accepted_currencies:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported payment currency for workflow",
                "accepted_currencies": template.accepted_currencies,
            },
        )

    from app.services.market_economy import get_wacp_usd_oracle

    await get_wacp_usd_oracle()

    row = _build_workflow_run_record(
        owner_user_id=user_id,
        template=template,
        payment_currency=body.payment_currency,
        unlock_full_result=body.unlock_full_result,
        inputs=body.inputs,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)

    result = _serialize_run(row)

    # Store idempotency result if key was provided
    if idempotency_key:
        await store_idempotency_result(
            session, scope="workflow_store.create_run", key=idempotency_key,
            request_payload=body.model_dump(), status_code=201, response_json=result.model_dump(),
        )

    return result
