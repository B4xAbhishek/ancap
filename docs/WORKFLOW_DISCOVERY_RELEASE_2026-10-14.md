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
