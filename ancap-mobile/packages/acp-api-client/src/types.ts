export type MobileConfig = {
  minAppVersion: string;
  maintenance: boolean;
  maintenanceMessage: string | null;
  acpDecimals: number;
  wacpDecimals: number;
  acpRpcStatus: string;
  bridgeStatus: string;
  bridgeEnabled: boolean;
  bridgePaused: boolean;
  bridgeReverseEnabled: boolean;
  wacpContract: string;
  bscChainId: number;
  acpRpcUrl: string;
  bscRpcUrl: string;
  acpExplorerTxBase: string;
  bscExplorerBase: string;
  supportUrl: string;
  docs: {
    bridge: string;
    risks: string;
    reserve: string;
    contracts: string;
    walletSecurity: string;
  };
};

export type AcpNetworkStatus = {
  chain: "acp";
  rpcStatus: string;
  blockHeight: number | null;
  minFeeAcp: string;
};

export type MobileBalance = {
  address: string;
  units: string;
  acp: string;
  utxo_count: number;
};

export type AcpTransaction = {
  txid: string;
  block_height: number;
  block_time: string;
  confirmations: number;
  direction: "in" | "out" | "self";
  sent_units: string;
  sent_acp: string;
  received_units: string;
  received_acp: string;
  net_units: string;
  net_acp: string;
};

export type AcpTransactionIo = {
  address: string | null;
  units: string;
  acp: string;
  vout: number | null;
};

export type AcpTransactionDetails = {
  txid: string;
  block_height: number;
  block_hash: string | null;
  block_time: string;
  confirmations: number;
  total_input_units: string;
  total_input_acp: string;
  total_output_units: string;
  total_output_acp: string;
  fee_units: string;
  fee_acp: string;
  inputs: AcpTransactionIo[];
  outputs: AcpTransactionIo[];
};

export type BroadcastResult = {
  accepted: boolean;
  txid: string | null;
  reason: string | null;
};

export type MobileDevicePlatform = "ios" | "android";

export type MobileDeviceRegisterInput = {
  deviceToken: string;
  platform: MobileDevicePlatform;
  appVersion?: string | null;
};

export type MobileDeviceRegisterResponse = {
  device_id: string;
  registered: boolean;
  message: string;
};

export type MobileDeviceUnregisterResponse = {
  ok: boolean;
  message: string;
};

export type MobileDeviceInfo = {
  device_id: string;
  platform: string;
  app_version: string | null;
  is_active: boolean;
  last_seen_at: string | null;
  created_at: string;
};

export type MobileDeviceListResponse = {
  devices: MobileDeviceInfo[];
};

export type SmartPaySupportedAsset = {
  network: string;
  symbol: string;
  tokenAddress?: string | null;
};

export type SmartPayCapabilities = {
  enabled: boolean;
  smartQrParseEnabled: boolean;
  smartQrAiFallbackEnabled: boolean;
  autoSwapEnabled: boolean;
  supportedNetworks: string[];
  supportedAssets: SmartPaySupportedAsset[];
  maxImageBytes: number;
  maxSlippageBps: number;
  minAcpFeeReserve: string;
};

export type SmartQrParseInput = {
  source: "camera" | "photo" | "paste" | "share" | "ocr";
  rawPayload: string;
  hint?: {
    locale?: string | null;
    platform?: "ios" | "android" | null;
  } | null;
};

export type SmartPayPaymentAsset = {
  kind: "native" | "erc20" | "unknown";
  symbol?: string | null;
  name?: string | null;
  tokenAddress?: string | null;
  decimals?: number | null;
  isSupported: boolean;
  isAllowlisted: boolean;
};

export type SmartPayPaymentRecipient = {
  address: string;
  resolvedDisplay?: string | null;
  addressType: "acp" | "evm" | "unknown";
  checksumValid?: boolean | null;
  ensOrAlias?: string | null;
};

export type SmartPayPaymentAmount = {
  value: string;
  atomicValue?: string | null;
  currencySymbol?: string | null;
  isExact: boolean;
  isMax: boolean;
};

export type SmartPayPaymentMemo = {
  value: string;
  type: "memo" | "tag" | "reference" | "note";
  required: boolean;
};

export type SmartPayMerchantHint = {
  label?: string | null;
  category?: string | null;
  website?: string | null;
  invoiceId?: string | null;
};

export type SmartPayPaymentMetadata = {
  detectedStandard?: string | null;
  invoiceType?: string | null;
  aiModel?: string | null;
  aiUsed: boolean;
  parserVersion: string;
};

