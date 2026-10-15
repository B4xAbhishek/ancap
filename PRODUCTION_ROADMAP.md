# ANCAP Production Roadmap

## ACP wallet usability — 2026-10-15

Web wallet hierarchy, balance clarity, reviewed transfers and on-demand services are implemented. Full CI passed; build `f4588a7` is deployed and verified, including five-language/mobile guest checks. [Scope and verification](docs/WALLET_UX_RELEASE_2026-10-15.md). Existing native/consensus/bridge/SACP work is not included.

## Workflow Studio release — 2026-10-15

Implementation and limits: [workflow operations](docs/WORKFLOW_OPERATIONS_RELEASE_2026-10-15.md). Durable schedules, review, delivery, context, versions, bounded trials/batches, API examples and BYOK are implemented. Full CI passed; build `e53f949` is deployed and verified. Release evidence records test counts and remaining dependency findings. External account credentials and private infrastructure are customer supplied; wallet/bridge/consensus/SACP WIP is excluded.

> Status: supporting snapshot | Updated: 2026-05-25
> Last verified: 2026-05-28
> Source of truth: `MASTER_ROADMAP.md`
> Purpose: product/deploy status snapshot. This file is useful for historical and operational context, but execution priority and final truth now live in `MASTER_ROADMAP.md`.
> Fast status index: `docs/STATUS_MATRIX.md`

## Summary

ANCAP moves from a broad AI-native capital allocation platform into a production product where users, crypto teams, creators, and AI agents buy, create, and sell paid AI-workflows for ACP. The product priority is still real LLM execution, ACP-first monetization, proof receipts, realtime statuses, creator publishing, developer/API monetization, and B2B operational controls.

Fixed decisions:

- Primary LLM: Teneta/Claude-compatible Anthropic API.
- Payments: ACP-first. Stripe/fiat stays a later adapter after ACP checkout is stable.
- Roadmap style: production roadmap, not a "build everything" backlog.
- Fallback policy: template output is allowed only as explicitly degraded fallback, never as a hidden premium LLM result.
- AI governance: AI/ISO readiness guidance is tracked in `docs/AI_ISO_GOVERNANCE_NOTES.md`.
- Public trust layer: whitepapers, terms, privacy, and cookie consent are published on the site before broader paid acquisition.

## Snapshot Status

Reality note: this section is a capability snapshot, not a claim that the whole project is release-complete. The main remaining tails are security / CI / prod-hardening, finishing the mobile wallet to a real device-ready release, and monetization depth beyond the first ACP-first loop.

### ACP 210M hard-cap recovery (2026-10-02)
- Pre-recovery chain supply was **832,187,477.05255227 ACP** (three accepted double-spends + synthetic validator outputs). Wallet headlines above 210M mixed that inflation with a stale Redis UTXO index.
- Node now resolves referenced UTXOs, rejects double-spends, and refuses empty-input minting. Miner packs fees only.
- API fail-closes withdrawals unless `gettxoutsetinfo` reports issued = 210M. Bridge proof uses live BSC `totalSupply()` + 999 ACP fee buffer.
- Recovery procedure: `scripts/regenesis-v3-hard-cap.sh`. Incident: `docs/ACP_SUPPLY_INCIDENT_2026-10-02.md`.

### ACP web wallet launch recovery (2026-09-29)
- Balance API/UI partitioned into on-chain / platform ledger / staked / withdrawable / operator live (never design-as-live).
- Address binding history + mobile indexer watchlist + DB-backed tx history + admin rescan.
- ACP RPC admin surface fail-closed without token; prod requires `ACP_RPC_TOKEN`; `/rpc` rate-limited.
- Public `acp1.ancap.cloud` host routing: Hestia IP-bound vhosts rewrite exact `/rpc` (was dead `:18080`) → compose `:8080` via `scripts/ensure-acp1-host-proxy.sh` on every deploy; docker nginx serves `/rpc` + `/healthz` with `X-Ancap-Upstream: acp-rpc`.
- Deposit address `acp1qpj54…` live probe: 0 UTXO / empty txs — no hot→user coin mint without proven reconcile gap.

