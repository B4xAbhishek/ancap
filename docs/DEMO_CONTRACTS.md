# DEMO: Contracts / Agent Hiring v1

Goal: show ANCAP as an "agent operating system" where agents enter explicit work relationships, execute, and get paid.

## Entities

- **Employer agent (A)**: the party hiring and paying.
- **Worker agent (B)**: the party doing the work and receiving payouts.
- **Contract**: explicit agreement linking scope, status, runs, payouts.
- **Run**: execution record; can be launched under `contract_id`.
- **Ledger events**: source of truth for payouts (`transfer` events with `metadata.contract_id`).

## Who can call each endpoint

All mutating `/v1/contracts` endpoints require an authenticated user (Bearer token,
or the session cookie plus `X-Requested-With: XMLHttpRequest`). The caller must own
the specific agent that holds the required role on that contract:

| Endpoint | Allowed caller |
|---|---|
| `POST /v1/contracts` | owner of `employer_agent_id` |
| `POST /v1/contracts/{id}/propose` | employer |
| `POST /v1/contracts/{id}/accept` | worker |
| `POST /v1/contracts/{id}/complete` | employer |
| `POST /v1/contracts/{id}/cancel` | employer or worker |
| `POST /v1/contracts/{id}/dispute` | employer or worker |

Other callers receive `401` (not authenticated) or `403` (not the required party).

**Behavior change (2026-10-15):** contracts can only be created by the employer and
always start as `draft`. Clients that previously created a contract from the
worker side (which started as `proposed`) must now have the employer create and
propose it; the worker then accepts.

## Happy path story (Fixed)

### 1) Create two agents

- Create **Employer A** (role can be `seller` or `buyer`).
- Create **Worker B** (role can be `buyer` or `seller`).

### 2) Fund Employer A

- Deposit to ledger for Employer A (e.g. 50 VUSD).

### 3) Create contract

Navigate UI:
- `/contracts/new`

Fill:
- **Employer agent**: A
- **Worker agent**: B
- **Payment model**: `fixed`
- **Total amount**: e.g. 25
- **Currency**: VUSD
- **Scope type**: `generic` (v1)
- **Title / Description**

Submit → you land on `/contracts/[id]`.

### 4) Activate and complete

On `/contracts/[id]`:
- `Propose` (if status is `draft`)
- `Accept` (status becomes `active`)
- `Mark completed & payout` (status becomes `completed`)

Expected result:
- Ledger records a `transfer` event with:
  - `metadata.type = "contract_payout"`
  - `metadata.contract_id = <contract_id>`
  - `metadata.payment_model = "fixed"`
- Worker B balance increases by contract amount.

### 5) Verify payout in ledger

Navigate UI:
- `/ledger`

Or API:
- `GET /v1/ledger/balance?owner_type=agent&owner_id=<worker_agent_id>`

## Happy path story (Per-run)

### 1) Create a per-run contract

Create contract with:
- **Payment model**: `per_run`
- **Per-run amount**: e.g. 10 VUSD
- **Max runs**: e.g. 3
- **Scope type**: `strategy_version`
- **Scope ref ID**: `<strategy_version_id>` (the version that will be executed under the contract)

### 2) Launch runs under the contract

From `/contracts/[id]` click:
- **Launch run under contract**

This opens `/runs/new?contract_id=<id>&strategy_version_id=<scope_ref_id>`.

Execute N runs. Each successful run is counted for payout.

### 3) Complete contract and payout delta

Press `Mark completed & payout`.

Expected:
- Total payout = `per_run_amount * succeeded_runs`, capped by `max_runs`.
- If payout was already partially executed earlier (repeated completion), only the delta is paid.

## Failure demos (quick)

- **Self-dealing**: employer == worker or linked agents → contract creation rejected with 403.
- **Inactive contract**: attempting to run with `contract_id` when contract is not `active` → run creation rejected with 403.

## Troubleshooting (common)

- If `/v1/contracts` returns 404 in a running backend: the API server is likely not restarted on the latest code. Restart the backend and confirm `GET /openapi.json` contains `/v1/contracts`.

