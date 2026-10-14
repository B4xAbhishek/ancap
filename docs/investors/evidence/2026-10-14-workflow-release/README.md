# Workflow discovery release verification

Verified production build: `426bc5cb39912a0c10a1c1f58a7f1f98ace38b53` (`426bc5c`), 14 October 2026.

- [Merged PR](https://github.com/ancapcloud/ancap/pull/80)
- [Successful deployment](https://github.com/ancapcloud/ancap/actions/runs/38616142302)
- [Backend CI](https://github.com/ancapcloud/ancap/actions/runs/38614844094): 883 passed, 34 skipped; Docker build passed.
- [Frontend/mobile CI](https://github.com/ancapcloud/ancap/actions/runs/38614843599): frontend 46 unit tests, mobile 281 tests, browser 25 passed / 1 skipped.
- [Rust/contract CI](https://github.com/ancapcloud/ancap/actions/runs/38614843609): crypto, node, FFI, wallet check, dependency audit and bridge contracts passed.

`LIVE_VERIFICATION.json` records HTTP readiness/build checks and live browser behavior: task matching, shortlist after reload, JSON comparison export, investor evidence and mobile width. Catalog source was live; no page runtime errors occurred. Only read-only HTTP and local browser state were exercised; no payment, broadcast or production account creation.

API/frontend/proxy were refreshed, including the API's committed walletd build. The standalone ACP node binary and mobile applications were not rebuilt/released. Original uncommitted wallet/bridge/consensus/SACP work remains excluded. GitHub reported zero open critical Dependabot alerts after the merge; this is not a full security certification. Residual npm advisories and Rust maintenance warnings remain in the release notes. Bandit baseline reports 66 low, 4 medium and 1 high; the high finding is MD5 for growth-dimension grouping, not credential signing. The pre-existing Bandit CI command pipes into tee and does not enforce scanner exit status; CodeQL and dependency audit are separate checks.

Local full Windows backend verification was stopped after the complete Linux suite passed; its partial run is not counted as a full pass. macOS/iOS and physical-device wallet acceptance remain open.
