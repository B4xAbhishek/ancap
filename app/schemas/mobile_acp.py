from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class SmartPaySupportedAsset(BaseModel):
    network: str
    symbol: str
    token_address: str | None = Field(default=None, serialization_alias="tokenAddress")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayCapabilitiesResponse(BaseModel):
    enabled: bool
    smart_qr_parse_enabled: bool = Field(serialization_alias="smartQrParseEnabled")
    smart_qr_ai_fallback_enabled: bool = Field(serialization_alias="smartQrAiFallbackEnabled")
    auto_swap_enabled: bool = Field(serialization_alias="autoSwapEnabled")
    supported_networks: list[str] = Field(serialization_alias="supportedNetworks")
    supported_assets: list[SmartPaySupportedAsset] = Field(serialization_alias="supportedAssets")
    max_image_bytes: int = Field(serialization_alias="maxImageBytes")
    max_slippage_bps: int = Field(serialization_alias="maxSlippageBps")
    min_acp_fee_reserve: str = Field(serialization_alias="minAcpFeeReserve")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartQrParseHint(BaseModel):
    locale: str | None = None
    platform: Literal["ios", "android"] | None = None


class SmartQrParseRequest(BaseModel):
    source: Literal["camera", "photo", "paste", "share", "ocr"]
    raw_payload: str = Field(alias="rawPayload", min_length=1, max_length=4096)
    hint: SmartQrParseHint | None = None

    model_config = ConfigDict(populate_by_name=True)


class PaymentAsset(BaseModel):
    kind: Literal["native", "erc20", "unknown"]
    symbol: str | None = None
    name: str | None = None
    token_address: str | None = Field(default=None, serialization_alias="tokenAddress")
    decimals: int | None = None
    is_supported: bool = Field(serialization_alias="isSupported")
    is_allowlisted: bool = Field(serialization_alias="isAllowlisted")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class PaymentRecipient(BaseModel):
    address: str
    resolved_display: str | None = Field(default=None, serialization_alias="resolvedDisplay")
    address_type: Literal["acp", "evm", "unknown"] = Field(serialization_alias="addressType")
    checksum_valid: bool | None = Field(default=None, serialization_alias="checksumValid")
    ens_or_alias: str | None = Field(default=None, serialization_alias="ensOrAlias")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class PaymentAmount(BaseModel):
    value: str
    atomic_value: str | None = Field(default=None, serialization_alias="atomicValue")
    currency_symbol: str | None = Field(default=None, serialization_alias="currencySymbol")
    is_exact: bool = Field(serialization_alias="isExact")
    is_max: bool = Field(serialization_alias="isMax")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class PaymentMemo(BaseModel):
    value: str
    type: Literal["memo", "tag", "reference", "note"]
    required: bool