export type SmartPayPaymentIntent = {
  id: string;
  createdAt: string;
  source: "camera" | "photo" | "paste" | "share" | "ocr";
  rawPayload: string;
  payloadHash: string;
  parseMethod: "deterministic" | "heuristic" | "ai";
  confidence: number;
  status: "parsed" | "unsupported" | "needs_review" | "rejected";
  network: "acp" | "bsc" | "base" | "ethereum" | "unknown";
  asset: SmartPayPaymentAsset;
  recipient: SmartPayPaymentRecipient;
  amount?: SmartPayPaymentAmount | null;
  memo?: SmartPayPaymentMemo | null;
  merchant?: SmartPayMerchantHint | null;
  riskFlags: string[];
  warnings: string[];
  unsupportedReasons: string[];
  requiresUserConfirmation: boolean;
  metadata: SmartPayPaymentMetadata;
};

export type SmartQrParseResponse = {
  paymentIntent: SmartPayPaymentIntent;
};

export type SmartPaySourcePreference = {
  preferredAsset: string;
  allowedAssets: string[];
  maxSlippageBps?: number;
  minAcpFeeReserve?: string;
};

export type SmartPayQuoteInput = {
  paymentIntentId: string;
  sourcePreference: SmartPaySourcePreference;
};

export type SmartPayQuoteAsset = {
  network: string;
  symbol: string;
  tokenAddress?: string | null;
  decimals?: number | null;
};

export type SmartPayNetworkFeeItem = {
  network: string;
  assetSymbol: string;
  amount: string;
};

export type SmartPayRouteStep = {
  kind: "bridge" | "swap" | "transfer";
  network: string;
  dexOrRail?: string | null;
  fromAsset: string;
  toAsset: string;
  estimatedOut: string;
};

export type SmartPayQuote = {
  quoteId: string;
  paymentIntentId: string;
  mode: "direct_send" | "swap_then_send";
  expiresAt: string;
  sourceAsset: SmartPayQuoteAsset;
  targetAsset: SmartPayQuoteAsset;
  targetAmount: string;
  requiredSourceAmount: string;
  serviceFeeAcp: string;
  networkFee: SmartPayNetworkFeeItem[];
  slippageBps: number;
  route: SmartPayRouteStep[];
  warnings: string[];
  riskFlags: string[];
};

export type SmartPayQuoteResponse = {
  quote: SmartPayQuote;
};

export type SmartPayExecuteInput = {
  paymentIntentId: string;
  quoteId: string;
  confirmationAccepted: boolean;
  deviceContext?: {
    platform: "ios" | "android";
    appVersion?: string | null;
  } | null;
};

export type SmartPayTxRef = {
  role: string;
  network: string;
  txid: string;
  explorerUrl?: string | null;
  routeStepIndex?: number | null;
};

export type SmartPayExecutionProgress = {
  totalRouteSteps: number;
  observedTxCount: number;
  remainingRouteSteps: number;
  pendingRoles: string[];
};

export type SmartPayRouteExecutionStep = {
  stepIndex: number;
  action: "bridge" | "swap" | "transfer" | "payment";
  network: string;
  fromAsset: string;
  toAsset: string;
  amount?: string | null;
  recipient?: string | null;
  status: "ready" | "pending" | "signed" | "confirmed";
  signingHint?: string | null;
};

export type SmartPayExecution = {
  id: string;
  paymentIntentId: string;
  quoteId: string;
  status: "awaiting_local_signature" | "pending_reconciliation" | "completed" | "failed";
  createdAt: string;
  updatedAt: string;
  recoverable: boolean;
  nextAction?: string | null;
  progress?: SmartPayExecutionProgress | null;
  routePlan?: SmartPayRouteExecutionStep[];
  txRefs: SmartPayTxRef[];
  error?: string | null;
};

export type SmartPayExecutionResponse = {
  execution: SmartPayExecution;
  sessionToken?: string | null;
};

export type SmartPayReceipt = {
  id: string;
  paymentExecutionId: string;
  paymentIntentId: string;
  completedAt: string | null;
  sourceAssetSpent: string;
  sourceAmountSpent: string;
  targetAssetPaid: string;
  targetAmountPaid: string;
  serviceFeeAcp: string;
  networkFees: SmartPayNetworkFeeItem[];
  recipientAddress: string;
  merchantLabel?: string | null;
  routeSummary: string[];
  txRefs: SmartPayTxRef[];
};

export type SmartPayHistoryEntry = {
  execution: SmartPayExecution;
  receipt: SmartPayReceipt;
  paymentIntent: SmartPayPaymentIntent;
  quote: SmartPayQuote;
};

