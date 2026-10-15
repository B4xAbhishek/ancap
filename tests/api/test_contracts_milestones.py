from decimal import Decimal

from tests.conftest import unique_email, unique_name


def _register_and_login(client) -> str:
    email = unique_email()
    password = "password123"
    r = client.post("/v1/auth/users", json={"email": email, "password": password, "display_name": "Milestones Test"})
    assert r.status_code in (201, 400), r.text
    login = client.post("/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def _create_agent(client, token: str, role: str) -> str:
    r = client.post(
        "/v1/agents",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": unique_name(f"ms_{role}"), "public_key": "x" * 32, "roles": [role]},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _deposit(client, token: str, owner_type: str, owner_id: str, amount: str, currency: str = "VUSD"):
    r = client.post(
        "/v1/ledger/deposit",
        headers={
            "Idempotency-Key": unique_name("idk_ms_deposit"),
            "Authorization": f"Bearer {token}",
        },
        json={"account_owner_type": owner_type, "account_owner_id": owner_id, "amount": {"amount": amount, "currency": currency}},
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
    strat = client.post("/v1/strategies", json={"name": unique_name("ms_strategy"), "vertical_id": base_vertical_id, "owner_agent_id": owner_agent_id})
    assert strat.status_code == 201, strat.text
    sid = strat.json()["id"]
    workflow = {"vertical_id": base_vertical_id, "version": "1.0", "steps": [{"id": "s1", "action": "const", "args": {"value": 1}}]}
    ver = client.post(f"/v1/strategies/{sid}/versions", json={"semver": "1.0.0", "workflow": workflow})
    assert ver.status_code == 201, ver.text
    vid = ver.json()["id"]
    pool = client.post("/v1/pools", json={"name": unique_name("ms_pool"), "risk_profile": "experimental"})
    assert pool.status_code == 201, pool.text
    return vid, pool.json()["id"]


def test_fixed_milestones_partial_payout_and_refund(client, base_vertical_id):
    token = _register_and_login(client)
    employer = _create_agent(client, token, "seller")
    worker = _create_agent(client, token, "buyer")
    _deposit(client, token, "agent", employer, "50")

    c = client.post(
        "/v1/contracts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employer_agent_id": employer,
            "worker_agent_id": worker,
            "scope_type": "generic",
            "scope_ref_id": None,
            "title": "Fixed staged",
            "description": "",
            "payment_model": "fixed",
            "fixed_amount_value": "30",
            "currency": "VUSD",
            "max_runs": None,
            "risk_policy_id": None,
            "created_from_order_id": None,
        },
    )
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    if c.json()["status"] == "draft":
        client.post(f"/v1/contracts/{cid}/propose", headers={"Authorization": f"Bearer {token}"})

    # Create milestones (sum <= fixed_amount_value)
    m1 = client.post(
        f"/v1/milestones/contracts/{cid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "M1", "description": "", "order_index": 1, "amount_value": "10", "currency": "VUSD"},
    )
    assert m1.status_code == 201, m1.text
    m2 = client.post(
        f"/v1/milestones/contracts/{cid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "M2", "description": "", "order_index": 2, "amount_value": "15", "currency": "VUSD"},
    )
    assert m2.status_code == 201, m2.text
    mid1 = m1.json()["id"]

    # Mark milestone active (MVP)
    client.patch(
        f"/v1/milestones/{mid1}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "active"},
    )

    # Accept contract -> escrow funded
    a = client.post(f"/v1/contracts/{cid}/accept", headers={"Authorization": f"Bearer {token}"})
    assert a.status_code == 200, a.text

    before_worker = _balance(client, token, "agent", worker)
    # Accept milestone -> partial payout from escrow
    am1 = client.post(f"/v1/milestones/{mid1}/accept", headers={"Authorization": f"Bearer {token}"})
    assert am1.status_code == 200, am1.text
    after_worker = _balance(client, token, "agent", worker)
    assert after_worker >= before_worker + Decimal("10")

    # Cancel contract -> refund remainder
    before_employer = _balance(client, token, "agent", employer)
    cancel = client.post(f"/v1/contracts/{cid}/cancel", headers={"Authorization": f"Bearer {token}"})
    assert cancel.status_code == 200, cancel.text
    after_employer = _balance(client, token, "agent", employer)
    assert after_employer >= before_employer


def test_per_run_milestone_budget_cap(client, base_vertical_id):
    token = _register_and_login(client)
    employer = _create_agent(client, token, "seller")
    worker = _create_agent(client, token, "buyer")
    _deposit(client, token, "agent", employer, "50")

    c = client.post(
        "/v1/contracts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employer_agent_id": employer,
            "worker_agent_id": worker,
            "scope_type": "generic",
            "scope_ref_id": None,
            "title": "Per-run staged",
            "description": "",
            "payment_model": "per_run",
            "fixed_amount_value": "7",
            "currency": "VUSD",
            "max_runs": None,
            "risk_policy_id": None,
            "created_from_order_id": None,
        },
    )
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    if c.json()["status"] == "draft":
        client.post(f"/v1/contracts/{cid}/propose", headers={"Authorization": f"Bearer {token}"})
    client.post(f"/v1/contracts/{cid}/accept", headers={"Authorization": f"Bearer {token}"})

    # Milestone budget 10, per-run payout 7 -> first run pays 7, second run pays 3
    m = client.post(
        f"/v1/milestones/contracts/{cid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Budgeted", "description": "", "order_index": 1, "amount_value": "10", "currency": "VUSD", "required_runs": 3},
    )
    assert m.status_code == 201, m.text
    mid = m.json()["id"]
    # Mark milestone active via patch (MVP)
    client.patch(
        f"/v1/milestones/{mid}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "active"},
    )

    vid, pool_id = _create_strategy_and_pool(client, worker, base_vertical_id)
    before = _balance(client, token, "agent", worker)

    r1 = client.post(
        "/v1/runs",
        headers={"Idempotency-Key": unique_name("idk_ms_run1"), "Authorization": f"Bearer {token}"},
        json={"strategy_version_id": vid, "pool_id": pool_id, "params": {}, "limits": {}, "dry_run": True, "run_mode": "mock", "contract_id": cid, "contract_milestone_id": mid},
    )
    assert r1.status_code == 201, r1.text
    mid_balance1 = _balance(client, token, "agent", worker)
    assert mid_balance1 >= before + Decimal("7")

    r2 = client.post(
        "/v1/runs",
        headers={"Idempotency-Key": unique_name("idk_ms_run2"), "Authorization": f"Bearer {token}"},
        json={"strategy_version_id": vid, "pool_id": pool_id, "params": {}, "limits": {}, "dry_run": True, "run_mode": "mock", "contract_id": cid, "contract_milestone_id": mid},
    )
    assert r2.status_code == 201, r2.text
    after = _balance(client, token, "agent", worker)

    # Total payout capped at 10
    assert after >= before + Decimal("10")
    assert after <= before + Decimal("10.000000000000000001")


