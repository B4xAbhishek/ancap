"""Public mobile gateway for non-custodial ACP Wallet (read + broadcast relay).

See docs/mobile/API_MOBILE.md and docs/mobile/ROADMAP.md.
"""
from __future__ import annotations

import hashlib
import logging
import re
from decimal import Decimal, ROUND_UP
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, unquote, urlparse
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user_id, require_auth
from app.api.routers import wallet_acp
from app.db.models import MobileDevice, MobileSmartPayRecord
from app.config import get_settings
from app.services.bridge_decimal import WACP_PER_ACP
from app.schemas.mobile_acp import (
    AcpBroadcastRequest,
    AcpBroadcastResponse,
    AcpFeeEstimateRequest,
    AcpFeeEstimateResponse,
    AcpNetworkStatusResponse,
    MerchantHint,
    MobileAcpBalanceResponse,
    MobileConfigResponse,
    MobileDocsLinks,
    PaymentAmount,
    PaymentAsset,
    PaymentIntentMetadata,
    PaymentIntentResponseItem,
    PaymentMemo,
    PaymentRecipient,
    SmartPayCapabilitiesResponse,
    SmartPayExecuteRequest,
    SmartPayExecutionItem,
    SmartPayExecutionProgress,
    SmartPayExecutionResponse,
    SmartPayNetworkFeeItem,
    SmartPayPaymentHistoryEntry,
    SmartPayPaymentHistoryResponse,
    SmartPayQuoteAsset,
    SmartPayQuoteItem,
    SmartPayQuoteRequest,
    SmartPayQuoteResponse,
    SmartPayReceiptItem,
    SmartPayRecoverRequest,
    SmartPayRouteExecutionStep,
    SmartPayRouteStep,
    SmartPaySupportedAsset,
    SmartPayTxRef,
    SmartQrParseRequest,
    SmartQrParseResponse,
)
from app.schemas.wallets import AcpTransactionDetailsPublic, AcpTransactionPublic
from app.services.payment_text_parse import parse_payment_text
from app.services.rate_limit import enforce_rate_limit, get_request_ip


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Mobile (ACP Wallet)"])