export type SmartPayHistoryResponse = {
  payments: SmartPayHistoryEntry[];
};

export type SmartPayClientKnownRef = {
  txid: string;
  network?: string | null;
  role?: string | null;
  explorerUrl?: string | null;
  routeStepIndex?: number | null;
};

export type SmartPayRecoverInput = {
  clientKnownTxs: string[];
  clientKnownRefs?: SmartPayClientKnownRef[];
};

/** ACP-hub mobile exchange office (multi-asset foundation). */
export type ExchangeAssetKind =
  | "native"
  | "crypto"
  | "metal"
  | "goods"
  | "commodity"
  | "real_estate"
  | "space"
  | "ip"
  | "fiat";
export type ExchangeAssetAvailability = "live" | "beta" | "planned";
export type ExchangeQuoteMode =
  | "identity"
  | "fixed"
  | "indicative"
  | "rfq"
  | "bridge_1_1"
  | "market_feed";
export type ExchangeSettlementRail =
  | "ledger"
  | "swap_desk"
  | "otc_metal"
  | "otc_goods"
  | "otc_commodity"
  | "otc_real_estate"
  | "otc_space"
  | "otc_ip"
  | "bridge"
  | "dex_deep_link"
  | "fiat_onramp"
  | "hub_cross";
export type ExchangeDirection = "into_acp" | "from_acp" | "both" | "none";
export type ExchangeTicketStatus =
  | "quoted"
  | "opened"
  | "awaiting_user"
  | "pending_review"
  | "settling"
  | "completed"
  | "cancelled"
  | "rejected"
  | "expired";

export type ExchangeAsset = {
  id: string;
  symbol: string;
  label: string;
  kind: ExchangeAssetKind;
  availability: ExchangeAssetAvailability;
  direction: ExchangeDirection;
  rail: ExchangeSettlementRail;
  quote_mode: ExchangeQuoteMode;
  unit: string;
  decimals: number;
  network?: string | null;
  note?: string | null;
  metadata?: Record<string, unknown>;
};

export type ExchangePair = {
  from_asset: string;
  to_asset: string;
  available: boolean;
  rail: ExchangeSettlementRail;
  legs: number;
  availability: ExchangeAssetAvailability;
  note?: string | null;
};

export type ExchangeCatalog = {
  hub_asset: string;
  model: string;
  assets: ExchangeAsset[];
  pairs: ExchangePair[];
  quote_ttl_seconds: number;
  handoff_note: string;
  compliance_note: string;
};

export type ExchangeQuoteLeg = {
  from_asset: string;
  to_asset: string;
  from_amount: string;
  to_amount: string;
  rate: string;
  rail: ExchangeSettlementRail;
  quote_mode: ExchangeQuoteMode;
  note?: string | null;
};

export type ExchangeQuoteInput = {
  from_asset: string;
  to_asset: string;
  from_amount: string;
  purity_ppt?: number | null;
  goods_estimate_acp?: string | null;
};

export type ExchangeQuote = {
  quote_id: string;
  from_asset: string;
  to_asset: string;
  from_amount: string;
  to_amount: string;
  acp_hub_amount: string;
  rate_from_to: string;
  legs: ExchangeQuoteLeg[];
  rail: ExchangeSettlementRail;
  expires_at: string;
  indicative: boolean;
  rate_note: string;
  next_step: string;
};

export type ExchangeTicketCreateInput = {
  quote_id: string;
  payout_acp_address?: string | null;
  counterparty_address?: string | null;
  note?: string | null;
  goods_title?: string | null;
  goods_description?: string | null;
};

export type ExchangeTicketAuthSettleInput = {
  tron_txid?: string | null;
};

export type ExchangeTicket = {
  id: string;
  user_id?: string | null;
  status: ExchangeTicketStatus;
  from_asset: string;
  to_asset: string;
  from_amount: string;
  to_amount_estimated: string;
  acp_hub_amount: string;
  rail: ExchangeSettlementRail;
  rail_ref_type?: string | null;
  rail_ref_id?: string | null;
  quote_id: string;
  quote_snapshot?: Record<string, unknown>;
  payout_acp_address?: string | null;
  counterparty_address?: string | null;
  intake_reference?: string | null;
  handoff_instructions?: string | null;
  next_step: string;
  note?: string | null;
  expires_at?: string | null;
  created_at: string;
  updated_at: string;
};