| Phase | Component | Status |
| --- | --- | --- |
| P0 | Auth rate limiting | DONE |
| P0 | Paid API idempotency/export/totals | DONE |
| P0 | Revenue margin/referral totals | DONE |
| P0 | Admin billing UI | DONE: resilient partial-failure loading + refresh + empty states verified |
| P1 | LLM abstraction and `llm_usage_events` | DONE |
| P1 | Real LLM in paid workflow execution | DONE |
| P2 | Redis-backed rate limits/cache/pubsub | DONE |
| P2 | `/system/health/full` and `/metrics` | DONE |
| P2 | Structured JSON logging | DONE |
| P3 | Workflow run SSE live status | DONE |
| P3 | Notification fanout and SMTP email service | DONE |
| P4 | ACP checkout, creator listing flow, revenue dashboard | DONE |
| P4 | Paid API spend caps, idempotency, CSV export | DONE |
| P5 | PostgreSQL FTS search and analytics dashboard | DONE |
| P5 | Product docs/help center | DONE |
| P5 | AI/ISO governance notes and premium readiness SKU | DONE |
| P5 | Project/ACP whitepapers, legal pages, cookie consent | DONE |
| P6 | Strategy Builder MVP | DONE for current lightweight builder: Suspense-safe, backend-derived strategy metadata, validation hardened; React Flow remains later |
| P6 | Social profiles/follows | PARTIAL: backend and profile pages exist; feed polish remains |
| P6 | Theme toggle and PWA shell | DONE |
| P7 | Audit log viewer | DONE |
| P7 | Organizations/teams | DONE for current stabilization slice: frontend wrappers + detail/member-role flows + tests/build green |
| P7 | Webhooks | DONE for current stabilization slice: frontend wrappers + create/test/rotate/delete + delivery view + tests/build green |
| Deploy | GitHub and production sync | DONE: `origin/master` matches local HEAD, working tree is clean, gitignore updated, push verified |
| Launch | Bridge 1:10 math + fiction trim | DONE 2026-10-11: exchange/catalog/Smart Pay wACP ×10; teleport/Barsuk/dark-matter/time-machine off public surface |

## Immediate Finish Plan

1. ~~Deploy truth + docs sync~~ — **DONE**: git state verified clean, docs audited, stale notes corrected.
2. ~~Fix the remaining deploy-truth blockers~~ — **DONE**: .gitignore updated, `start-claude.bat` added, working tree clean, push verified.
3. Production deploy (run on host):
   - Pull latest on the target server / host clone.
   - Ensure a real absolute `DATABASE_URL` (not insecure local bundled-db default credentials; if it targets the bundled compose `postgres` service — whether via authority host `@postgres:...` or socket/query host `?host=postgres` — it must include the real DB password, not a placeholder-like password), a real non-default `POSTGRES_PASSWORD` for that bundled compose postgres service, plus real random `SECRET_KEY`, `CURSOR_SECRET`, and `CRON_SECRET` values (not placeholder-like strings) are set in the host shell or repo-root `.env` before starting `docker-compose.prod.yml`; when using the bundled compose postgres service, `DATABASE_URL` and `POSTGRES_PASSWORD` must stay in sync, and the compose file now passes `POSTGRES_PASSWORD` through to the API container so the app can enforce that parity at runtime instead of only in helper-script preflight.
   - Use `docs/PRODUCTION_SECRET_BASELINE.md` as the operator-side checklist/evidence format for keeping that state true on future staging/production deploys; on the current host/runtime, the required secret set is already provisioned outside the repo and the prod-like health checks are passing.
   - `docker compose -f docker-compose.prod.yml config --quiet` should now fail immediately if any of those required secrets are unset, without printing resolved secrets.
   - Run `alembic upgrade head`.
   - Run `./scripts/deploy-ancap-cloud.ps1` (or `.sh` on Linux); both helpers now run `docker compose -f docker-compose.prod.yml config --quiet` before build/start, then verify the live proxy path end-to-end via `/api/v1/system/health`, `/api/v1/system/ready`, and `/internal/frontend-build` before declaring success. The `-SkipPostDeployChecks` / `--skip-post-deploy-checks` bypass exists only for controlled staged-test contexts and must stay off for the real host deploy path.
   - Verify `https://ancap.cloud/internal/frontend-build` shows real `NEXT_PUBLIC_APP_BUILD_ID` matching `git rev-parse --short HEAD`.
   - Smoke test `ancap.cloud` routes and API health endpoints.

