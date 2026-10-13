# ANCAP docs repo Discussions seed

Status: active prep for the future public `ancap-docs` repository.

This file captures the initial GitHub Discussions shape for the future public docs repo so the first public community surface starts with clear lanes instead of one undifferentiated thread bucket.

## Goal

Enable GitHub Discussions with a small, public-safe category set that helps contributors separate ideas, support questions, and integration/audit conversation.

## Recommended categories

### 1. `Ideas`
Use for:
- docs improvements
- proposed repo structure improvements
- public transparency/trust improvements
- future public-safe split ideas (`ancap-sdk`, `ancap-contracts`, `ancap-examples`)

### 2. `Q&A`
Use for:
- integration questions
- docs clarification requests
- contract verification questions
- bridge-risk / trust-surface questions that do not contain private operator details

### 3. `Show and tell`
Use for:
- public integrations built on ANCAP docs/specs
- example tooling
- tutorials and walkthroughs
- public merchant/wallet/dev experiments

### 4. `Announcements`
Use for:
- docs repo milestone updates
- release-note pointers
- public roadmap/status updates
- audit-readiness and transparency updates

## Moderator rules

- Keep Discussions public-safe: no secrets, private infra details, wallet keys, deploy tokens, or signer/operator runbooks.
- Move actionable bug reports and feature requests into Issues when they need tracking.
- Redirect security disclosures to `SECURITY.md` instead of handling them in public threads.
- Prefer Discussions for exploratory conversation and Issues for concrete work items.

## Suggested first pinned topics

1. **Welcome / how to use this repo**
   - explain what `ancap-docs` is for
   - point to roadmap/status/docs entry points
   - remind contributors not to post secrets or operator-only details

   Suggested starter copy:

   ```md
   # Welcome to ANCAP docs

   This repo is the public-safe docs and trust surface for ANCAP.
   Use it to inspect roadmap/status truth, architecture and whitepapers, bridge-risk and verification guidance, and public integration examples.

   Start here:
   - `MASTER_ROADMAP.md`
   - `docs/STATUS_MATRIX.md`
   - `docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md`
   - `README.md`

   Please do **not** post secrets, wallet keys, deploy tokens, private infrastructure details, or operator-only runbooks here.
   ```

2. **Where to ask what**
   - Issues → concrete bugs/features/docs tasks
   - Discussions → questions, ideas, integration chatter
   - Security reports → `SECURITY.md`

   Suggested starter copy:

   ```md
   # Where to ask what

   Use the right lane so work stays searchable and public-safe:

   - **Issues** → concrete bugs, feature requests, docs fixes, and tracked tasks
   - **Discussions / Q&A** → integration questions, docs clarification, and exploratory ideas
   - **Discussions / Show and tell** → public experiments, examples, and walkthroughs
   - **Security reports** → follow `SECURITY.md`; do not post disclosures in public threads

   If a Discussion turns into concrete work, move it into an Issue.
   ```

3. **Public scope boundaries**
   - clarify what ANCAP publishes here
   - clarify what remains private by design

   Suggested starter copy:

   ```md
   # Public scope boundaries

   This repo is for public-safe ANCAP material such as:
   - roadmap and status truth
   - architecture, whitepapers, and public-facing trust docs
   - public contract verification guidance
   - public integration examples and contributor workflow metadata

   This repo is **not** for:
   - private keys, mnemonics, API tokens, or production `.env` values
   - signer internals, hot-wallet operating procedures, or abuse-sensitive controls
   - private infrastructure/admin runbooks

   If you are unsure whether something is safe to post publicly, do not post it here.
   ```

## Bootstrap usage

During the first `ancap-docs` repo setup:

1. Enable GitHub Discussions.
2. Create the categories above.
3. Add the pinned welcome/scope/routing topics.
4. Copy or adapt the starter text from this file or `.github/bootstrap/ancap-docs-discussions.json` instead of drafting those pinned posts from scratch during launch.
5. Link the Discussions surface from the root `README.md` or repo sidebar when the public repo exists.

## Current live follow-up state

The public repo now already has the three seeded bootstrap topics live at:
- `https://github.com/ancapcloud/ancap-docs/discussions/2` — `Welcome / how to use this repo`
- `https://github.com/ancapcloud/ancap-docs/discussions/3` — `Where to ask what`
- `https://github.com/ancapcloud/ancap-docs/discussions/4` — `Public scope boundaries`

Current honest drift against this seed:
- those three topics are still unpinned;
- live Discussions still carry extra default categories `General` and `Polls`;
- the seeded categories still use GitHub's stock live descriptions instead of the ANCAP-specific descriptions above;
- live project-board verification is still blocked under the current token because it lacks `read:project`.

Use `python scripts/bootstrap_ancap_docs_repo.py --repo <owner>/ancap-docs --verify-live --verify-live-community` to get an explicit operator action list for those remaining Discussions/project-board cleanup steps instead of re-deriving them manually. Current helper truth: GitHub's public GraphQL surface does expose `createDiscussion` / `updateDiscussion` for future missing-topic, topic-body, or category-reassignment automation, but the helper does not apply those mutations today, and the remaining category-description/pinning cleanup still needs GitHub UI or a future owner-capable automation path.

## Definition of done for this prep slice

This seed is doing its job when the future docs repo can open Discussions with clear public-safe defaults, minimal moderator ambiguity, and copy-ready pinned-topic text instead of needing to invent launch copy from scratch.
