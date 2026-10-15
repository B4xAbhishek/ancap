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

Full CI and production deployment are recorded after verification. Production checks
are read-only. Screenshots of the signed-in layout use a clearly identified test user.