# Matches acp-crypto protocol_params MIN_FEE_UNITS = 100 (1e-8 ACP units)
_DEFAULT_MIN_FEE_ACP = "0.00000100"
_DEFAULT_MIN_FEE_UNITS = "100"
_EVM_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_EIP681_NATIVE_TRANSFER_SEGMENT = "/transfer"
_ACP_TO_USDT_RATE = Decimal("0.25")
_SERVICE_FEE_ACP = Decimal("0.75")
_BSC_NETWORK_FEE_BNB = Decimal("0.00021")
_QUOTE_TTL_MINUTES = 5
_RECOVERY_URL_QUERY_KEYS = ("txid", "txId", "hash", "txHash", "transactionHash")
_RECOVERY_URL_PATH_MARKERS = {"tx", "txs", "transaction", "transactions"}
_RECOVERY_URL_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_RECOVERY_URL_HOST_RE = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}(?:[/:?#]|$)", re.IGNORECASE)


def _public_docs() -> MobileDocsLinks:
    base = "https://ancap.cloud"
    return MobileDocsLinks(
        bridge=f"{base}/docs/wacp/bridge",
        risks=f"{base}/docs/wacp/risks",
        reserve=f"{base}/docs/wacp/reserve",
        contracts=f"{base}/docs/wacp/contracts",
        wallet_security=f"{base}/docs/mobile/security",
    )


def _acp_rpc_status() -> str:
    settings = get_settings()
    if not (settings.acp_rpc_url or "").strip():
        return "unconfigured"
    try:
        wallet_acp._rpc_call(settings.acp_rpc_url.strip(), "getblockcount", [])
        return "ok"
    except HTTPException:
        return "degraded"
    except Exception as exc:
        logger.warning("mobile acp rpc probe failed: %s", exc)
        return "degraded"


def _bridge_status_label() -> str:
    s = get_settings()
    if not s.bridge_rail_enabled:
        return "disabled"
    if s.bridge_rail_paused:
        return "paused"
    return "ok"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _payload_hash(raw_payload: str) -> str:
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def _new_session_token() -> str:
    return hashlib.sha256(uuid4().hex.encode("utf-8")).hexdigest()


# In-process cache in front of the durable mobile_smart_pay_records table.
_PAYMENT_INTENTS: dict[str, PaymentIntentResponseItem] = {}
_SMART_PAY_QUOTES: dict[str, SmartPayQuoteItem] = {}
_SMART_PAY_EXECUTIONS: dict[str, SmartPayExecutionItem] = {}
_SMART_PAY_RECEIPTS: dict[str, SmartPayReceiptItem] = {}
_SMART_PAY_EXECUTION_OWNERS: dict[str, str | None] = {}
_SMART_PAY_EXECUTION_SESSION_TOKENS: dict[str, str] = {}


async def _persist_smart_pay_record(
    session,
    *,
    record_id: str,
    kind: str,
    payload_model,
    owner_user_id: str | None = None,
    session_token: str | None = None,
) -> None:
    """Write-through persistence so Smart Pay state survives API restarts."""
    record = await session.get(MobileSmartPayRecord, record_id)
    data = payload_model.model_dump(mode="json")
    if record is None:
        session.add(
            MobileSmartPayRecord(
                id=record_id,
                kind=kind,
                owner_user_id=owner_user_id,
                session_token=session_token,
                payload=data,
            )
        )
    else:
        record.payload = data
        if owner_user_id is not None:
            record.owner_user_id = owner_user_id
        if session_token is not None:
            record.session_token = session_token
    await session.flush()


async def _hydrate_intent(session, intent_id: str) -> PaymentIntentResponseItem | None:
    intent_id = (intent_id or "").strip()
    cached = _PAYMENT_INTENTS.get(intent_id)
    if cached is not None:
        return cached
    record = await session.get(MobileSmartPayRecord, intent_id)
    if record is None or record.kind != "intent":
        return None
    intent = PaymentIntentResponseItem.model_validate(record.payload)
    _PAYMENT_INTENTS[intent.id] = intent
    return intent


async def _hydrate_quote(session, quote_id: str) -> SmartPayQuoteItem | None:
    quote_id = (quote_id or "").strip()
    cached = _SMART_PAY_QUOTES.get(quote_id)
    if cached is not None:
        return cached
    record = await session.get(MobileSmartPayRecord, quote_id)
    if record is None or record.kind != "quote":
        return None
    quote = SmartPayQuoteItem.model_validate(record.payload)
    _SMART_PAY_QUOTES[quote.quote_id] = quote
    return quote


def _mask_legacy_unverified_completion(execution: SmartPayExecutionItem) -> SmartPayExecutionItem:
    """Old recover results could claim completion from client-submitted tx hashes alone.

    No trusted chain-confirmation path currently sets Smart Pay completion. Normalize
    legacy cache/DB snapshots on reads without rewriting their original evidence.
    """
    if execution.status != "completed":
        return execution
    return execution.model_copy(
        update={"status": "pending_reconciliation", "recoverable": True, "next_action": None}
    )


async def _hydrate_execution(session, execution_id: str) -> SmartPayExecutionItem | None:
    execution_id = (execution_id or "").strip()
    cached = _SMART_PAY_EXECUTIONS.get(execution_id)
    if cached is not None:
        normalized = _mask_legacy_unverified_completion(cached)
        _SMART_PAY_EXECUTIONS[execution_id] = normalized
        return normalized
    record = await session.get(MobileSmartPayRecord, execution_id)
    if record is None or record.kind != "execution":
        return None
    execution = _mask_legacy_unverified_completion(SmartPayExecutionItem.model_validate(record.payload))
    _SMART_PAY_EXECUTIONS[execution.id] = execution
    _SMART_PAY_EXECUTION_OWNERS[execution.id] = str(record.owner_user_id) if record.owner_user_id else None
    if record.session_token:
        _SMART_PAY_EXECUTION_SESSION_TOKENS[execution.id] = record.session_token
    return execution


async def _hydrate_receipt(session, execution_id: str) -> SmartPayReceiptItem | None:
    execution_id = (execution_id or "").strip()
    execution = await _hydrate_execution(session, execution_id)
    cached = _SMART_PAY_RECEIPTS.get(execution_id)
    if cached is not None:
        receipt = cached
    else:
        record = await session.get(MobileSmartPayRecord, f"spr_{execution_id}")
        if record is None or record.kind != "receipt":
            return None
        receipt = SmartPayReceiptItem.model_validate(record.payload)
    # Historical receipts stored completedAt even for unsigned/in-flight payments.
    if execution is None or execution.status != "completed":
        receipt = receipt.model_copy(update={"completed_at": None})
    _SMART_PAY_RECEIPTS[execution_id] = receipt
    return receipt


async def _persist_execution_bundle(
    session,
    *,
    intent: PaymentIntentResponseItem,
    quote: SmartPayQuoteItem,
    execution: SmartPayExecutionItem,
    owner_user_id: str | None,
    session_token: str | None,
) -> None:
    receipt = _SMART_PAY_RECEIPTS.get(execution.id)
    await _persist_smart_pay_record(session, record_id=intent.id, kind="intent", payload_model=intent)
    await _persist_smart_pay_record(session, record_id=quote.quote_id, kind="quote", payload_model=quote)
    await _persist_smart_pay_record(
        session,
        record_id=execution.id,
        kind="execution",
        payload_model=execution,
        owner_user_id=owner_user_id,
        session_token=session_token,
    )
    if receipt is not None:
        await _persist_smart_pay_record(
            session,
            record_id=receipt.id,
            kind="receipt",
            payload_model=receipt,
            owner_user_id=owner_user_id,
        )


def _supported_assets() -> list[SmartPaySupportedAsset]:
    s = get_settings()
    assets = [SmartPaySupportedAsset(network="acp", symbol="ACP")]
    wacp_contract = (s.bridge_wacp_contract or "").strip() or None
    assets.append(SmartPaySupportedAsset(network="bsc", symbol="wACP", token_address=wacp_contract))
    sacp_contract = (getattr(s, "sacp_contract", None) or "").strip() or None
    if bool(getattr(s, "ff_sacp", True)):
        assets.append(SmartPaySupportedAsset(network="bsc", symbol="sACP", token_address=sacp_contract))
    assets.append(SmartPaySupportedAsset(network="bsc", symbol="USDT", token_address=None))
    return assets


def _base_metadata(detected_standard: str | None, invoice_type: str | None) -> PaymentIntentMetadata:
    return PaymentIntentMetadata(
        detected_standard=detected_standard,
        invoice_type=invoice_type,
        ai_model=None,
        ai_used=False,
        parser_version="1",
    )


def _make_payment_intent(
    *,
    source: str,
    raw_payload: str,
    parse_method: str,
    confidence: float,
    status: str,
    network: str,
    asset: PaymentAsset,
    recipient: PaymentRecipient,
    amount: PaymentAmount | None,
    memo: PaymentMemo | None,
    merchant: MerchantHint | None,
    risk_flags: list[str],
    warnings: list[str],
    unsupported_reasons: list[str],
    metadata: PaymentIntentMetadata,
) -> PaymentIntentResponseItem:
    intent = PaymentIntentResponseItem(
        id=f"pi_{uuid4().hex}",
        created_at=_utc_now_iso(),
        source=source,
        raw_payload=raw_payload,
        payload_hash=_payload_hash(raw_payload),
        parse_method=parse_method,
        confidence=confidence,
        status=status,
        network=network,
        asset=asset,
        recipient=recipient,
        amount=amount,
        memo=memo,
        merchant=merchant,
        risk_flags=risk_flags,
        warnings=warnings,
        unsupported_reasons=unsupported_reasons,
        requires_user_confirmation=True,
        metadata=metadata,
    )
    _PAYMENT_INTENTS[intent.id] = intent
    return intent


def _parse_decimal_string(raw: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise HTTPException(status_code=400, detail="amount is required")
    normalized = value.replace(",", "")
    wallet_acp._parse_positive_decimal(normalized, "amount")
    return normalized


def _parse_acp_payload(source: str, raw_payload: str) -> PaymentIntentResponseItem:
    payload = raw_payload.strip()
    if "?" in payload:
        address_part, query_part = payload.split("?", 1)
    else:
        address_part, query_part = payload, ""
    address = wallet_acp._validate_acp_address(address_part, "recipient")
    params = parse_qs(query_part, keep_blank_values=False)
    amount_value = params.get("amount", [None])[0]
    memo_value = params.get("memo", [None])[0] or params.get("message", [None])[0]
    amount = None
    if amount_value:
        parsed_amount = _parse_decimal_string(amount_value)
        amount = PaymentAmount(
            value=parsed_amount,
            atomic_value=None,
            currency_symbol="ACP",
            is_exact=True,
            is_max=False,
        )
    memo = None
    if memo_value:
        memo = PaymentMemo(value=memo_value, type="memo", required=False)
    return _make_payment_intent(
        source=source,
        raw_payload=raw_payload,
        parse_method="deterministic",
        confidence=1.0,
        status="parsed",
        network="acp",
        asset=PaymentAsset(kind="native", symbol="ACP", name="ACP", token_address=None, decimals=8, is_supported=True, is_allowlisted=True),
        recipient=PaymentRecipient(address=address, resolved_display=None, address_type="acp", checksum_valid=True, ens_or_alias=None),
        amount=amount,
        memo=memo,
        merchant=None,
        risk_flags=[],
        warnings=[],
        unsupported_reasons=[],
        metadata=_base_metadata("acp_uri" if query_part else "acp_address", "native_transfer"),
    )


def _parse_evm_address_payload(source: str, raw_payload: str) -> PaymentIntentResponseItem:
    address = raw_payload.strip()
    if not _EVM_ADDRESS_RE.fullmatch(address):
        raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")
    return _make_payment_intent(
        source=source,
        raw_payload=raw_payload,
        parse_method="deterministic",
        confidence=1.0,
        status="needs_review",
        network="unknown",
        asset=PaymentAsset(kind="unknown", symbol=None, name=None, token_address=None, decimals=None, is_supported=False, is_allowlisted=False),
        recipient=PaymentRecipient(address=address, resolved_display=None, address_type="evm", checksum_valid=True, ens_or_alias=None),
        amount=None,
        memo=None,
        merchant=None,
        risk_flags=["unknown_network", "unknown_asset", "missing_amount"],
        warnings=["Raw EVM address detected. Select network and asset before paying."],
        unsupported_reasons=[],
        metadata=_base_metadata("evm_address", "address_only"),
    )


def _parse_eip681_payload(source: str, raw_payload: str) -> PaymentIntentResponseItem:
    decoded = unquote(raw_payload.strip())
    parsed = urlparse(decoded)
    if parsed.scheme.lower() != "ethereum":
        raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")

    target = parsed.path or parsed.netloc
    if not target:
        raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")

    params = parse_qs(parsed.query, keep_blank_values=False)
    token_transfer = target.endswith(_EIP681_NATIVE_TRANSFER_SEGMENT)
    if token_transfer:
        contract_part = target[: -len(_EIP681_NATIVE_TRANSFER_SEGMENT)]
        if "@" in contract_part:
            contract_part, chain_id = contract_part.split("@", 1)
        else:
            chain_id = ""
        recipient = params.get("address", [None])[0]
        atomic = params.get("uint256", [None])[0]
        if not contract_part or not _EVM_ADDRESS_RE.fullmatch(contract_part) or not recipient or not _EVM_ADDRESS_RE.fullmatch(recipient):
            raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")
        amount = None
        if atomic:
            if not atomic.isdigit():
                raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")
            amount = PaymentAmount(value=atomic, atomic_value=atomic, currency_symbol="USDT", is_exact=True, is_max=False)
        network = "bsc" if chain_id == "56" else "ethereum"
        return _make_payment_intent(
            source=source,
            raw_payload=raw_payload,
            parse_method="deterministic",
            confidence=1.0,
            status="parsed",
            network=network,
            asset=PaymentAsset(kind="erc20", symbol="USDT", name="Tether USD", token_address=contract_part, decimals=None, is_supported=network == "bsc", is_allowlisted=network == "bsc"),
            recipient=PaymentRecipient(address=recipient, resolved_display=None, address_type="evm", checksum_valid=True, ens_or_alias=None),
            amount=amount,
            memo=None,
            merchant=None,
            risk_flags=[] if network == "bsc" else ["unsupported_asset"],
            warnings=[] if network == "bsc" else ["Ethereum mainnet token payments are not in first Smart Pay release scope."],
            unsupported_reasons=[] if network == "bsc" else ["network_not_in_first_release_scope"],
            metadata=_base_metadata("eip681", "token_transfer"),
        )

    address_only = target
    if "@" in address_only:
        address_only, chain_id = address_only.split("@", 1)
    else:
        chain_id = ""
    if not _EVM_ADDRESS_RE.fullmatch(address_only):
        raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")
    amount_raw = params.get("value", [None])[0]
    amount = None
    if amount_raw:
        parsed_amount = _parse_decimal_string(amount_raw)
        amount = PaymentAmount(value=parsed_amount, atomic_value=None, currency_symbol="ETH" if chain_id != "56" else "BNB", is_exact=True, is_max=False)
    network = "bsc" if chain_id == "56" else "ethereum"
    symbol = "BNB" if network == "bsc" else "ETH"
    return _make_payment_intent(
        source=source,
        raw_payload=raw_payload,
        parse_method="deterministic",
        confidence=1.0,
        status="parsed",
        network=network,
        asset=PaymentAsset(kind="native", symbol=symbol, name=symbol, token_address=None, decimals=18, is_supported=network == "bsc", is_allowlisted=network == "bsc"),
        recipient=PaymentRecipient(address=address_only, resolved_display=None, address_type="evm", checksum_valid=True, ens_or_alias=None),
        amount=amount,
        memo=None,
        merchant=None,
        risk_flags=[] if network == "bsc" else ["unsupported_asset"],
        warnings=[] if network == "bsc" else ["Ethereum mainnet payments are not in first Smart Pay release scope."],
        unsupported_reasons=[] if network == "bsc" else ["network_not_in_first_release_scope"],
        metadata=_base_metadata("eip681", "native_transfer"),
    )


def _parse_ocr_invoice_payload(source: str, raw_payload: str) -> PaymentIntentResponseItem:
    parsed = parse_payment_text(raw_payload, source="ocr")
    if not parsed.address:
        raise HTTPException(status_code=400, detail="Unsupported or malformed OCR payload")

    network = parsed.detected_network or "unknown"
    address_type = "acp" if network == "acp" else ("evm" if parsed.address.startswith("0x") else "unknown")
    asset_symbol = parsed.currency or ("ACP" if network == "acp" else "USDT")
    amount = None
    if parsed.amount:
        amount = PaymentAmount(
            value=parsed.amount,
            atomic_value=None,
            currency_symbol=asset_symbol,
            is_exact=True,
            is_max=False,
        )

    merchant = MerchantHint(label=parsed.label, category=None, website=None, invoice_id=parsed.label)
    risk_flags: list[str] = []
    warnings: list[str] = ["OCR/receipt parse requires manual review before execute."]
    unsupported_reasons: list[str] = []
    if network not in {"acp", "bsc"}:
        risk_flags.append("unknown_network")
        if network == "ethereum":
            unsupported_reasons.append("network_not_in_first_release_scope")
            warnings.append("Ethereum mainnet payments are not in first Smart Pay release scope.")
    if amount is None:
        risk_flags.append("missing_amount")
        warnings.append("Amount not detected from OCR text; confirm before paying.")

    is_supported = network in {"acp", "bsc"} and address_type in {"acp", "evm"}
    return _make_payment_intent(
        source=source,
        raw_payload=raw_payload,
        parse_method="heuristic",
        confidence=parsed.confidence,
        status="needs_review" if parsed.confidence < 0.75 else "parsed",
        network=network if network != "unknown" else ("acp" if address_type == "acp" else "bsc"),
        asset=PaymentAsset(
            kind="native" if asset_symbol in {"ACP", "BNB", "ETH"} else "erc20",
            symbol=asset_symbol,
            name=asset_symbol,
            token_address=None,
            decimals=8 if asset_symbol == "ACP" else 18,
            is_supported=is_supported,
            is_allowlisted=is_supported,
        ),
        recipient=PaymentRecipient(
            address=parsed.address,
            resolved_display=None,
            address_type=address_type,
            checksum_valid=address_type == "evm",
            ens_or_alias=None,
        ),
        amount=amount,
        memo=None,
        merchant=merchant if parsed.label else None,
        risk_flags=risk_flags,
        warnings=warnings,
        unsupported_reasons=unsupported_reasons,
        metadata=_base_metadata("ocr", "invoice_or_receipt"),
    )


def _parse_smart_qr_payload(source: str, raw_payload: str) -> PaymentIntentResponseItem:
    payload = (raw_payload or "").strip()
    if not payload:
        raise HTTPException(status_code=400, detail="rawPayload is required")
    if source == "ocr":
        return _parse_ocr_invoice_payload(source, payload)
    if payload.startswith("ethereum:"):
        return _parse_eip681_payload(source, payload)
    if payload.startswith("acp1"):
        return _parse_acp_payload(source, payload)
    if _EVM_ADDRESS_RE.fullmatch(payload):
        return _parse_evm_address_payload(source, payload)
    if source in {"photo", "paste", "share"}:
        try:
            return _parse_ocr_invoice_payload(source, payload)
        except HTTPException:
            pass
    raise HTTPException(status_code=400, detail="Unsupported or malformed QR payload")


def _quantize_up(value: Decimal, places: str) -> str:
    return str(value.quantize(Decimal(places), rounding=ROUND_UP))


def _get_payment_intent_or_404(payment_intent_id: str) -> PaymentIntentResponseItem:
    intent = _PAYMENT_INTENTS.get((payment_intent_id or "").strip())
    if intent is None:
        raise HTTPException(status_code=404, detail="paymentIntentId not found")
    return intent


def _get_quote_or_404(quote_id: str) -> SmartPayQuoteItem:
    quote = _SMART_PAY_QUOTES.get((quote_id or "").strip())
    if quote is None:
        raise HTTPException(status_code=404, detail="quoteId not found")
    return quote


def _get_session_token(execution_id: str) -> str | None:
    return _SMART_PAY_EXECUTION_SESSION_TOKENS.get((execution_id or "").strip())


def _session_token_matches(execution_id: str, supplied: str | None) -> bool:
    expected = _get_session_token(execution_id)
    if not expected or not supplied:
        return False
    return supplied.strip() == expected


def _can_access_execution(execution_id: str, user_id: str | None, session_token: str | None) -> bool:
    owner_id = _SMART_PAY_EXECUTION_OWNERS.get((execution_id or "").strip())
    return (user_id is not None and owner_id == user_id) or _session_token_matches(execution_id, session_token)


def _require_execution_access(execution_id: str, user_id: str | None, session_token: str | None) -> None:
    if _can_access_execution(execution_id, user_id, session_token):
        return
    raise HTTPException(status_code=401, detail="Smart Pay execution access required")


def _intent_target_amount(intent: PaymentIntentResponseItem) -> Decimal:
    if intent.amount is None or not intent.amount.value:
        raise HTTPException(status_code=422, detail="Payment intent is missing amount")
    return Decimal(str(intent.amount.value))


def _source_asset_for_symbol(symbol: str) -> SmartPayQuoteAsset:
    normalized = (symbol or "").strip().upper()
    if normalized == "ACP":
        return SmartPayQuoteAsset(network="acp", symbol="ACP", token_address=None, decimals=8)
    if normalized == "WACP":
        s = get_settings()
        return SmartPayQuoteAsset(network="bsc", symbol="wACP", token_address=(s.bridge_wacp_contract or "").strip() or None, decimals=18)
    if normalized in {"SACP", "STABLE ACP"}:
        s = get_settings()
        return SmartPayQuoteAsset(
            network="bsc",
            symbol="sACP",
            token_address=(getattr(s, "sacp_contract", None) or "").strip() or None,
            decimals=18,
        )
    if normalized == "USDT":
        return SmartPayQuoteAsset(network="bsc", symbol="USDT", token_address=None, decimals=18)
    raise HTTPException(status_code=422, detail=f"Unsupported preferred asset: {symbol}")


def _target_asset_from_intent(intent: PaymentIntentResponseItem) -> SmartPayQuoteAsset:
    return SmartPayQuoteAsset(
        network=intent.network,
        symbol=intent.asset.symbol or "UNKNOWN",
        token_address=intent.asset.token_address,
        decimals=intent.asset.decimals,
    )


def _build_quote_route(intent: PaymentIntentResponseItem, source_symbol: str) -> tuple[str, list[SmartPayRouteStep], list[SmartPayNetworkFeeItem]]:
    source = source_symbol.upper()
    if intent.network == "acp" and source == "ACP":
        return (
            "direct_send",
            [SmartPayRouteStep(kind="transfer", network="acp", dex_or_rail=None, from_asset="ACP", to_asset="ACP", estimated_out=intent.amount.value if intent.amount else "0")],
            [SmartPayNetworkFeeItem(network="acp", asset_symbol="ACP", amount=_DEFAULT_MIN_FEE_ACP)],
        )
    if intent.network == "bsc" and (intent.asset.symbol or "").upper() == "USDT" and source in {"ACP", "WACP", "USDT"}:
        if source == "USDT":
            route = [SmartPayRouteStep(kind="transfer", network="bsc", dex_or_rail=None, from_asset="USDT", to_asset="USDT", estimated_out=intent.amount.value if intent.amount else "0")]
            mode = "direct_send"
        elif source == "WACP":
            route = [
                SmartPayRouteStep(kind="swap", network="bsc", dex_or_rail="ancap_router_v1", from_asset="wACP", to_asset="USDT", estimated_out=intent.amount.value if intent.amount else "0"),
                SmartPayRouteStep(kind="transfer", network="bsc", dex_or_rail=None, from_asset="USDT", to_asset="USDT", estimated_out=intent.amount.value if intent.amount else "0"),
            ]
            mode = "swap_then_send"
        else:
            # Indicative: lock face ACP equal to USDT target → mint 10× wACP (bridge 1↔10).
            target = Decimal(str(intent.amount.value if intent.amount else "0"))
            wacp_bridged = format((target * Decimal(WACP_PER_ACP)).normalize(), "f")
            usdt_out = intent.amount.value if intent.amount else "0"
            route = [
                SmartPayRouteStep(
                    kind="bridge",
                    network="acp",
                    dex_or_rail="ancap_bridge_v1",
                    from_asset="ACP",
                    to_asset="wACP",
                    estimated_out=wacp_bridged,
                ),
                SmartPayRouteStep(
                    kind="swap",
                    network="bsc",
                    dex_or_rail="ancap_router_v1",
                    from_asset="wACP",
                    to_asset="USDT",
                    estimated_out=usdt_out,
                ),
                SmartPayRouteStep(
                    kind="transfer",
                    network="bsc",
                    dex_or_rail=None,
                    from_asset="USDT",
                    to_asset="USDT",
                    estimated_out=usdt_out,
                ),
            ]
            mode = "swap_then_send"
        return (
            mode,
            route,
            [
                SmartPayNetworkFeeItem(network="acp", asset_symbol="ACP", amount=_DEFAULT_MIN_FEE_ACP),
                SmartPayNetworkFeeItem(network="bsc", asset_symbol="BNB", amount=str(_BSC_NETWORK_FEE_BNB)),
            ],
        )
    if intent.network == "bsc" and (intent.asset.symbol or "").upper() == "SACP" and source in {"ACP", "SACP"}:
        if source == "SACP":
            route = [
                SmartPayRouteStep(
                    kind="transfer",
                    network="bsc",
                    dex_or_rail=None,
                    from_asset="sACP",
                    to_asset="sACP",
                    estimated_out=intent.amount.value if intent.amount else "0",
                )
            ]
            mode = "direct_send"
        else:
            route = [
                SmartPayRouteStep(
                    kind="mint",
                    network="bsc",
                    dex_or_rail="sacp_rail_v1",
                    from_asset="ACP",
                    to_asset="sACP",
                    estimated_out=intent.amount.value if intent.amount else "0",
                ),
                SmartPayRouteStep(
                    kind="transfer",
                    network="bsc",
                    dex_or_rail=None,
                    from_asset="sACP",
                    to_asset="sACP",
                    estimated_out=intent.amount.value if intent.amount else "0",
                ),
            ]
            mode = "mint_then_send"
        return (
            mode,
            route,
            [
                SmartPayNetworkFeeItem(network="acp", asset_symbol="ACP", amount=_DEFAULT_MIN_FEE_ACP),
                SmartPayNetworkFeeItem(network="bsc", asset_symbol="BNB", amount=str(_BSC_NETWORK_FEE_BNB)),
            ],
        )
    raise HTTPException(status_code=422, detail="Unsupported route for current Smart Pay scope")


def _required_source_amount(intent: PaymentIntentResponseItem, preferred_asset: str) -> str:
    target_amount = _intent_target_amount(intent)
    asset_symbol = (intent.asset.symbol or "").upper()
    source = preferred_asset.upper()
    if intent.network == "acp" and asset_symbol == "ACP" and source == "ACP":
        return _quantize_up(target_amount + Decimal(_DEFAULT_MIN_FEE_ACP) + _SERVICE_FEE_ACP, "0.00000001")
    if intent.network == "bsc" and asset_symbol == "USDT":
        if source == "USDT":
            return _quantize_up(target_amount, "0.000001")
        if source == "WACP":
            return _quantize_up(target_amount / Decimal("0.98"), "0.00000001")
        if source == "ACP":
            return _quantize_up(target_amount / _ACP_TO_USDT_RATE, "0.00000001")
    if intent.network == "bsc" and asset_symbol == "SACP":
        from app.services import sacp as sacp_svc

        if source == "SACP":
            return _quantize_up(target_amount, "0.00000001")
        if source == "ACP":
            return _quantize_up(sacp_svc.indicative_acp_for_sacp(target_amount), "0.00000001")
    raise HTTPException(status_code=422, detail="Unsupported quote source/target pair")


def _build_quote(intent: PaymentIntentResponseItem, body: SmartPayQuoteRequest) -> SmartPayQuoteItem:
    s = get_settings()
    preferred = body.source_preference.preferred_asset.upper()
    allowed = {a.upper() for a in body.source_preference.allowed_assets}
    if allowed and preferred not in allowed:
        raise HTTPException(status_code=422, detail="preferredAsset must be present in allowedAssets")
    min_reserve = Decimal(str(body.source_preference.min_acp_fee_reserve or s.mobile_smart_pay_min_acp_fee_reserve))
    required_fee_reserve = Decimal(str(s.mobile_smart_pay_min_acp_fee_reserve))
    if min_reserve < required_fee_reserve:
        raise HTTPException(status_code=409, detail="ACP fee reserve below required minimum")
    source_asset = _source_asset_for_symbol(preferred)
    target_asset = _target_asset_from_intent(intent)
    mode, route, network_fee = _build_quote_route(intent, preferred)
    quote = SmartPayQuoteItem(
        quote_id=f"q_{uuid4().hex}",
        payment_intent_id=intent.id,
        mode=mode,
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=_QUOTE_TTL_MINUTES)).isoformat().replace("+00:00", "Z"),
        source_asset=source_asset,
        target_asset=target_asset,
        target_amount=str(intent.amount.value if intent.amount else "0"),
        required_source_amount=_required_source_amount(intent, preferred),
        service_fee_acp=str(_SERVICE_FEE_ACP),
        network_fee=network_fee,
        slippage_bps=min(int(body.source_preference.max_slippage_bps), int(s.mobile_smart_pay_max_slippage_bps)),
        route=route,
        warnings=list(intent.warnings),
        risk_flags=list(intent.risk_flags),
    )
    _SMART_PAY_QUOTES[quote.quote_id] = quote
    return quote


def _route_summary(quote: SmartPayQuoteItem) -> list[str]:
    summary: list[str] = []
    for index, step in enumerate(quote.route, start=1):
        via = f" via {step.dex_or_rail}" if step.dex_or_rail else ""
        summary.append(f"{index}. {step.kind} {step.from_asset} -> {step.to_asset} on {step.network}{via}")
    return summary


def _tx_role_for_route_step(step: SmartPayRouteStep, index: int, total_steps: int) -> str:
    if step.kind == "bridge":
        return "bridge"
    if step.kind == "swap":
        return "swap"
    if step.kind == "transfer" and total_steps > 1 and index == total_steps:
        return "merchant_payout"
    if step.kind == "transfer":
        return "payment"
    return step.kind


def _explorer_url_for_network(network: str, txid: str) -> str | None:
    s = get_settings()
    if network == "acp":
        base = (s.acp_explorer_tx_base or "").strip().rstrip("/")
        return f"{base}/{txid}" if base else None
    if network == "bsc":
        base = (s.bsc_explorer_base or "").strip().rstrip("/")
        return f"{base}/tx/{txid}" if base else None
    return None


def _trim_recovery_locator_token(value: str) -> str:
    trimmed = value.strip()
    trimmed = re.sub(r'^["\'`<([{]+', "", trimmed)
    trimmed = re.sub(r'["\'`>)}\],;:.]+$', "", trimmed)
    return trimmed


def _looks_like_recovery_locator(value: str) -> bool:
    return bool(
        _RECOVERY_URL_SCHEME_RE.match(value)
        or value.lower().startswith("www.")
        or _RECOVERY_URL_HOST_RE.match(value)
        or any(marker in value for marker in ("/", "?", "#"))
    )


def _parse_recovery_locator_url(value: str):
    candidate = _trim_recovery_locator_token(value)
    if not candidate:
        return None

    if _RECOVERY_URL_SCHEME_RE.match(candidate):
        normalized_candidate = candidate
    elif candidate.lower().startswith("www.") or _RECOVERY_URL_HOST_RE.match(candidate):
        normalized_candidate = f"https://{candidate}"
    else:
        return None

    parsed = urlparse(normalized_candidate)
    if not parsed.scheme or not parsed.netloc:
        return None
    return parsed


def _infer_recovery_locator_network(parsed_url) -> str | None:
    hostname = parsed_url.netloc.lower()
    pathname = parsed_url.path.lower()

    if "bscscan.com" in hostname:
        return "bsc"

    if "ancap.cloud" in hostname and (
        "/acp/tx" in pathname
        or "/acp/transactions" in pathname
        or "/explorer/tx" in pathname
    ):
        return "acp"

    return None


def _extract_recovery_locator_ref(value: str) -> tuple[str, str | None, str | None] | None:
    parsed_url = _parse_recovery_locator_url(value)
    if parsed_url is None:
        return None

    params = parse_qs(parsed_url.query, keep_blank_values=False)
    for key in _RECOVERY_URL_QUERY_KEYS:
        raw_txid = params.get(key, [None])[0]
        if not isinstance(raw_txid, str):
            continue
        txid = _trim_recovery_locator_token(unquote(raw_txid))
        if txid:
            return txid, _infer_recovery_locator_network(parsed_url), parsed_url.geturl()

    path_segments = [
        segment
        for segment in (
            _trim_recovery_locator_token(unquote(item))
            for item in parsed_url.path.split("/")
        )
        if segment
    ]
    for index, segment in enumerate(path_segments):
        if segment.lower() not in _RECOVERY_URL_PATH_MARKERS:
            continue
        if index + 1 >= len(path_segments):
            continue
        txid = path_segments[index + 1]
        if txid:
            return txid, _infer_recovery_locator_network(parsed_url), parsed_url.geturl()

    return None


def _normalize_client_known_txid_or_locator(
    value: object,
) -> tuple[str, str | None, str | None] | None:
    if not isinstance(value, str):
        return None

    trimmed = _trim_recovery_locator_token(value)
    if not trimmed:
        return None

    locator_ref = _extract_recovery_locator_ref(trimmed)
    if locator_ref is not None:
        return locator_ref

    if _looks_like_recovery_locator(trimmed):
        return None

    return trimmed, None, None


def _normalize_route_step_index(value: object, total_steps: int) -> int | None:
    if total_steps <= 0:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        step_index = value
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if not stripped.isdigit():
            return None
        step_index = int(stripped)
    else:
        return None
    if step_index < 1 or step_index > total_steps:
        return None
    return step_index


def _normalize_client_known_ref_payload(
    ref: object, total_steps: int
) -> tuple[str, str | None, str | None, str | None, int | None] | None:
    if isinstance(ref, str):
        normalized = _normalize_client_known_txid_or_locator(ref)
        if normalized is None:
            return None
        txid, network, explorer_url = normalized
        return txid, network, None, explorer_url, None

    if ref is None:
        return None

    normalized_txid = _normalize_client_known_txid_or_locator(getattr(ref, "txid", None))
    if normalized_txid is None:
        return None

    txid, inferred_network, inferred_explorer_url = normalized_txid
    network = getattr(ref, "network", None)
    role = getattr(ref, "role", None)
    explorer_url_value = getattr(ref, "explorer_url", None)
    explorer_url = inferred_explorer_url

    if isinstance(explorer_url_value, str) and explorer_url_value.strip():
        normalized_explorer_ref = _extract_recovery_locator_ref(explorer_url_value)
        if normalized_explorer_ref is not None:
            explorer_txid, explorer_network, normalized_explorer_url = normalized_explorer_ref
            if explorer_txid.lower() == txid.lower():
                explorer_url = normalized_explorer_url
                if inferred_network is None:
                    inferred_network = explorer_network

    return (
        txid,
        network.strip() if isinstance(network, str) and network.strip() else inferred_network,
        role.strip() if isinstance(role, str) and role.strip() else None,
        explorer_url,
        _normalize_route_step_index(getattr(ref, "route_step_index", None), total_steps),
    )


def _normalized_ref_metadata_score(
    normalized_ref: tuple[str, str | None, str | None, str | None, int | None]
) -> int:
    _, network, role, explorer_url, route_step_index = normalized_ref
    score = 0
    if network:
        score += 1
    if role:
        score += 1
    if explorer_url:
        score += 1
    if route_step_index is not None:
        score += 1
    return score


def _merge_duplicate_normalized_ref(
    existing: tuple[str, str | None, str | None, str | None, int | None],
    incoming: tuple[str, str | None, str | None, str | None, int | None],
    *,
    existing_priority: int,
    incoming_priority: int,
) -> tuple[tuple[str, str | None, str | None, str | None, int | None], int]:
    existing_score = _normalized_ref_metadata_score(existing)
    incoming_score = _normalized_ref_metadata_score(incoming)

    if incoming_priority > existing_priority:
        return incoming, incoming_priority
    if incoming_priority < existing_priority:
        return existing, existing_priority
    if incoming_score > existing_score:
        return incoming, incoming_priority
    return existing, existing_priority


def _build_client_known_fallback_tx_ref(
    txid: str,
    network: str | None,
    role: str | None,
    explorer_url: str | None,
    route_step_index: int | None,
) -> SmartPayTxRef:
    normalized_network = network or "unknown"
    normalized_role = role or "client_known"
    return SmartPayTxRef(
        role=normalized_role,
        network=normalized_network,
        txid=txid,
        explorer_url=explorer_url or _explorer_url_for_network(normalized_network, txid),
        route_step_index=route_step_index,
    )


def _normalize_execution_tx_refs(
    quote: SmartPayQuoteItem,
    refs: list[object],
    *,
    existing_tx_ref_count: int = 0,
) -> list[SmartPayTxRef]:
    normalized_refs_by_txid: dict[str, tuple[tuple[str, str | None, str | None, str | None, int | None], int]] = {}
    total_steps = len(quote.route)

    for index, ref in enumerate(refs):
        normalized = _normalize_client_known_ref_payload(ref, total_steps)
        if not normalized:
            continue
        txid, _, _, _, _ = normalized
        key = txid.lower()
        priority = 1 if index < existing_tx_ref_count else 0
        if index >= existing_tx_ref_count and not isinstance(ref, str):
            priority = 2
        existing = normalized_refs_by_txid.get(key)
        if existing is None:
            normalized_refs_by_txid[key] = (normalized, priority)
            continue
        merged, merged_priority = _merge_duplicate_normalized_ref(
            existing[0],
            normalized,
            existing_priority=existing[1],
            incoming_priority=priority,
        )
        normalized_refs_by_txid[key] = (merged, merged_priority)

    normalized_refs = [item[0] for item in normalized_refs_by_txid.values()]

    route_roles = [
        _tx_role_for_route_step(step, index, total_steps)
        for index, step in enumerate(quote.route, start=1)
    ]
    route_refs: list[SmartPayTxRef | None] = [None] * total_steps
    sequential_refs: list[tuple[str, str | None, str | None, str | None, int | None]] = []
    extra_refs: list[SmartPayTxRef] = []

    for txid, network, role, explorer_url, route_step_index in normalized_refs:
        preferred_indices: list[int] = []
        if route_step_index is not None:
            preferred_indices.append(route_step_index - 1)
        elif role and network:
            preferred_indices.extend(
                step_index
                for step_index, step in enumerate(quote.route)
                if step_index not in preferred_indices
                and route_roles[step_index] == role
                and step.network == network
            )
        elif network:
            preferred_indices.extend(
                step_index
                for step_index, step in enumerate(quote.route)
                if step_index not in preferred_indices and step.network == network
            )
        elif role:
            preferred_indices.extend(
                step_index
                for step_index, step in enumerate(quote.route)
                if step_index not in preferred_indices and route_roles[step_index] == role
            )

        matched = False
        for step_index in preferred_indices:
            if route_refs[step_index] is not None:
                continue
            step = quote.route[step_index]
            step_role = route_roles[step_index]
            if role and step_role != role:
                continue
            if network and step.network != network:
                continue
            route_refs[step_index] = SmartPayTxRef(
                role=step_role,
                network=step.network,
                txid=txid,
                explorer_url=explorer_url or _explorer_url_for_network(step.network, txid),
                route_step_index=step_index + 1,
            )
            matched = True
            break

        if matched:
            continue

        if role or network or route_step_index is not None:
            extra_refs.append(
                _build_client_known_fallback_tx_ref(txid, network, role, explorer_url, route_step_index)
            )
            continue

        sequential_refs.append((txid, network, role, explorer_url, route_step_index))

    sequential_index = 0
    for step_index, step in enumerate(quote.route):
        if route_refs[step_index] is not None:
            continue
        if sequential_index >= len(sequential_refs):
            break
        txid, network, role, explorer_url, route_step_index = sequential_refs[sequential_index]
        sequential_index += 1
        step_role = route_roles[step_index]
        step_network = step.network
        route_refs[step_index] = SmartPayTxRef(
            role=step_role,
            network=step_network,
            txid=txid,
            explorer_url=explorer_url or _explorer_url_for_network(step_network, txid),
            route_step_index=route_step_index if route_step_index is not None else step_index + 1,
        )

    while sequential_index < len(sequential_refs):
        txid, network, role, explorer_url, route_step_index = sequential_refs[sequential_index]
        sequential_index += 1
        extra_refs.append(_build_client_known_fallback_tx_ref(txid, network, role, explorer_url, route_step_index))

    return [ref for ref in route_refs if ref is not None] + extra_refs


def _match_tx_refs_to_route_steps(
    quote: SmartPayQuoteItem, tx_refs: list[SmartPayTxRef]
) -> tuple[list[SmartPayTxRef | None], list[SmartPayTxRef]]:
    total_steps = len(quote.route)
    if total_steps == 0:
        return [], list(tx_refs)

    route_roles = [
        _tx_role_for_route_step(step, index, total_steps)
        for index, step in enumerate(quote.route, start=1)
    ]
    route_refs: list[SmartPayTxRef | None] = [None] * total_steps
    unmatched_refs = list(tx_refs)

    for step_index, step in enumerate(quote.route):
        role = route_roles[step_index]
        explicit_match_index = next(
            (
                index
                for index, candidate in enumerate(unmatched_refs)
                if candidate.route_step_index == step_index + 1
                and candidate.role == role
                and candidate.network == step.network
            ),
            None,
        )
        fallback_match_index = next(
            (
                index
                for index, candidate in enumerate(unmatched_refs)
                if candidate.route_step_index is None
                and candidate.role == role
                and candidate.network == step.network
            ),
            None,
        )
        match_index = explicit_match_index if explicit_match_index is not None else fallback_match_index
        if match_index is None:
            continue
        route_refs[step_index] = unmatched_refs.pop(match_index)

    return route_refs, unmatched_refs


def _build_execution_progress(quote: SmartPayQuoteItem, tx_refs: list[SmartPayTxRef]) -> SmartPayExecutionProgress:
    total_steps = len(quote.route)
    if total_steps == 0:
        observed_tx_count = len(tx_refs)
        normalized_total_steps = max(observed_tx_count, 1)
        return SmartPayExecutionProgress(
            total_route_steps=normalized_total_steps,
            observed_tx_count=observed_tx_count,
            remaining_route_steps=max(normalized_total_steps - observed_tx_count, 0),
            pending_roles=[],
        )

    route_refs, _ = _match_tx_refs_to_route_steps(quote, tx_refs)
    observed_tx_count = sum(1 for ref in route_refs if ref is not None)
    pending_roles = [
        _tx_role_for_route_step(step, index, total_steps)
        for index, step in enumerate(quote.route, start=1)
        if route_refs[index - 1] is None
    ]
    return SmartPayExecutionProgress(
        total_route_steps=total_steps,
        observed_tx_count=observed_tx_count,
        remaining_route_steps=max(total_steps - observed_tx_count, 0),
        pending_roles=pending_roles,
    )


def _execution_lifecycle_state(
    quote: SmartPayQuoteItem, tx_refs: list[SmartPayTxRef]
) -> tuple[str, bool, str | None, SmartPayExecutionProgress]:
    progress = _build_execution_progress(quote, tx_refs)
    if not tx_refs:
        next_action = "sign_direct_send_tx" if quote.mode == "direct_send" else "sign_swap_tx"
        return "awaiting_local_signature", True, next_action, progress
    # Client-provided tx hashes/explorer links are observations, not settlement proof.
    # Full route reference coverage must NOT imply chain-confirmed execution.
    # A trusted network verification path must be added before returning "completed".
    return "pending_reconciliation", True, None, progress


def _build_receipt(intent: PaymentIntentResponseItem, quote: SmartPayQuoteItem, execution: SmartPayExecutionItem) -> SmartPayReceiptItem:
    completed_at = (
        execution.updated_at or execution.created_at or _utc_now_iso()
    ) if execution.status == "completed" else None
    merchant_label = intent.merchant.label if intent.merchant and intent.merchant.label else None
    return SmartPayReceiptItem(
        id=f"spr_{execution.id}",
        payment_execution_id=execution.id,
        payment_intent_id=intent.id,
        completed_at=completed_at,
        source_asset_spent=quote.source_asset.symbol,
        source_amount_spent=quote.required_source_amount,
        target_asset_paid=quote.target_asset.symbol,
        target_amount_paid=quote.target_amount,
        service_fee_acp=quote.service_fee_acp,
        network_fees=list(quote.network_fee),
        recipient_address=intent.recipient.address,
        merchant_label=merchant_label,
        route_summary=_route_summary(quote),
        tx_refs=list(execution.tx_refs),
    )


def _store_execution_and_receipt(intent: PaymentIntentResponseItem, quote: SmartPayQuoteItem, execution: SmartPayExecutionItem) -> SmartPayExecutionItem:
    _SMART_PAY_EXECUTIONS[execution.id] = execution
    _SMART_PAY_RECEIPTS[execution.id] = _build_receipt(intent, quote, execution)
    return execution


def _build_payment_history_entry(execution: SmartPayExecutionItem) -> SmartPayPaymentHistoryEntry:
    intent = _get_payment_intent_or_404(execution.payment_intent_id)
    quote = _get_quote_or_404(execution.quote_id)
    receipt = _SMART_PAY_RECEIPTS.get(execution.id)
    if receipt is None:
        receipt = _build_receipt(intent, quote, execution)
        _SMART_PAY_RECEIPTS[execution.id] = receipt
    return SmartPayPaymentHistoryEntry(
        execution=execution,
        receipt=receipt,
        payment_intent=intent,
        quote=quote,
    )


def _build_route_execution_plan(
    intent: PaymentIntentResponseItem,
    quote: SmartPayQuoteItem,
) -> list[SmartPayRouteExecutionStep]:
    recipient = intent.recipient.address if intent.recipient else None
    plan: list[SmartPayRouteExecutionStep] = []
    for index, step in enumerate(quote.route, start=1):
        action = step.kind if step.kind in {"bridge", "swap", "transfer"} else "payment"
        signing_hint = {
            "bridge": "Sign bridge deposit/claim transaction locally",
            "swap": "Sign swap transaction locally via configured DEX/router",
            "transfer": "Sign transfer transaction locally from wallet",
            "payment": "Sign final payment transaction locally",
        }.get(action, "Sign transaction locally")
        amount = step.estimated_out or (intent.amount.value if intent.amount else None)
        plan.append(
            SmartPayRouteExecutionStep(
                step_index=index,
                action=action,  # type: ignore[arg-type]
                network=step.network,
                from_asset=step.from_asset,
                to_asset=step.to_asset,
                amount=amount,
                recipient=recipient if action in {"transfer", "payment"} else None,
                status="ready",
                signing_hint=signing_hint,
            )
        )
    return plan


def _build_execution(intent: PaymentIntentResponseItem, quote: SmartPayQuoteItem) -> SmartPayExecutionItem:
    status, recoverable, next_action, progress = _execution_lifecycle_state(quote, [])
    execution = SmartPayExecutionItem(
        id=f"pe_{uuid4().hex}",
        payment_intent_id=intent.id,
        quote_id=quote.quote_id,
        status=status,
        created_at=_utc_now_iso(),
        updated_at=_utc_now_iso(),
        recoverable=recoverable,
        next_action=next_action,
        progress=progress,
        route_plan=_build_route_execution_plan(intent, quote),
        tx_refs=[],
        error=None,
    )
    return _store_execution_and_receipt(intent, quote, execution)


@router.get("/mobile/config", response_model=MobileConfigResponse)
async def mobile_config():
    s = get_settings()
    rpc_status = _acp_rpc_status()
    bridge_status = _bridge_status_label()
    maintenance = bool(s.mobile_wallet_maintenance) or rpc_status == "unconfigured"
    message = s.mobile_wallet_maintenance_message if maintenance else None
    if maintenance and not message and rpc_status == "unconfigured":
        message = "ACP network RPC is not configured."

    reverse_enabled = bool(
        s.bridge_rail_enabled
        and not s.bridge_rail_paused
        and s.mobile_wallet_bridge_reverse_enabled
    )

    return MobileConfigResponse(
        min_app_version=s.mobile_wallet_min_app_version,
        maintenance=maintenance,
        maintenance_message=message,
        acp_decimals=8,
        wacp_decimals=18,
        acp_rpc_status=rpc_status,
        bridge_status=bridge_status,
        bridge_enabled=bool(s.bridge_rail_enabled),
        bridge_paused=bool(s.bridge_rail_paused),
        bridge_reverse_enabled=reverse_enabled,
        wacp_contract=(s.bridge_wacp_contract or "").strip(),
        bsc_chain_id=56,
        acp_rpc_url=(s.acp_rpc_url or "").strip(),
        bsc_rpc_url=(s.bridge_bsc_rpc_url or "").strip(),
        acp_explorer_tx_base=(s.acp_explorer_tx_base or "https://ancap.cloud/explorer/tx").rstrip("/"),
        bsc_explorer_base=(s.bsc_explorer_base or "https://bscscan.com").rstrip("/"),
        support_url=(s.mobile_wallet_support_url or "https://ancap.cloud/support").strip(),
        docs=_public_docs(),
    )


@router.get("/acp/network/status", response_model=AcpNetworkStatusResponse)
async def acp_network_status():
    settings = get_settings()
    rpc = (settings.acp_rpc_url or "").strip()
    if not rpc:
        return AcpNetworkStatusResponse(rpc_status="unconfigured", block_height=None, min_fee_acp=_DEFAULT_MIN_FEE_ACP)
    try:
        height = wallet_acp._rpc_call(rpc, "getblockcount", [])
        block_height = int(height) if height is not None else None
        status = "ok"
    except HTTPException:
        block_height = None
        status = "degraded"
    return AcpNetworkStatusResponse(
        rpc_status=status,
        block_height=block_height,
        min_fee_acp=_DEFAULT_MIN_FEE_ACP,
    )


@router.get("/acp/address/{address}/balance", response_model=MobileAcpBalanceResponse)
async def acp_address_balance(address: str):
    target = wallet_acp._validate_acp_address(address, "address")
    try:
        raw = wallet_acp._load_balance_result(target)
    except HTTPException as exc:
        if exc.status_code in (502, 503, 504):
            return MobileAcpBalanceResponse(address=target, units="0", acp="0", utxo_count=0)
        raise
    return MobileAcpBalanceResponse(
        address=str(raw.get("address") or target),
        units=str(raw.get("units") or "0"),
        acp=str(raw.get("acp") or "0"),
        utxo_count=int(raw.get("utxo_count") or 0),
    )


@router.get("/acp/address/{address}/transactions", response_model=list[AcpTransactionPublic])
async def acp_address_transactions(
    address: str,
    limit: int = Query(default=50, ge=1, le=500),
):
    target = wallet_acp._validate_acp_address(address, "address")
    try:
        rows, _warming = wallet_acp._chain_transactions_for_address(target, limit)
        return rows
    except HTTPException as exc:
        if exc.status_code in (502, 503, 504):
            return []
        raise


@router.get("/acp/transactions/{txid}", response_model=AcpTransactionDetailsPublic)
async def acp_transaction_by_id(txid: str):
    txid_norm = (txid or "").strip()
    if len(txid_norm) < 32:
        raise HTTPException(status_code=400, detail="txid looks invalid")
    try:
        details = wallet_acp._chain_transaction_details(txid_norm)
    except HTTPException as exc:
        if exc.status_code in (502, 503, 504):
            raise HTTPException(status_code=503, detail="ACP transaction lookup is temporarily unavailable") from exc
        raise
    if details is None:
        raise HTTPException(status_code=404, detail="ACP transaction not found")
    return details


@router.post("/acp/tx/estimate-fee", response_model=AcpFeeEstimateResponse)
async def acp_estimate_fee(body: AcpFeeEstimateRequest):
    wallet_acp._validate_acp_address(body.from_address, "from")
    wallet_acp._validate_acp_address(body.to_address, "to")
    wallet_acp._parse_positive_decimal(body.amount_acp, "amountAcp")
    return AcpFeeEstimateResponse(
        fee_acp=_DEFAULT_MIN_FEE_ACP,
        fee_units=_DEFAULT_MIN_FEE_UNITS,
        min_fee_acp=_DEFAULT_MIN_FEE_ACP,
    )


@router.post("/acp/tx/broadcast", response_model=AcpBroadcastResponse)
async def acp_broadcast(
    request: Request,
    body: AcpBroadcastRequest,
    session: DbSession,
    user_id: str | None = Depends(get_current_user_id),
    device_token: str | None = Header(default=None, alias="X-Device-Token"),
):
    s = get_settings()

    # Broadcast is not an open relay: require an authenticated user or a
    # registered active mobile device (registration itself requires auth).
    caller_scope: str | None = None
    if user_id:
        caller_scope = f"user:{user_id}"
    elif device_token:
        row = await session.execute(
            select(MobileDevice).where(
                MobileDevice.device_token == device_token.strip(),
                MobileDevice.is_active == True,  # noqa: E712
            )
        )
        device = row.scalars().first()
        if device is not None:
            caller_scope = f"device:{device.id}"
    if caller_scope is None:
        raise HTTPException(
            status_code=401,
            detail="Broadcast requires authentication or a registered device (X-Device-Token)",
        )

    ip = get_request_ip(request)
    await enforce_rate_limit(
        key=f"mobile:broadcast:{ip}",
        limit=s.mobile_broadcast_rate_limit_per_minute,
        window_seconds=60,
    )
    await enforce_rate_limit(
        key=f"mobile:broadcast:{caller_scope}",
        limit=s.mobile_broadcast_rate_limit_per_minute,
        window_seconds=60,
    )

    raw = (body.raw_tx or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="rawTx is required")
    if raw.startswith("0x") or raw.startswith("0X"):
        raw = raw[2:]
    if len(raw) < 32 or len(raw) > 2_000_000:
        raise HTTPException(status_code=400, detail="rawTx length is invalid")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="rawTx must be hexadecimal") from exc

    rpc = wallet_acp._require_acp_rpc_url()
    try:
        result = wallet_acp._rpc_call(rpc, "sendrawtransaction", {"tx": raw})
    except HTTPException as exc:
        if exc.status_code == 502:
            raise HTTPException(status_code=503, detail="ACP broadcast is temporarily unavailable") from exc
        raise

    if not isinstance(result, dict):
        raise HTTPException(status_code=502, detail="ACP RPC returned unexpected broadcast result")

    accepted = bool(result.get("accepted"))
    txid = result.get("txid")
    if isinstance(txid, str):
        txid = txid.strip() or None
    else:
        txid = None
    reason = result.get("reason")
    if isinstance(reason, str):
        reason = reason.strip() or None
    else:
        reason = None

    return AcpBroadcastResponse(accepted=accepted, txid=txid, reason=reason)