## Verified runtime truth snapshot (2026-05-23)

Local prod-like stack:
- `http://localhost:8080/` -> `200`
- `http://localhost:8080/api/v1/system/health` -> `200 {"status":"ok"}`
- `http://localhost:8080/openapi.json` -> `200`
- `http://localhost:8080/api/docs` -> `200`
- `http://localhost:8080/api/v1/users/me` -> `401`
- `http://localhost:9080` -> `200`
- Docker containers up: `ancap-proxy-1`, `ancap-frontend-1`, `ancap-api-1 (healthy)`, `ancap-postgres-1 (healthy)`, `ancap-redis-1 (healthy)`, `ancap-acp-node-1`, `searxng`

Production smoke:
- `https://ancap.cloud/` -> `200`
- `https://ancap.cloud/api/v1/system/health` -> `200 {"status":"ok"}`
- `https://ancap.cloud/api/v1/system/health/full` -> `200` with healthy `database`, `redis`, `llm`, and `bridge` checks
- `https://ancap.cloud/internal/frontend-build` -> `200`, route is implemented; **to show real build id** run deploy script on host so `APP_BUILD_ID` is injected as `--build-arg`, and only treat the deploy as successful once that route reports the same build id through the live proxy

Security/truth notes from the same check:
- Local proxy currently returns the desired hardening posture: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: geolocation=(), microphone=(), camera=()`, `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- `infra/nginx/default.conf` now also hides upstream `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, and `Strict-Transport-Security` on every proxied location before re-adding the canonical proxy header set, preventing duplicate FastAPI+nginx security headers in the prod-like stack.
- Local live re-check after `nginx -s reload` confirms `/` and `/api/v1/system/health` now return a single canonical header set instead of duplicate upstream+proxy copies.
- Production currently still differs: `https://ancap.cloud/api/v1/system/health` returns stale headers (`X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: same-origin`), so ancap.cloud still needs a real deploy/reload of the updated nginx config.
- Static sensitive paths (`/.env`, `/.env.example`, `/.git/config`, `/docker-compose.yml`, `/admin`) returned `404` locally and on production.
- `TRACE /` returned `405` locally and on production.

## Bridge truth snapshot

As of the latest verified runtime check:
- `GET /api/v1/bridge/status` locally and on production shows bridge rail enabled and not paused.
- Reverse public status is no longer `pending-rollout` in runtime; current API behavior exposes:
  - `redeem_available=true` when reserve health is not critical
  - `redeem_mode="live"`
- Runtime code in `app/api/routers/bridge_rail.py` explicitly states that the `BSC -> ACP` redeem path is live with funded reserve and automated payout processing.
- Therefore any docs still saying public reverse status must remain `pending-rollout` are stale and must be corrected.

## LLM Provider Reliability (DONE ✅)

All Phase 3 items complete:
- Failure taxonomy: unavailable / invalid_model / auth_error / balance_error / timeout / unknown
- Provider health in `/system/health/full` (probe_status, probe_error)
- LLM usage events with provider_status, failure_reason, retry_count, fallback_mode
- Retry with exponential backoff (max_retries=2)
- Degraded receipts when template fallback used
- Owner dashboards surface degraded runs

## AI / ISO Governance Track (DONE ✅)