class MerchantHint(BaseModel):
    label: str | None = None
    category: str | None = None
    website: str | None = None
    invoice_id: str | None = Field(default=None, serialization_alias="invoiceId")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class PaymentIntentMetadata(BaseModel):
    detected_standard: str | None = Field(default=None, serialization_alias="detectedStandard")
    invoice_type: str | None = Field(default=None, serialization_alias="invoiceType")
    ai_model: str | None = Field(default=None, serialization_alias="aiModel")
    ai_used: bool = Field(serialization_alias="aiUsed")
    parser_version: str = Field(serialization_alias="parserVersion")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class PaymentIntentResponseItem(BaseModel):
    id: str
    created_at: str = Field(serialization_alias="createdAt")
    source: Literal["camera", "photo", "paste", "share", "ocr"]
    raw_payload: str = Field(serialization_alias="rawPayload")
    payload_hash: str = Field(serialization_alias="payloadHash")
    parse_method: Literal["deterministic", "heuristic", "ai"] = Field(serialization_alias="parseMethod")
    confidence: float
    status: Literal["parsed", "unsupported", "needs_review", "rejected"]
    network: Literal["acp", "bsc", "base", "ethereum", "unknown"]
    asset: PaymentAsset
    recipient: PaymentRecipient
    amount: PaymentAmount | None = None
    memo: PaymentMemo | None = None
    merchant: MerchantHint | None = None
    risk_flags: list[str] = Field(default_factory=list, serialization_alias="riskFlags")
    warnings: list[str] = Field(default_factory=list)
    unsupported_reasons: list[str] = Field(default_factory=list, serialization_alias="unsupportedReasons")
    requires_user_confirmation: bool = Field(serialization_alias="requiresUserConfirmation")
    metadata: PaymentIntentMetadata

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartQrParseResponse(BaseModel):
    payment_intent: PaymentIntentResponseItem = Field(serialization_alias="paymentIntent")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPaySourcePreference(BaseModel):
    preferred_asset: str = Field(alias="preferredAsset", serialization_alias="preferredAsset", min_length=1, max_length=16)
    allowed_assets: list[str] = Field(default_factory=list, alias="allowedAssets", serialization_alias="allowedAssets")
    max_slippage_bps: int = Field(default=150, alias="maxSlippageBps", serialization_alias="maxSlippageBps", ge=0, le=5000)
    min_acp_fee_reserve: str = Field(default="1.0", alias="minAcpFeeReserve", serialization_alias="minAcpFeeReserve")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayQuoteRequest(BaseModel):
    payment_intent_id: str = Field(alias="paymentIntentId", serialization_alias="paymentIntentId", min_length=1)
    source_preference: SmartPaySourcePreference = Field(alias="sourcePreference", serialization_alias="sourcePreference")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayQuoteAsset(BaseModel):
    network: str
    symbol: str
    token_address: str | None = Field(default=None, serialization_alias="tokenAddress")
    decimals: int | None = None

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayNetworkFeeItem(BaseModel):
    network: str
    asset_symbol: str = Field(serialization_alias="assetSymbol")
    amount: str

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayRouteStep(BaseModel):
    kind: Literal["bridge", "swap", "transfer", "mint"]
    network: str
    dex_or_rail: str | None = Field(default=None, serialization_alias="dexOrRail")
    from_asset: str = Field(serialization_alias="fromAsset")
    to_asset: str = Field(serialization_alias="toAsset")
    estimated_out: str = Field(serialization_alias="estimatedOut")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayQuoteItem(BaseModel):
    quote_id: str = Field(serialization_alias="quoteId")
    payment_intent_id: str = Field(serialization_alias="paymentIntentId")
    mode: Literal["direct_send", "swap_then_send", "mint_then_send"]
    expires_at: str = Field(serialization_alias="expiresAt")
    source_asset: SmartPayQuoteAsset = Field(serialization_alias="sourceAsset")
    target_asset: SmartPayQuoteAsset = Field(serialization_alias="targetAsset")
    target_amount: str = Field(serialization_alias="targetAmount")
    required_source_amount: str = Field(serialization_alias="requiredSourceAmount")
    service_fee_acp: str = Field(serialization_alias="serviceFeeAcp")
    network_fee: list[SmartPayNetworkFeeItem] = Field(default_factory=list, serialization_alias="networkFee")
    slippage_bps: int = Field(serialization_alias="slippageBps")
    route: list[SmartPayRouteStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list, serialization_alias="riskFlags")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayQuoteResponse(BaseModel):
    quote: SmartPayQuoteItem

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayDeviceContext(BaseModel):
    platform: Literal["ios", "android"]
    app_version: str | None = Field(default=None, alias="appVersion", serialization_alias="appVersion")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayExecuteRequest(BaseModel):
    payment_intent_id: str = Field(alias="paymentIntentId", serialization_alias="paymentIntentId", min_length=1)
    quote_id: str = Field(alias="quoteId", serialization_alias="quoteId", min_length=1)
    confirmation_accepted: bool = Field(alias="confirmationAccepted", serialization_alias="confirmationAccepted")
    device_context: SmartPayDeviceContext | None = Field(default=None, alias="deviceContext", serialization_alias="deviceContext")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayTxRef(BaseModel):
    role: str
    network: str
    txid: str
    explorer_url: str | None = Field(default=None, serialization_alias="explorerUrl")
    route_step_index: int | None = Field(default=None, serialization_alias="routeStepIndex")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayExecutionProgress(BaseModel):
    total_route_steps: int = Field(serialization_alias="totalRouteSteps")
    observed_tx_count: int = Field(serialization_alias="observedTxCount")
    remaining_route_steps: int = Field(serialization_alias="remainingRouteSteps")
    pending_roles: list[str] = Field(default_factory=list, serialization_alias="pendingRoles")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayRouteExecutionStep(BaseModel):
    step_index: int = Field(serialization_alias="stepIndex")
    action: Literal["bridge", "swap", "transfer", "payment"]
    network: str
    from_asset: str = Field(serialization_alias="fromAsset")
    to_asset: str = Field(serialization_alias="toAsset")
    amount: str | None = None
    recipient: str | None = None
    status: Literal["ready", "pending", "signed", "confirmed"] = "ready"
    signing_hint: str | None = Field(default=None, serialization_alias="signingHint")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayExecutionItem(BaseModel):
    id: str
    payment_intent_id: str = Field(serialization_alias="paymentIntentId")
    quote_id: str = Field(serialization_alias="quoteId")
    status: Literal["awaiting_local_signature", "pending_reconciliation", "completed", "failed"]
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")
    recoverable: bool
    next_action: str | None = Field(default=None, serialization_alias="nextAction")
    progress: SmartPayExecutionProgress | None = None
    route_plan: list[SmartPayRouteExecutionStep] = Field(default_factory=list, serialization_alias="routePlan")
    tx_refs: list[SmartPayTxRef] = Field(default_factory=list, serialization_alias="txRefs")
    error: str | None = None

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayExecutionResponse(BaseModel):
    execution: SmartPayExecutionItem
    session_token: str | None = Field(default=None, serialization_alias="sessionToken")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayClientKnownRef(BaseModel):
    txid: str = Field(min_length=1)
    network: str | None = None
    role: str | None = None
    explorer_url: str | None = Field(default=None, alias="explorerUrl", serialization_alias="explorerUrl")
    route_step_index: int | None = Field(default=None, alias="routeStepIndex", serialization_alias="routeStepIndex")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayRecoverRequest(BaseModel):
    client_known_txs: list[str] = Field(default_factory=list, alias="clientKnownTxs", serialization_alias="clientKnownTxs")
    client_known_refs: list[SmartPayClientKnownRef] = Field(default_factory=list, alias="clientKnownRefs", serialization_alias="clientKnownRefs")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayReceiptItem(BaseModel):
    id: str
    payment_execution_id: str = Field(serialization_alias="paymentExecutionId")
    payment_intent_id: str = Field(serialization_alias="paymentIntentId")
    completed_at: str | None = Field(default=None, serialization_alias="completedAt")
    source_asset_spent: str = Field(serialization_alias="sourceAssetSpent")
    source_amount_spent: str = Field(serialization_alias="sourceAmountSpent")
    target_asset_paid: str = Field(serialization_alias="targetAssetPaid")
    target_amount_paid: str = Field(serialization_alias="targetAmountPaid")
    service_fee_acp: str = Field(serialization_alias="serviceFeeAcp")
    network_fees: list[SmartPayNetworkFeeItem] = Field(default_factory=list, serialization_alias="networkFees")
    recipient_address: str = Field(serialization_alias="recipientAddress")
    merchant_label: str | None = Field(default=None, serialization_alias="merchantLabel")
    route_summary: list[str] = Field(default_factory=list, serialization_alias="routeSummary")
    tx_refs: list[SmartPayTxRef] = Field(default_factory=list, serialization_alias="txRefs")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayPaymentHistoryEntry(BaseModel):
    execution: SmartPayExecutionItem
    receipt: SmartPayReceiptItem
    payment_intent: PaymentIntentResponseItem = Field(serialization_alias="paymentIntent")
    quote: SmartPayQuoteItem

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class SmartPayPaymentHistoryResponse(BaseModel):
    payments: list[SmartPayPaymentHistoryEntry] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class MobileDocsLinks(BaseModel):
    bridge: str
    risks: str
    reserve: str
    contracts: str
    wallet_security: str = Field(serialization_alias="walletSecurity")

    model_config = ConfigDict(populate_by_name=True)