@router.get("/mobile/smart-pay/capabilities", response_model=SmartPayCapabilitiesResponse)
async def smart_pay_capabilities():
    s = get_settings()
    return SmartPayCapabilitiesResponse(
        enabled=bool(s.mobile_smart_pay_enabled),
        smart_qr_parse_enabled=True,
        smart_qr_ai_fallback_enabled=bool(s.mobile_smart_pay_ai_fallback_enabled),
        auto_swap_enabled=bool(s.mobile_smart_pay_auto_swap_enabled),
        supported_networks=["acp", "bsc"],
        supported_assets=_supported_assets(),
        max_image_bytes=int(s.mobile_smart_pay_max_image_bytes),
        max_slippage_bps=int(s.mobile_smart_pay_max_slippage_bps),
        min_acp_fee_reserve=str(s.mobile_smart_pay_min_acp_fee_reserve),
    )


@router.post("/mobile/smart-pay/parse", response_model=SmartQrParseResponse)
async def smart_pay_parse(body: SmartQrParseRequest, session: DbSession):
    intent = _parse_smart_qr_payload(body.source, body.raw_payload)
    await _persist_smart_pay_record(session, record_id=intent.id, kind="intent", payload_model=intent)
    return SmartQrParseResponse(payment_intent=intent)


@router.post("/mobile/smart-pay/quote", response_model=SmartPayQuoteResponse)
async def smart_pay_quote(body: SmartPayQuoteRequest, session: DbSession):
    intent = await _hydrate_intent(session, body.payment_intent_id)
    if intent is None:
        raise HTTPException(status_code=404, detail="paymentIntentId not found")
    quote = _build_quote(intent, body)
    await _persist_smart_pay_record(session, record_id=quote.quote_id, kind="quote", payload_model=quote)
    return SmartPayQuoteResponse(quote=quote)


