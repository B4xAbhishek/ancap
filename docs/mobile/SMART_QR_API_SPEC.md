# ANCAP Mobile — Smart QR API Specification

> Status: proposed API spec | Updated: 2026-05-25
> Related: `SMART_QR_PAYMENT_INTENT_SCHEMA.md`, `SMART_QR_SECURITY.md`, `SMART_QR_AUTO_SWAP_PLAN.md`
> Base URL: production `https://api.ancap.cloud`

---

## 1. API goals

The Smart QR API should support five jobs:

1. parse and normalize scanned QR payloads
2. classify ambiguous payloads when deterministic parsing fails
3. quote direct-pay or auto-swap payment routes
4. track execution sessions and recovery
5. expose supported assets/networks/limits for mobile UX

Rule: server may help parse, quote, and orchestrate — but it must not hold mobile seed phrases or sign on behalf of the user in the non-custodial path.

---

## 2. Auth model

### Public or low-friction endpoints
Can be unauthenticated with rate limits:
- parse
- classify (if enabled)
- capabilities
- supported assets/networks

### Auth-required endpoints
Should require ANCAP auth or signed device session:
- execute payment session
- recover session
- fetch private payment session history
- fetch per-execution status / receipt unless the caller presents either the per-execution `sessionToken` or the authenticated execution-owner session

---

## 3. Capability discovery

### `GET /v1/mobile/smart-pay/capabilities`

Purpose:
- feature flags
- supported networks/assets
- limits
- AI fallback availability

Example response:

```json
{
  "enabled": true,
  "smartQrParseEnabled": true,
  "smartQrAiFallbackEnabled": false,
  "autoSwapEnabled": false,
  "supportedNetworks": ["acp", "bsc"],
  "supportedAssets": [
    { "network": "acp", "symbol": "ACP" },
    { "network": "bsc", "symbol": "wACP", "tokenAddress": "0x..." },
    { "network": "bsc", "symbol": "USDT", "tokenAddress": "0x..." }
  ],
  "maxImageBytes": 5242880,
  "maxSlippageBps": 500,
  "minAcpFeeReserve": "1.0"
}
```

---

## 4. Parse endpoint

### `POST /v1/mobile/smart-pay/parse`

Purpose:
- turn decoded QR text into canonical `PaymentIntent`
- use deterministic + heuristic parsers first

Request:

```json
{
  "source": "camera",
  "rawPayload": "ethereum:0xabc...@56/transfer?address=0xdef...&uint256=25000000",
  "hint": {
    "locale": "en",
    "platform": "ios"
  }
}
```

Response:

```json
{
  "paymentIntent": {
    "id": "pi_123",
    "parseMethod": "deterministic",
    "confidence": 1,
    "network": "bsc",
    "asset": {
      "kind": "erc20",
      "symbol": "USDT",
      "tokenAddress": "0x...",
      "decimals": 18,
      "isSupported": true,
      "isAllowlisted": true
    },
    "recipient": {
      "address": "0xdef...",
      "addressType": "evm",
      "checksumValid": true
    },
    "amount": {
      "value": "25",
      "atomicValue": "25000000",
      "currencySymbol": "USDT",
      "isExact": true,
      "isMax": false
    },
    "memo": null,
    "merchant": null,
    "riskFlags": [],
    "warnings": [],
    "unsupportedReasons": [],
    "requiresUserConfirmation": true,
    "status": "parsed",
    "metadata": {
      "detectedStandard": "eip681",
      "invoiceType": "token_transfer",
      "aiModel": null,
      "aiUsed": false,
      "parserVersion": "1"
    }
  }
}
```

Error cases:
- 400 malformed payload
- 422 unsupported but parseable payload
- 429 rate limit

---

## 5. AI fallback classification endpoint

### `POST /v1/mobile/smart-pay/classify`

Purpose:
- use AI only when `parse` fails or returns ambiguous result
- classify raw payload or screenshot-derived text into the canonical schema

Request:

```json
{
  "rawPayload": "PAY TO USDT BSC 25.50 -> 0xdef...",
  "context": {
    "source": "photo",
    "allowImageUpload": false,
    "locale": "en"
  }
}
```

Response:

