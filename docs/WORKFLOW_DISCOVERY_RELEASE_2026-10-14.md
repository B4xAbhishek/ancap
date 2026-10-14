# Workflow discovery release — 14 October 2026

## User features

- Task-based discovery: token risk, listing, growth or integration. Matching is deterministic and uses only offers present in the supplied catalog.
- Browser shortlist: save and revisit workflows; duplicates and obsolete catalog entries are removed. This is local browser storage, not account synchronization.
- Compare up to three workflows: outputs, per-run price and estimated runtime.
- Monthly run-cost planning: exact decimal multiplication in each offer's currency; no assumed ACP/EUR conversion and no automatic billing.
- Download the comparison as JSON with source/price/output information and the planning count.

The existing reference-catalog warning remains visible when the backend catalog is unavailable. Checkout remains responsible for the actual price and payment.

## Investor feature

The investor overview exposes the recorded local Ollama demonstration and links directly to its immutable receipt, generated artifact and evidence archive. It labels the run as a local test-credit demonstration, not customer revenue or production-provider acceptance.

## Verification and release scope

Release implementation is isolated from uncommitted mobile/consensus/bridge/SACP work in a separate Git worktree. No payment, signing, token issuance or database schema changes are included in this release.

Initial local checks: frontend 46 unit tests and 12 browser checks passed; production frontend build passed. Mobile workspace type checks and 281 unit tests passed for the committed release baseline. Full backend and Rust/contract verification are recorded separately as they complete.

Deployment now requires fetched master to equal the requested GitHub deployment commit and does not ignore reset failure. Production deployment and public checks must be confirmed before marking this release shipped.

## Security and regression follow-up

- Replaced vulnerable python-jose with PyJWT, retaining existing HS256 token claims and requiring signed expiry and a string subject. Seven security cases cover expired, incomplete, malformed, oversized and wrong-algorithm tokens. Test signing keys are explicit.
- Updated frontend compatible dependency versions; patched PostCSS and selector parsing through overrides. Updated mobile tar and shell-quote overrides; removed the unused stale pnpm lock (npm is the supported workspace installer).
- Updated Rust lockfile quinn-proto to 0.11.18 and rustls to 0.23.46 after the CI audit reported nine vulnerabilities. No consensus, bridge or wallet implementation WIP was imported.
- Local final checks: 46 frontend unit tests, 15 public browser scenarios, frontend production build, 281 mobile unit tests and workspace type checks passed; Rust crypto/node/mobile FFI tests passed. Authentication/dependency regressions: 16 passed.
- Residual npm advisories remain: frontend 7 high reports trace to unpatched braces in build/lint glob tooling; mobile 63 high and 10 moderate reports require a separately tested Expo/tooling upgrade. Both active npm locks report zero critical findings. Rust unmaintained-crate warnings remain a migration task. These counts are the 14 October snapshot, not a security certification.
- Full backend/CI results and deployment are pending at this commit.