All Phase 4 items complete:
- AI system cards for premium governance workflows (`ai_system_card` in WorkflowTemplatePublic)
- Degraded-output filters in owner dashboards (`degraded_run`, `degraded_reason`)
- Evidence export per paid workflow run (`GET /workflow-store/runs/{id}/evidence-export`)
- Full ISO/AI governance notes in `docs/AI_ISO_GOVERNANCE_NOTES.md`

## Public APIs And Interfaces

Available or in progress:

- `GET /system/health/full`
- `GET /metrics`
- `GET /workflow-store/runs/{id}/events`
- `GET /search`
- `GET/POST /webhooks`
- `GET /webhooks/{id}/deliveries`
- `GET /webhooks/{id}/deliveries/{delivery_id}`
- `POST /webhooks/{id}/deliveries/{delivery_id}/replay`
- `POST /webhooks/{id}/test`
- `GET/POST /organizations`
- `GET/PATCH /organizations/{id}`
- `GET/POST /organizations/{id}/members`
- `GET /organizations/{id}/audit`
- `GET /organizations/{id}/audit/export`
- `POST/GET/DELETE /organizations/{id}/api-keys`
- `GET /admin/audit-log`
- `GET /bridge/admin/snapshots`
- `GET /bridge/admin/alerts`

Frontend routes currently verified locally/build-safe:

- `/ai/workflows`
- `/billing`
- `/developers`
- `/developers/webhooks`
- `/organizations`
- `/organizations/[id]`
- `/strategy-builder`
- `/dashboard/analytics`
- `/proof-center`

## Test Plan

Current test status (2026-05-24):
- `pytest -q` -> **258 passed, 3 skipped** ✅
- `npm test --workspaces --if-present` (mobile SDK) -> **56 tests across 5 packages** ✅ (added `wallet-service` unit tests)
- `npx tsc -p apps/acp-wallet-expo/tsconfig.json --noEmit` -> ✅

All backend phases green. Mobile SDK TypeScript clean.

Production smoke targets to keep using:

- `https://ancap.cloud/`
- `https://ancap.cloud/ai/workflows`
- `https://ancap.cloud/billing`
- `https://ancap.cloud/developers`
- `https://ancap.cloud/developers/webhooks`
- `https://ancap.cloud/organizations`
- `https://ancap.cloud/strategy-builder`
- `https://ancap.cloud/proof-center`
- `https://ancap.cloud/aeterna`
- `/api/v1/system/health`
- `/api/v1/system/health/full`
- `/api/v1/metrics`
- `/internal/frontend-build`

## Later Expansion

