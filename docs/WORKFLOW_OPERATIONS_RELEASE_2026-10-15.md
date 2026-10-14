# Workflow operations release — 15 October 2026

This extends the workflow discovery release with executable operations at
`/ai/studio`, translated into EN/RU/UK/DE/zh-Hant. No customer revenue, investment
commitments, live customer connectors or provisioned private hosting are claimed.

Implemented scope:

- Recurring schedules with published versions, current/previous CoinGecko snapshots,
  minimum hourly interval and owner-selected ACP monthly spending limits.
- Authorized webhook, Telegram, Google Sheets and HubSpot note delivery; encrypted
  credentials, human review and durable delivery claims with explicit uncertain retry.
- One bounded, nontransferable AI trial per account, 20 daily globally and three per
  IP daily. No ACP minting/top-up; unavailable-model fallback is labelled.
- Project text/document context and registered-account viewer/editor/reviewer access.
- Quality passports: provider/model/fallback, hashes, market-source timestamps,
  structure and declared required-text checks. These are not fact verification.
- Review queue with edits, reviewer identity, approval/rejection and cancellation of
  unfinished work. A rejected result is not delivered; completed steps stay charged.
- Immutable definition snapshots, paid draft tests, publication and version rollback.
- Operator-only captured-credit and repeat-account metrics; supplier invoice cost,
  cash margin and EUR revenue are unavailable until actual invoices are reconciled.
- Downloadable Python API example and inactive n8n HTTP template. Tokens and explicit
  spending limits are supplied by the caller; examples never auto-approve delivery.
- Bounded CSV batch parsing and per-row/per-step execution receipts.
- Sequential visual builder: 1–5 existing approved workflow steps; version export/import.
- Request-local encrypted Anthropic BYOK; provider billing remains separate from ACP.
- Customer-operated private deployment profile and setup documentation. Infrastructure
  provision, managed hosting, unrestricted graphs and OAuth refresh are outside this release.

Financial execution reuses the existing credits reservation/capture/refund path and
ledger halt. Actual ACP quote checks occur at enqueue and before every model step;
no assumed ACP/EUR exchange rate. Request idempotency and PostgreSQL transaction
locks protect restart recovery and concurrent accounting.

Validation: 907 backend tests, 50 frontend tests, 281 mobile SDK tests and 27 browser scenarios passed in full CI. Migration upgrade/downgrade/upgrade passed on a disposable database. Deployed build `e53f949` passed readiness, queue heartbeat, five-language and mobile checks. [Immutable release evidence](investors/evidence/2026-10-15-workflow-operations/README.md) records scope and remaining dependency findings. Connector/provider tests use
synthetic credentials and mocks; paid API tests use disposable databases and test
credits. Production verification is read-only. Wallet/consensus/bridge/SACP WIP in
the original checkout is excluded.