/** Soulbound digital passport (org identity + BSC attestation). */
export type DigitalPassportRecord = {
  id: string;
  user_id: string;
  org_id?: string | null;
  wallet_address: string;
  token_id: number;
  claim_hash: string;
  chain_id: string;
  contract_address?: string | null;
  tx_hash?: string | null;
  token_uri?: string | null;
  status: string;
  nfc_credential_id?: string | null;
  issued_at?: string | null;
  revoked_at?: string | null;
  created_at: string;
  explorer_url?: string | null;
};

export type DigitalPassportListResponse = {
  items: DigitalPassportRecord[];
};

export type DigitalPassportIssueInput = {
  wallet_address: string;
  nfc_credential_id?: string | null;
};

export type NfcCredentialRegisterInput = {
  uid_hash: string;
  label?: string | null;
};

export type NfcCredentialRecord = {
  id: string;
  label?: string | null;
  uid_hash: string;
  vendor: string;
  created_at: string;
  revoked_at?: string | null;
  is_active: boolean;
};

/** Banknote/coin authenticity + numismatic valuation (iPhone prototype). */
export type NumismaticInstrumentKind = "banknote" | "coin";
export type NumismaticAuthVerdict =
  | "likely_genuine"
  | "needs_review"
  | "suspect"
  | "insufficient_data";
export type NumismaticGrade = "G" | "VG" | "F" | "VF" | "XF" | "AU" | "UNC" | "PR";
export type NumismaticRarity = "common" | "scarce" | "rare" | "very_rare" | "unique_est";

export type NumismaticFeatureDef = {
  id: string;
  label: string;
  applies_to: NumismaticInstrumentKind[];
  weight: number;
};

export type NumismaticCatalogCurrency = {
  code: string;
  label: string;
  note_series: string[];
  coin_series: string[];
};

export type NumismaticCatalog = {
  currencies: NumismaticCatalogCurrency[];
  features: NumismaticFeatureDef[];
  grades: Array<{ code: string; label: string }>;
  rarity_tiers: Array<{ code: string; label: string }>;
  disclaimer: string;
};

export type NumismaticAuthInput = {
  kind: NumismaticInstrumentKind;
  currency_code: string;
  series_or_denomination: string;
  year?: number | null;
  serial_or_mint_mark?: string | null;
  features_present?: string[];
  features_missing?: string[];
  features_unchecked?: string[];
  measured_weight_g?: string | null;
  measured_diameter_mm?: string | null;
  magnetic?: boolean | null;
  notes?: string | null;
};

export type NumismaticAuthResult = {
  kind: NumismaticInstrumentKind;
  currency_code: string;
  series_or_denomination: string;
  authenticity_score: number;
  verdict: NumismaticAuthVerdict;
  checks: Array<{ id: string; label: string; status: string; weight: number }>;
  flags: string[];
  next_step: string;
  disclaimer: string;
};

export type NumismaticValueInput = {
  kind: NumismaticInstrumentKind;
  currency_code: string;
  series_or_denomination: string;
  year?: number | null;
  grade?: NumismaticGrade;
  rarity?: NumismaticRarity;
  face_value_hint?: string | null;
  authenticity_score?: number | null;
  quantity?: number;
};

export type NumismaticValueResult = {
  kind: NumismaticInstrumentKind;
  currency_code: string;
  series_or_denomination: string;
  grade: NumismaticGrade;
  rarity: NumismaticRarity;
  indicative_acp_amount: string;
  face_reference_acp?: string | null;
  premium_factor: string;
  rate_note: string;
  authenticity_note: string;
  next_step: string;
  disclaimer: string;
};

export type DatingCatalog = {
  title: string;
  device_name_prefix: string;
  ble_service_uuid: string;
  max_hop: number;
  age_gate: string;
  docs_url: string;
  legal_url: string;
  notes: string[];
};

export type DatingAccessPoint = {
  id: string;
  title: string;
  description: string | null;
  lat: number;
  lon: number;
  ble_service_hint: string;
  status: string;
  created_at: string;
};

export type DatingAccessPointCreateInput = {
  title: string;
  description?: string | null;
  lat: number;
  lon: number;
};

export type DatingProfile = {
  id: string;
  user_id: string;
  display_name: string;
  bio: string | null;
  age_attested_18: boolean;
  visibility: string;
  lat: number | null;
  lon: number | null;
  mesh_peer_id: string | null;
  updated_at: string;
};

export type DatingProfileUpsertInput = {
  display_name: string;
  bio?: string | null;
  age_attested_18: boolean;
  visibility?: string;
  lat?: number | null;
  lon?: number | null;
  mesh_peer_id?: string | null;
};