```json
{
  "paymentIntent": {
    "id": "pi_456",
    "parseMethod": "ai",
    "confidence": 0.91,
    "status": "needs_review",
    "network": "bsc",
    "asset": {
      "kind": "erc20",
      "symbol": "USDT",
      "tokenAddress": "0x...",
      "decimals": 18,
      "isSupported": true,
      "isAllowlisted": true
    },
    "recipient": {
      "address": "0xdef...",
      "addressType": "evm",
      "checksumValid": true
    },
    "amount": {
      "value": "25.50",
      "atomicValue": "25500000",
      "currencySymbol": "USDT",
      "isExact": true,
      "isMax": false
    },
    "memo": null,
    "merchant": {
      "label": "Example Store",
      "category": null,
      "website": null,
      "invoiceId": null
    },
    "riskFlags": ["ai_classified"],
    "warnings": ["AI-assisted classification requires user review"],
    "unsupportedReasons": [],
    "requiresUserConfirmation": true,
    "metadata": {
      "detectedStandard": null,
      "invoiceType": "merchant_freeform",
      "aiModel": "smart-qr-classifier-v1",
      "aiUsed": true,
      "parserVersion": "1"
    }
  }
}
```

Rules:
- AI response must validate against `SMART_QR_PAYMENT_INTENT_SCHEMA.md`
- if confidence too low -> return 422 with structured reason
- do not auto-execute after classification alone

---

## 6. Quote endpoint

### `POST /v1/mobile/smart-pay/quote`

Purpose:
- build direct-pay or auto-swap quote for a validated `PaymentIntent`

Request:

```json
{
  "paymentIntentId": "pi_123",
  "sourcePreference": {
    "preferredAsset": "ACP",
    "allowedAssets": ["ACP", "wACP", "USDT"],
    "maxSlippageBps": 150,
    "minAcpFeeReserve": "1.0"
  }
}
```

Response:

```json
{
  "quote": {
    "quoteId": "q_123",
    "paymentIntentId": "pi_123",
    "mode": "swap_then_send",
    "expiresAt": "2026-05-25T10:55:00Z",
    "sourceAsset": {
      "network": "acp",
      "symbol": "ACP",
      "tokenAddress": null,
      "decimals": 8
    },
    "targetAsset": {
      "network": "bsc",
      "symbol": "USDT",
      "tokenAddress": "0x...",
      "decimals": 18
    },
    "targetAmount": "25.50",
    "requiredSourceAmount": "103.42",
    "serviceFeeAcp": "0.75",
    "networkFee": [
      { "network": "acp", "assetSymbol": "ACP", "amount": "0.00000100" },
      { "network": "bsc", "assetSymbol": "BNB", "amount": "0.00021" }
    ],
    "slippageBps": 150,
    "route": [
      {
        "kind": "swap",
        "network": "bsc",
        "dexOrRail": "ancap_router_v1",
        "fromAsset": "wACP",
        "toAsset": "USDT",
        "estimatedOut": "25.50"
      },
      {
        "kind": "transfer",
        "network": "bsc",
        "dexOrRail": null,
        "fromAsset": "USDT",
        "toAsset": "USDT",
        "estimatedOut": "25.50"
      }
    ],
    "warnings": [],
    "riskFlags": []
  }
}
```

Error cases:
- 409 insufficient ACP fee reserve
- 422 unsupported route
- 503 quote source unavailable

---

## 7. Execute endpoint

### `POST /v1/mobile/smart-pay/execute`

Purpose:
- create a tracked execution session from a confirmed quote
- server orchestrates session state, but mobile still performs required local signatures in the non-custodial path

Request:

```json
{
  "paymentIntentId": "pi_123",
  "quoteId": "q_123",
  "confirmationAccepted": true,
  "deviceContext": {
    "platform": "android",
    "appVersion": "1.1.0"
  }
}
```

Response:

```json
{
  "execution": {
    "id": "pe_123",
    "paymentIntentId": "pi_123",
    "quoteId": "q_123",
    "status": "awaiting_local_signature",
    "createdAt": "2026-05-25T10:50:00Z",
    "updatedAt": "2026-05-25T10:50:00Z",
    "recoverable": true,
    "nextAction": "sign_swap_tx",
    "progress": {
      "totalRouteSteps": 3,
      "observedTxCount": 0,
      "remainingRouteSteps": 3,
      "pendingRoles": ["bridge", "swap", "merchant_payout"]
    },
    "txRefs": [],
    "error": null
  }
}
```

