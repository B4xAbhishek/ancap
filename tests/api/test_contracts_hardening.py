from decimal import Decimal

from tests.conftest import unique_email, unique_name


def _register_and_login(client) -> str:
    email = unique_email()
    password = "password123"
    r = client.post("/v1/auth/users", json={"email": email, "password": password, "display_name": "Contracts Hardening"})
    assert r.status_code in (201, 400), r.text
    login = client.post("/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def _create_agent(client, token: str, role: str) -> str:
    r = client.post(
        "/v1/agents",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": unique_name(f"hard_{role}"), "public_key": "x" * 32, "roles": [role]},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _deposit(client, token: str, owner_type: str, owner_id: str, amount: str, currency: str = "VUSD"):
    # /v1/ledger/* endpoints require an authenticated user and check that the user
    # owns the target account. Helper threads the bearer token through.
    r = client.post(
        "/v1/ledger/deposit",
        headers={
            "Idempotency-Key": unique_name("idk_hard_deposit"),
            "Authorization": f"Bearer {token}",
        },
        json={
            "account_owner_type": owner_type,
            "account_owner_id": owner_id,
            "amount": {"amount": amount, "currency": currency},
        },
    )
    assert r.status_code == 201, r.text


def _balance(client, token: str, owner_type: str, owner_id: str, currency: str = "VUSD") -> Decimal:
    r = client.get(
        "/v1/ledger/balance",
        params={"owner_type": owner_type, "owner_id": owner_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    for b in r.json().get("balances") or []:
        if b.get("currency") == currency:
            return Decimal(str(b.get("amount") or "0"))
    return Decimal("0")


def _create_strategy_and_pool(client, owner_agent_id: str, base_vertical_id: str):
    strat = client.post(
        "/v1/strategies",
        json={"name": unique_name("hard_strategy"), "vertical_id": base_vertical_id, "owner_agent_id": owner_agent_id},
    )
    assert strat.status_code == 201, strat.text
    sid = strat.json()["id"]
    workflow = {"vertical_id": base_vertical_id, "version": "1.0", "steps": [{"id": "s1", "action": "const", "args": {"value": 1}}]}
    ver = client.post(f"/v1/strategies/{sid}/versions", json={"semver": "1.0.0", "workflow": workflow})
    assert ver.status_code == 201, ver.text
    vid = ver.json()["id"]
    pool = client.post("/v1/pools", json={"name": unique_name("hard_pool"), "risk_profile": "experimental"})
    assert pool.status_code == 201, pool.text
    return vid, pool.json()["id"]


def test_run_under_contract_requires_auth_and_worker(client, base_vertical_id):
    token = _register_and_login(client)
    # user owns exactly one agent -> will be used as worker identity
    worker = _create_agent(client, token, "buyer")
    employer = _create_agent(client, token, "seller")
    _deposit(client, token, "agent", employer, "50")

    c = client.post(
        "/v1/contracts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employer_agent_id": employer,
            "worker_agent_id": worker,
            "scope_type": "generic",
            "scope_ref_id": None,
            "title": "Hardening per_run",
            "description": "",
            "payment_model": "per_run",
            "fixed_amount_value": "3",
            "currency": "VUSD",
            "max_runs": 1,
            "risk_policy_id": None,
            "created_from_order_id": None,
        },
    )
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    if c.json()["status"] == "draft":
        client.post(f"/v1/contracts/{cid}/propose", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/v1/contracts/{cid}/accept", headers={"Authorization": f"Bearer {token}"})

    vid, pool_id = _create_strategy_and_pool(client, worker, base_vertical_id)

    # Not authenticated -> 401 when contract_id provided.
    # Empty Authorization header opts out of the session-wide default token
    # (see _AuthedTestClient in conftest.py).
    r0 = client.post(
        "/v1/runs",
        headers={"Idempotency-Key": unique_name("idk_run0"), "Authorization": ""},
        json={"strategy_version_id": vid, "pool_id": pool_id, "params": {}, "limits": {}, "dry_run": True, "run_mode": "mock", "contract_id": cid},
    )
    assert r0.status_code == 401, r0.text


def test_per_run_one_run_one_payout_and_max_runs(client, base_vertical_id):
    token = _register_and_login(client)
    worker = _create_agent(client, token, "buyer")
    employer = _create_agent(client, token, "seller")
    _deposit(client, token, "agent", employer, "50")

    c = client.post(
        "/v1/contracts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employer_agent_id": employer,
            "worker_agent_id": worker,
            "scope_type": "generic",
            "scope_ref_id": None,
            "title": "Hardening per_run",
            "description": "",
            "payment_model": "per_run",
            "fixed_amount_value": "4",
            "currency": "VUSD",
            "max_runs": 1,
            "risk_policy_id": None,
            "created_from_order_id": None,
        },
    )
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    if c.json()["status"] == "draft":
        client.post(f"/v1/contracts/{cid}/propose", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/v1/contracts/{cid}/accept", headers={"Authorization": f"Bearer {token}"})

    vid, pool_id = _create_strategy_and_pool(client, worker, base_vertical_id)

    before = _balance(client, token, "agent", worker)
    run = client.post(
        "/v1/runs",
        headers={"Idempotency-Key": unique_name("idk_run1"), "Authorization": f"Bearer {token}"},
        json={"strategy_version_id": vid, "pool_id": pool_id, "params": {}, "limits": {}, "dry_run": True, "run_mode": "mock", "contract_id": cid},
    )
    assert run.status_code == 201, run.text
    run_id = run.json()["id"]

    after = _balance(client, token, "agent", worker)
    assert after >= before + Decimal("4")

    # Attempt second run should be blocked by max_runs (runs_completed reserved atomically)
    run2 = client.post(
        "/v1/runs",
        headers={"Idempotency-Key": unique_name("idk_run2"), "Authorization": f"Bearer {token}"},
        json={"strategy_version_id": vid, "pool_id": pool_id, "params": {}, "limits": {}, "dry_run": True, "run_mode": "mock", "contract_id": cid},
    )
    assert run2.status_code == 403, run2.text

    # Ledger has exactly one contract_payout for (contract_id, run_id)
    ev = client.get(
        "/v1/ledger/events",
        params={"limit": 200, "type": "contract_payout"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ev.status_code == 200, ev.text
    items = ev.json().get("items") or []
    hits = [e for e in items if (e.get("metadata") or {}).get("contract_id") == cid and (e.get("metadata") or {}).get("run_id") == run_id]
    assert len(hits) == 1

