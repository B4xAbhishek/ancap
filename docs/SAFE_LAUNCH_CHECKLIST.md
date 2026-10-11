# Safe launch checklist (2026-09-28)

Operator dry-run before treating ancap.cloud as “final launch”.

Evidence refreshed: 2026-09-28 (cloud agent pre-deploy pass on `cursor/ancap-safe-launch-d185`).

## Auth / API

- [x] `docker-compose.prod.yml` has `CORS_ORIGINS` including `https://ancap.cloud` and `https://www.ancap.cloud`
- [ ] Browser login from `ancap.cloud` → `api.ancap.cloud` sets `ancap_token` with `HttpOnly`, `Secure`, `SameSite=Lax`, `Domain=.ancap.cloud` *(post-deploy smoke)*
- [x] Network failure shows friendly API-unreachable copy (not raw `Failed to fetch`) — `frontend-app/src/lib/api.ts` `formatNetworkError`
- [x] `pytest tests/test_auth.py tests/test_cors_dev_stack.py -q` passes (local 2026-09-28)

## Free ACP / market honesty

- [ ] `GET /v1/market/free-distribution` reports cap / distributed / open *(route ships with this PR; live was 404 on `fac3b98`)*
- [x] Faucet rejects amount above `FAUCET_MAX_AMOUNT_ACP` (default 10) — covered by `tests/api/test_free_distribution.py`
- [x] When distributed ≥ 1_000_000 ACP or `FREE_ACP_DISTRIBUTION_ENABLED=false`, welcome/faucet/referral signup stop — covered by unit/API tests
- [x] `/buy-acp` and `/markets` copy distinguish desk quote vs wACP DEX spot vs promo credit

## Anti-sybil

- [x] Second registration from same device/IP within window does not receive welcome grant — `tests/api/test_anti_sybil_register.py`
- [x] Faucet for quarantined users returns `held` — faucet eligibility + idempotent held path
- [x] `faucet_abuse_check_tick` flags granted claims for review

## Theodore / security

- [x] `scripts/theodore-earn-promo.ps1` runs visibly; no `-WindowStyle Hidden`
- [x] Script refuses wallet/signer env vars
- [x] `python scripts/check_secret_hygiene.py` clean for pending push
- [x] Skim `docs/AUDIT_CHECKLIST.md` + `docs/CISCO_SECURITY_APPENDIX.md`

## wACP / listings

- [x] `python scripts/check_wacp_reserve_before_mint.py` fail-closed when proof is not healthy (live proof currently `status=degraded` → **do not mint/LP**)
- [x] Mint only to treasury/multisig after human confirm (no agent auto-mint) — policy docs + Theodore refuse keys
- [x] `/docs/wacp/metamask` and `/tokenlist.json` show canonical address only
- [x] CoinGecko submission (if any) uses **wACP**, never ticker ACP — markets/listings copy

## Legal / transparency

- [ ] Terms §3 residency draft reviewed by licensed counsel before relying on it *(operator / counsel)*
- [ ] Operator entity placeholders filled when Cyprus/other Ltd is incorporated *(operator)*
- [x] Public GitHub stays public-safe; secrets stay private (`OPEN_SOURCE_GITHUB_TRANSPARENCY.md`)

## New verticals (MVP)

- [ ] `/server-bounty` + `/v1/robot-ops/server-install-bounties` pending until operator verify *(post-deploy)*
- [x] Robot telemetry ingest requires active owner consent — API enforces consent
- [x] `/delivery` jobs are separate from strategy `/marketplace`

## Content

- [x] No “time machine / time lighter” lore anywhere (hero, footer, or product claims)
- [x] Teleport earphones + Project Barsuk retired from public AETERNA / workflow catalog / legal hub
- [x] Dark-matter auction unmounted from API + removed from Explore nav (DB tables kept)
- [x] Exchange / catalog / Smart Pay wACP math aligned to bridge **1 ACP ↔ 10 wACP**

## Migrations / deploy

- [x] Local `alembic upgrade head` → `080_safe_launch_controls`
- [ ] Production `alembic upgrade head` via `scripts/deploy-ancap-cloud.sh` (GitHub Actions Deploy on merge to `master`)
- [ ] Post-deploy: live `/v1/market/free-distribution` 200 + frontend build id matches merged SHA