@router.post("/mobile/smart-pay/execute", response_model=SmartPayExecutionResponse)
async def smart_pay_execute(
    body: SmartPayExecuteRequest,
    session: DbSession,
    user_id: str = Depends(require_auth),
):
    if not body.confirmation_accepted:
        raise HTTPException(status_code=400, detail="confirmationAccepted must be true")
    intent = await _hydrate_intent(session, body.payment_intent_id)
    if intent is None:
        raise HTTPException(status_code=404, detail="paymentIntentId not found")
    quote = await _hydrate_quote(session, body.quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="quoteId not found")
    if quote.payment_intent_id != intent.id:
        raise HTTPException(status_code=409, detail="quote does not belong to payment intent")
    execution = _build_execution(intent, quote)
    session_token = _new_session_token()
    _SMART_PAY_EXECUTION_OWNERS[execution.id] = user_id
    _SMART_PAY_EXECUTION_SESSION_TOKENS[execution.id] = session_token
    await _persist_execution_bundle(
        session,
        intent=intent,
        quote=quote,
        execution=execution,
        owner_user_id=user_id,
        session_token=session_token,
    )
    return SmartPayExecutionResponse(execution=execution, session_token=session_token)


@router.get("/mobile/smart-pay/payments", response_model=SmartPayPaymentHistoryResponse)
async def smart_pay_payment_history(
    session: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(require_auth),
):
    rows = await session.execute(
        select(MobileSmartPayRecord)
        .where(
            MobileSmartPayRecord.kind == "execution",
            MobileSmartPayRecord.owner_user_id == user_id,
        )
        .order_by(MobileSmartPayRecord.updated_at.desc())
        .limit(limit)
    )
    payments: list[SmartPayPaymentHistoryEntry] = []
    for record in rows.scalars().all():
        execution = await _hydrate_execution(session, record.id)
        if execution is None:
            continue
        # Ensure the sync history builder finds intent/quote/receipt in cache.
        if await _hydrate_intent(session, execution.payment_intent_id) is None:
            continue
        if await _hydrate_quote(session, execution.quote_id) is None:
            continue
        await _hydrate_receipt(session, execution.id)
        payments.append(_build_payment_history_entry(execution))
    return SmartPayPaymentHistoryResponse(payments=payments)


