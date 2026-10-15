# ACP wallet usability release evidence

Published build: `f4588a7`.

- [Merged PR #90](https://github.com/ancapcloud/ancap/pull/90)
- [Successful deployment](https://github.com/ancapcloud/ancap/actions/runs/38683245215)
- [Backend CI](https://github.com/ancapcloud/ancap/actions/runs/38682514625): 907 passed, 34 skipped; public-trust regression 60 passed, 5 skipped.
- [Frontend/mobile/browser CI](https://github.com/ancapcloud/ancap/actions/runs/38682514442): 54 frontend tests and 38 browser scenarios passed, one browser scenario skipped; mobile SDK checks passed.
- [CodeQL](https://github.com/ancapcloud/ancap/actions/runs/38682514351) passed.
- [Live wallet](https://ancap.cloud/wallet/acp)

The release clarifies available ACP, chain balances and platform credits; separates
receive/send/history/security; adds exact fee-aware preparation and transfer review;
preserves queued job IDs for read-only status checks; and loads extra services only
on request. Unknown or degraded native balances block sends. Scope and limitations
are described in [the release note](../../../WALLET_UX_RELEASE_2026-10-15.md).

`results.json` records the verified build, API readiness, denied unauthenticated
balance access, robots metadata, five-language guest headings and mobile width.
Live browser checks found no horizontal overflow or captured JavaScript errors.

Ten wallet browser scenarios use synthetic credentials, addresses and balances.
Their assertions cover reviewed transfers, exact fees, degraded balances, operator
totals, retained backup display, expired sessions, mobile views and uncertain jobs.
These tests do not prove live chain settlement or customer balances. No production
account login, transfer, broadcast, password change or wallet creation was performed.
Original mobile/consensus/bridge/SACP WIP was excluded. This documentation follow-up
does not change the deployed application SHA.