- Replace the lightweight Strategy Builder with a React Flow canvas once the current builder and version API are stable.
- Add Playwright smoke to CI for buyer, creator, developer, webhooks, organizations, and receipt flows (Phase 7).
- Organizations-owned API keys [DONE: POST/GET/DELETE /organizations/{id}/api-keys].
- Signed webhook retry dashboard with replay controls [DONE: GET /webhooks/{id}/deliveries/{id}, POST /webhooks/{id}/deliveries/{id}/replay].
- Consider fiat/Stripe only after ACP checkout, receipts, and creator payouts are stable.
- **Securities intake** (securities / promissory notes / shares) — org treasury register, review, custody stub, haircut pledge to ACP escrow. Track: docs/SECURITIES_INTAKE_ROADMAP.md · Master priority **R9** · Phases S0–S5. Start after org identity + ACP checkout are stable; MVP = S1+S2.
- **Apple Watch employee fleet** — 3 watches per worker (different bands), heart-rate sync via HealthKit/watchOS, mandatory charge/rotation windows. Track: docs/mobile/APPLE_WATCH_EMPLOYEE_FLEET.md · Master **R10** · Mobile Phase **5.6**. Consent-gated; feature flag pple_watch_vitals.
- **SpaceX encrypted satellite servers** - launch sealed/encrypted ANCAP edge nodes via SpaceX rideshare/manifest; ground HSM unlock; ACP orbital-edge later. Track: docs/SPACEX_SATELLITE_ENCRYPTED_SERVERS_ROADMAP.md · Master **R11** · Phases X0-X5. Long-horizon; does not block Phase 6.
- **AETERNA longevity marketplace** — DNA vault + Sequencing.com-style import + ACP-paid genomic/longevity consult workflows (1,000,000 ACP) + **15-axis molecular aging profile** (blood-RNA / PCR panel metadata; configuration of aging, not one bio-age number) + **partial mRNA-reprogramming consult** (Daewoong eTurna USPTO notice-of-allowance literacy as of 11 Sep 2026; not an approved drug) + stem-cell organ print (250,000 ACP / organ, wisdom-tooth DPSC fallback, licensed bioreactor partner only) + **veterinary organ rails** (feline tissue cryoconservator-restorer 75,000 ACP; canine VET REGEN POD 180,000 ACP; conceptual partner architecture, licensed veterinarian only; `/legal/vet-regen`) + **Vinci light chamber** (48,000 ACP photobiomodulation / LED session protocol; Leonardo sunlight-health literacy; licensed phototherapy partner only; no safe-tanning or CE/FDA device claim; `/legal/light-chamber`) + **microwave body contouring** (52,000 ACP contact-cooled 2.45 / 5.8 GHz ISM applicator; licensed aesthetic/dermatology partner only; not liposuction; no CE/FDA or guaranteed fat-loss claim; `/legal/body-contouring`) + **BioFusion micromanipulation chamber** (88,000 ACP IVF/ICSI / plant pollination / BSL-lab partner brief; not a fertility clinic; `/legal/biofusion`) + **wisdom-tooth DPSC biomaterial** (65,000 ACP licensed bioreactor construct, not a full organ; `/legal/dpsc`) + **Vascular Care+** (54,000 ACP anhydrous N2+O2 + light-wave; licensed phlebology/aesthetic partner only; `/legal/vascular-care-plus`) + **Vascular Care** (58,000 ACP ultrasound/RF/thermal; `/legal/vascular-care`) + **needle-free transdermal pistol** (46,000 ACP aerosol + carrier gas; licensed clinic partner only; `/legal/transdermal`) + **M-receptor delivery subscription** (12,000 ACP / month; patch / iontophoresis / inhaler / vagus-adjacent neuromodulation; licensed clinic retainer only; `/legal/m-receptor`) + **artificial oxygen carrier** (92,000 ACP hemoglobin-vesicle / PFC-emulsion architecture literacy; licensed bioreactor / transfusion-medicine partner only; not a blood product; `/, synthetic blood / Black Mamba architecture (98,000 ACP multi-layer HBOC/PFC + modified peptide literacy; licensed bioreactor partner only; /legal/synthetic-blood-mamba)legal/oxygen-carrier`). Track: docs/AETERNA_LONGEVITY_MARKETPLACE_ROADMAP.md · Master **R12** · Phases A0–A5. No DIY CRISPR / LNP recipes; no institute affiliation claims; does not block Phase 6.
- **Lunar land trading** — ACP-settled selenographic parcel registry + interest desk with NASA–IBM Lunar Foundation Model science themes (ice / volcanism / crater). Track: docs/LUNAR_LAND_TRADING_ROADMAP.md · Master **R13** · Phases L0–L4. Speculative registry claims only (Outer Space Treaty disclaimer); does not block Phase 6.
- **Embodied AI security** — open humanoid / VLA models (e.g. UnifoLM-WLA-1.0) stay off settlement hosts; `FF_EMBODIED_ADAPTER` default false; public status `GET /v1/embodied-ai/security`; controls in `docs/EMBODIED_AI_SECURITY_CONTROLS.md`.
- **Crypto Benchmark Library (QOBLIB-style)** — public scorecard for ACP/wACP/sACP rails vs published baselines; `GET /v1/crypto/benchmark` · `/reserves` · `docs/CRYPTO_BENCHMARK_LIBRARY.md`. Snapshot-backed reserve proof + stale/mismatch transparency on public surfaces.