Notes:
- in pure non-custodial mode, mobile may need one or more local sign steps
- `execute` creates orchestration state, not blind backend fund movement
- execution payloads now include `progress` metadata so clients can show total route steps, observed tx count, remaining steps, and pending route roles without guessing from raw tx lists alone

---

## 8. Execution status endpoint

### `GET /v1/mobile/smart-pay/payments`

Purpose:
- fetch authenticated payment history for receipt/history screens
- resume recent Smart Pay sessions across devices or app reinstalls

Auth:
- requires authenticated ANCAP user/device session

Query params:
- `limit` (default `20`, max `100`)

Response:

```json
{
  "payments": [
    {
      "execution": {
        "id": "pe_123",
        "status": "pending_reconciliation",
        "recoverable": true,
        "nextAction": null,
        "progress": {
          "totalRouteSteps": 3,
          "observedTxCount": 3,
          "remainingRouteSteps": 0,
          "pendingRoles": []
        },
        "txRefs": [
          {
            "role": "bridge",
            "network": "acp",
            "txid": "0xbridge...",
            "explorerUrl": "https://ancap.cloud/acp/tx/0xbridge..."
          }
        ],
        "error": null
      },
      "receipt": {
        "id": "spr_pe_123",
        "paymentExecutionId": "pe_123",
        "paymentIntentId": "pi_123",
        "completedAt": null,
        "sourceAssetSpent": "ACP",
        "sourceAmountSpent": "103.42",
        "targetAssetPaid": "USDT",
        "targetAmountPaid": "25.50",
        "serviceFeeAcp": "0.75",
        "networkFees": [],
        "recipientAddress": "0xdef...",
        "merchantLabel": null,
        "routeSummary": ["1. bridge ACP -> wACP on acp via ancap_bridge_v1"],
        "txRefs": []
      },
      "paymentIntent": {
        "id": "pi_123"
      },
      "quote": {
        "quoteId": "q_123"
      }
    }
  ]
}
```

Notes:
- first repo slice returns the authenticated caller's recent executions only
- each history entry includes `execution` + `receipt` + original `paymentIntent` + `quote` so clients can rebuild receipt/history UIs without extra round trips
- anonymous/session-token resume still depends on the device-local per-execution `sessionToken`
- however, when the current device is signed into the same ANCAP account, clients may use authenticated payment-history entries to reopen the receipt/progress view and call status / receipt / recover endpoints through account ownership access even without the original session token

---

## 8. Execution status endpoint

### `GET /v1/mobile/smart-pay/payments/{executionId}`

Purpose:
- resume progress screen
- recover after app restart

Access:
- anonymous/device-local resume may pass `?sessionToken=...`
- authenticated execution owners may reopen the same execution without the original device-local token

Response:

```json
{
  "execution": {
    "id": "pe_123",
    "status": "pending_reconciliation",
    "recoverable": true,
    "nextAction": null,
    "progress": {
      "totalRouteSteps": 3,
      "observedTxCount": 2,
      "remainingRouteSteps": 1,
      "pendingRoles": ["merchant_payout"]
    },
    "txRefs": [
      {
        "role": "bridge",
        "network": "acp",
        "txid": "0xbridge...",
        "explorerUrl": "https://ancap.cloud/acp/tx/0xbridge..."
      },
      {
        "role": "swap",
        "network": "bsc",
        "txid": "0xswap...",
        "explorerUrl": "https://bscscan.com/tx/0xswap..."
      }
    ],
    "error": null
  }
}
```

---

### Settlement safety (fail closed)

- Smart Pay `execute` currently prepares a non-custodial route plan; it does not broadcast a signed payment.
- Client-submitted `clientKnownTxs` / `clientKnownRefs` and explorer URLs are **unverified observations**, even when all quoted route steps have a tx reference.
- The `recover` endpoint therefore keeps the execution at `pending_reconciliation` (`recoverable: true`) instead of marking it `completed`. A zero `remainingRouteSteps` value means all route references are present, **not** that funds settled.
- Receipts are preliminary snapshots with `completedAt: null` unless a trusted chain-confirmation path has established final settlement. The backend also masks previously stored unverified `completed` statuses and completion timestamps when reading them.
- The trusted ACP/BSC transaction confirmation, route matching, finality and recipient/amount verification workflow is **not implemented by this change**. Until it exists, no recovery-supplied tx reference may finalize a payment.

