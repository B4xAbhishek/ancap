# ACP wallet usability release — 15 October 2026

Scope: `/wallet/acp`, client-side presentation and transfer preparation. Chain,
ledger, signing, password verification and broadcast APIs retain their existing
contracts. Native mobile/consensus/bridge/SACP WIP is excluded.

## User journey

- The first screen shows explicitly available-to-send ACP, with on-chain ACP,
  platform workflow credits and committed funds in separate cards. These amounts
  are never added into a new invented total. Operator/network aggregates stay in
  labelled technical details, with an operator explanation.
- Receive, Send, Activity, Security and More services have separate views. The
  receiving address is shown in full, with ACP-network guidance and copy feedback.
- Sending has an explicit review step with recipient, amount, fee and total. Native
  limits and Max use integer atoms rather than floating point; unknown availability
  blocks preparation. A second submit is prevented while the request is active.
- A queued job ID survives polling failure and can be checked without creating
  another send. Pending/uncertain status is not presented as a successful transfer;
  network acceptance is distinguished from confirmations.
- History is loaded on demand for one explicitly selected address. Provider errors
  remain errors, rather than zero balances or empty-history claims. Read-auth failure
  clears the session. Account changes invalidate outstanding reads and sensitive UI.
- Password recovery keeps `/wallet/acp#password-security`. Credentials are cleared
  from forms after attempts or section/account changes and are not persisted locally.
- The returned creation mnemonic remains visible until explicitly hidden. Copy
  explicitly explains that it is not a full Dilithium backup: original keystore is
  required, and the existing web API does not export that keystore.
- OTC, assay, ownership and bulk tools are loaded only when requested. Legacy disabled
  web-USDT swap calls are removed from the default load. Bulk sends validate every row
  and cumulative fees before any send, preserve completed results and stop on failure
  or uncertainty. Unmounting stops remaining rows; no automatic batch retry exists.
- Guest users get a useful sign-in screen. Five-language labels and responsive layout
  are retained; financial account pages remain noindex/nofollow.

## Verification

Targeted tests exercise exact fees, overprecision, unavailable balances, cumulative
bulk limits and five-language completeness. Browser fixtures exercise normal/operator
balances, explicit transfer review, queued-job failures, backup display, expired
sessions, history failures and mobile widths. All credentials, addresses and balances
in those fixtures are synthetic. No real transfer or password rotation is performed.

Full CI passed: 907 backend tests (34 skipped), 60 public-trust regression tests
(5 skipped), 54 frontend tests and 38 browser scenarios (1 skipped), including
10 wallet fixture scenarios. Frontend production build, mobile SDK checks, secret
hygiene and CodeQL passed. Production checks are read-only. Screenshots of the
signed-in layout use a clearly identified test user.

## Deployment

[PR #90](https://github.com/ancapcloud/ancap/pull/90) merged as
`f4588a7b473131a26de1fda987376aaf36cc1611`.
[Production deployment](https://github.com/ancapcloud/ancap/actions/runs/38683245215)
succeeded; `/internal/frontend-build` reports `f4588a7`. On 15 October 2026,
readiness confirmed database/Redis, `/wallet/acp` returned HTTP 200 with
`noindex, nofollow`, and an unauthenticated balance request returned HTTP 401.
The live guest page stayed on the wallet route, rendered all five languages and
fit a 390-pixel viewport without horizontal overflow or captured JavaScript errors.

[Release evidence](investors/evidence/2026-10-15-wallet-ux/README.md) records CI and
read-only production results. No production account login, real transfer, broadcast,
password change or wallet creation was performed. Existing backend/native wallet
limitations remain; the web API still has no complete Dilithium keystore export.
The documentation-only follow-up does not change the deployed application SHA.