class MobileConfigResponse(BaseModel):
    min_app_version: str = Field(serialization_alias="minAppVersion")
    maintenance: bool
    maintenance_message: str | None = Field(default=None, serialization_alias="maintenanceMessage")
    acp_decimals: int = Field(serialization_alias="acpDecimals")
    wacp_decimals: int = Field(serialization_alias="wacpDecimals")
    acp_rpc_status: str = Field(serialization_alias="acpRpcStatus")
    bridge_status: str = Field(serialization_alias="bridgeStatus")
    bridge_enabled: bool = Field(serialization_alias="bridgeEnabled")
    bridge_paused: bool = Field(serialization_alias="bridgePaused")
    bridge_reverse_enabled: bool = Field(serialization_alias="bridgeReverseEnabled")
    wacp_contract: str = Field(serialization_alias="wacpContract")
    bsc_chain_id: int = Field(serialization_alias="bscChainId")
    acp_rpc_url: str = Field(serialization_alias="acpRpcUrl")
    bsc_rpc_url: str = Field(serialization_alias="bscRpcUrl")
    acp_explorer_tx_base: str = Field(serialization_alias="acpExplorerTxBase")
    bsc_explorer_base: str = Field(serialization_alias="bscExplorerBase")
    support_url: str = Field(serialization_alias="supportUrl")
    docs: MobileDocsLinks

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class AcpNetworkStatusResponse(BaseModel):
    chain: str = "acp"
    rpc_status: str = Field(serialization_alias="rpcStatus")
    block_height: int | None = Field(default=None, serialization_alias="blockHeight")
    min_fee_acp: str = Field(serialization_alias="minFeeAcp")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class MobileAcpBalanceResponse(BaseModel):
    """On-chain balance only (no custodial in_work fields)."""

    address: str
    units: str
    acp: str
    utxo_count: int = 0