---

## 9. Recover endpoint

### `POST /v1/mobile/smart-pay/payments/{executionId}/recover`

Purpose:
- continue or reconcile a payment session stuck after crash/network loss

Access:
- anonymous/device-local resume may pass `?sessionToken=...`
- authenticated execution owners may recover the same execution without the original device-local token

Request:

```json
{
  "clientKnownTxs": ["0xswap...", "0xpay..."],
  "clientKnownRefs": [
    {
      "txid": "0xbridge...",
      "network": "acp",
      "role": "bridge",
      "explorerUrl": "https://ancap.cloud/acp/tx/0xbridge...",
      "routeStepIndex": 1
    },
    {
      "txid": "0xpay...",
      "network": "bsc",
      "role": "merchant_payout",
      "explorerUrl": "https://bscscan.com/tx/0xpay...",
      "routeStepIndex": 3
    }
  ]
}
```

Response:

```json
{
  "execution": {
    "id": "pe_123",
    "status": "pending_reconciliation",
    "recoverable": true,
    "nextAction": null,
    "progress": {
      "totalRouteSteps": 3,
      "observedTxCount": 3,
      "remainingRouteSteps": 0,
      "pendingRoles": []
    },
    "txRefs": [
      {
        "role": "bridge",
        "network": "acp",
        "txid": "0xbridge...",
        "explorerUrl": "https://ancap.cloud/acp/tx/0xbridge...",
        "routeStepIndex": 1
      },
      {
        "role": "swap",
        "network": "bsc",
        "txid": "0xswap...",
        "explorerUrl": "https://bscscan.com/tx/0xswap...",
        "routeStepIndex": 2
      },
      {
        "role": "merchant_payout",
        "network": "bsc",
        "txid": "0xpay...",
        "explorerUrl": "https://bscscan.com/tx/0xpay...",
        "routeStepIndex": 3
      }
    ],
    "error": null
  }
}
```

Notes:
- `clientKnownTxs` remains the compatibility fallback for raw tx hashes
- `clientKnownRefs` lets clients preserve `network`, `role`, `explorerUrl`, and optional quoted-route `routeStepIndex` linkage from pasted explorer links or richer local observations
- when both forms describe the same tx, backend reconciliation should prefer the richer structured ref instead of collapsing back to a bare hash
- explicit `routeStepIndex` linkage should only attach when the role/network matches the quoted route step; conflicting refs should stay visible as additional proof rather than being silently remapped

---

## 10. Receipt endpoint

### `GET /v1/mobile/smart-pay/payments/{executionId}/receipt`

Purpose:
- return final receipt for history and receipt screen
- used together with payment-history listing for direct receipt refresh on the active session

Response:
- `SmartPayReceipt` from schema spec

---

## 11. Asset and route discovery

### `GET /v1/mobile/smart-pay/assets`
Returns assets supported for:
- scan parsing
- direct send
- auto-swap source selection

### `GET /v1/mobile/smart-pay/networks`
Returns supported networks + current health/flags.

---

## 12. Server-side implementation notes

Suggested backend modules:
- `smart_qr.py` — deterministic parsers + normalization
- `smart_qr_ai.py` — fallback classifier wrapper
- `smart_pay_quotes.py` — route/fee/slippage quote engine
- `smart_pay_sessions.py` — execution session state + recovery

Suggested persistence:
- `smart_qr_intents`
- `smart_pay_quotes`
- `smart_pay_executions`
- `smart_pay_receipts`

---

## 13. Rate limits and abuse controls

Recommended baseline:
- parse: 60/min per IP/device
- classify: 20/min per IP/device
- quote: 20/min per auth user/device
- execute: 10/min per auth user/device
- recover: 20/min per auth user/device

Add:
- payload size limit
- image size limit
- quote TTL
- request dedupe / idempotency for execute

---

## 14. Release-scope recommendation

For first release:
- expose only `capabilities`, `parse`, `quote`, `execute`, authenticated `payments` history, `status`, `recover`, and `receipt`
- keep AI classify endpoint behind feature flag
- keep supported networks limited to `acp` and `bsc`

---

## 15. Bottom line

The Smart QR API should not be a vague “AI service”.
It should be a strict payment-intelligence API:
- parse safely
- quote transparently
- execute trackably
- recover reliably
