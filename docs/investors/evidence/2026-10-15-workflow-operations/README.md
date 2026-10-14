# Workflow Studio release evidence

Published build: `e53f949` (full merge SHA in `results.json`).

- [Merged PR #89](https://github.com/ancapcloud/ancap/pull/89)
- [Successful deployment](https://github.com/ancapcloud/ancap/actions/runs/38648982401)
- [Full backend CI](https://github.com/ancapcloud/ancap/actions/runs/38648155226): 907 passed, 34 skipped.
- [Frontend/mobile/browser CI](https://github.com/ancapcloud/ancap/actions/runs/38648155184): 50 frontend, 281 mobile SDK, 27 browser scenarios passed; one browser scenario skipped.
- [Live Studio](https://ancap.cloud/ai/studio) and [integration instructions](https://ancap.cloud/docs/workflow-operations).

Read-only production checks verified build identity, readiness, advancing queue
heartbeat, public routes/downloads and denied unauthenticated private endpoints.
The browser check covered all five languages and 390-pixel width, with no JavaScript
errors or horizontal overflow. `results.json` records timestamps and test scope.

This verifies implementation/release checks, not customer revenue or live delivery
to customer accounts. Provider/connector integration tests used synthetic credentials
and mocks. Infrastructure/keys for private installations are customer supplied.
Supplier invoices and cash margin remain unverified. Provider API calls can repeat
following an interrupted execution; ACP captures remain protected by transaction
boundaries, and separate provider billing must be reconciled.

Security limitations are explicit: production npm frontend dependencies audited to
zero findings; seven high build-tool findings rooted in the upstream braces advisory
remain. The repository's last Dependabot report has 93 existing findings (51 high,
30 moderate, 12 low). CodeQL passed with one informational lifecycle-yield note;
the async context manager's yield is required for startup/shutdown handover.

No Stripe payments, chain broadcasts or real external messages were sent during
verification. Original wallet/consensus/bridge/SACP WIP was excluded. This documentation
follow-up does not alter the deployed application build.