class AcpFeeEstimateRequest(BaseModel):
    from_address: Annotated[str, Field(validation_alias="from")]
    to_address: Annotated[str, Field(validation_alias="to")]
    amount_acp: Annotated[str, Field(validation_alias="amountAcp")]

    model_config = ConfigDict(populate_by_name=True)


class AcpFeeEstimateResponse(BaseModel):
    fee_acp: str = Field(serialization_alias="feeAcp")
    fee_units: str = Field(serialization_alias="feeUnits")
    min_fee_acp: str = Field(serialization_alias="minFeeAcp")

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)


class AcpBroadcastRequest(BaseModel):
    raw_tx: str = Field(alias="rawTx", min_length=16)

    model_config = ConfigDict(populate_by_name=True)


class AcpBroadcastResponse(BaseModel):
    accepted: bool
    txid: str | None = None
    reason: str | None = None


# ── Device registration ────────────────────────────────────────────────────────


class MobileDeviceInfo(BaseModel):
    device_id: str
    platform: str
    app_version: str | None = None
    is_active: bool
    last_seen_at: datetime | None = None
    created_at: datetime


class MobileDeviceRegisterRequest(BaseModel):
    device_token: str = Field(min_length=1, max_length=512, description="Push notification token from iOS (APNs) or Android (FCM)")
    platform: Literal["ios", "android"] = Field(description="Device platform")
    app_version: str | None = Field(default=None, max_length=16, description="App version string e.g. 1.0.0")


class MobileDeviceRegisterResponse(BaseModel):
    device_id: str
    registered: bool
    message: str = "Device registered"


class MobileDeviceUnregisterRequest(BaseModel):
    device_token: str = Field(min_length=1, max_length=512)


class MobileDeviceListResponse(BaseModel):
    devices: list[MobileDeviceInfo] = Field(default_factory=list)