@router.get("/mobile/smart-pay/payments/{execution_id}", response_model=SmartPayExecutionResponse)
async def smart_pay_payment_status(
    execution_id: str,
    session: DbSession,
    session_token: str | None = Query(default=None, alias="sessionToken"),
    user_id: str | None = Depends(get_current_user_id),
):
    execution = await _hydrate_execution(session, execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="execution not found")
    _require_execution_access(execution.id, user_id, session_token)
    return SmartPayExecutionResponse(execution=execution, session_token=_get_session_token(execution.id))


@router.get("/mobile/smart-pay/payments/{execution_id}/receipt", response_model=SmartPayReceiptItem)
async def smart_pay_receipt(
    execution_id: str,
    session: DbSession,
    session_token: str | None = Query(default=None, alias="sessionToken"),
    user_id: str | None = Depends(get_current_user_id),
):
    # Hydrate the execution first so ownership/session-token checks work after restart.
    execution = await _hydrate_execution(session, execution_id)
    receipt = await _hydrate_receipt(session, execution_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="receipt not found")
    _require_execution_access(execution.id if execution else execution_id, user_id, session_token)
    return receipt


@router.post("/mobile/smart-pay/payments/{execution_id}/recover", response_model=SmartPayExecutionResponse)
async def smart_pay_recover(
    execution_id: str,
    body: SmartPayRecoverRequest,
    session: DbSession,
    session_token: str | None = Query(default=None, alias="sessionToken"),
    user_id: str | None = Depends(get_current_user_id),
):
    execution = await _hydrate_execution(session, execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="execution not found")
    _require_execution_access(execution.id, user_id, session_token)
    quote = await _hydrate_quote(session, execution.quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="quoteId not found")
    intent = await _hydrate_intent(session, execution.payment_intent_id)
    if intent is None:
        raise HTTPException(status_code=404, detail="paymentIntentId not found")
    known_refs: list[object] = list(execution.tx_refs)
    existing_tx_ref_count = len(known_refs)
    known_refs.extend(body.client_known_refs)
    known_refs.extend(body.client_known_txs)
    tx_refs = _normalize_execution_tx_refs(
        quote,
        known_refs,
        existing_tx_ref_count=existing_tx_ref_count,
    )
    status, recoverable, next_action, progress = _execution_lifecycle_state(quote, tx_refs)
    execution = execution.model_copy(
        update={
            "status": status,
            "updated_at": _utc_now_iso(),
            "recoverable": recoverable,
            "next_action": next_action,
            "progress": progress,
            "tx_refs": tx_refs,
        }
    )
    _store_execution_and_receipt(intent, quote, execution)
    await _persist_execution_bundle(
        session,
        intent=intent,
        quote=quote,
        execution=execution,
        owner_user_id=_SMART_PAY_EXECUTION_OWNERS.get(execution.id),
        session_token=_get_session_token(execution.id),
    )
    return SmartPayExecutionResponse(execution=execution, session_token=_get_session_token(execution.id))


@router.get("/mobile/health")
async def mobile_health():
    return JSONResponse({"ok": True, "service": "acp-wallet-mobile-gateway"})
