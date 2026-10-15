"""Contract lifecycle endpoints must be restricted to the contract's parties."""
from decimal import Decimal

from tests.conftest import unique_email, unique_name


def _login(client) -> str:
    email = unique_email()
    password = "password123"
    r = client.post("/v1/auth/users", json={"email": email, "password": password, "display_name": "Contracts Authz"})
    assert r.status_code in (201, 400), r.text
    login = client.post("/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_agent(client, token: str, role: str) -> str:
    r = client.post(
        "/v1/agents",
        headers=_auth(token),
        json={"display_name": unique_name(f"authz_{role}"), "public_key": "x" * 32, "roles": [role]},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _deposit(client, token: str, agent_id: str, amount: str) -> None:
    r = client.post(
        "/v1/ledger/deposit",
        headers={**_auth(token), "Idempotency-Key": unique_name("idk_authz")},
        json={"account_owner_type": "agent", "account_owner_id": agent_id, "amount": {"amount": amount, "currency": "VUSD"}},
    )
    assert r.status_code == 201, r.text


def _balance(client, token: str, agent_id: str) -> Decimal:
    r = client.get("/v1/ledger/balance", params={"owner_type": "agent", "owner_id": agent_id}, headers=_auth(token))
    assert r.status_code == 200, r.text
    for b in r.json().get("balances") or []:
        if b.get("currency") == "VUSD":
            return Decimal(str(b.get("amount") or "0"))
    return Decimal("0")


def _contract_body(employer: str, worker: str, amount: str = "40") -> dict:
    return {
        "employer_agent_id": employer,
        "worker_agent_id": worker,
        "scope_type": "generic",
        "title": "Authz",
        "description": "",
        "payment_model": "fixed",
        "fixed_amount_value": amount,
        "currency": "VUSD",
    }


def test_contract_mutations_require_auth(client):
    for action in ("propose", "accept", "cancel", "complete", "dispute"):
        r = client.post(
            "/v1/contracts/00000000-0000-0000-0000-000000000000/" + action,
            headers={"Authorization": ""},
        )
        assert r.status_code == 401, (action, r.text)
    r = client.post("/v1/contracts", headers={"Authorization": ""}, json=_contract_body(
        "00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002"))
    assert r.status_code == 401, r.text


def test_outsider_cannot_drain_employer_via_contract(client):
    victim = _login(client)
    attacker = _login(client)
    victim_agent = _create_agent(client, victim, "seller")
    attacker_agent = _create_agent(client, attacker, "buyer")
    _deposit(client, victim, victim_agent, "50")

    # Attacker names the victim as employer and themselves as worker.
    r = client.post("/v1/contracts", headers=_auth(attacker), json=_contract_body(victim_agent, attacker_agent))
    assert r.status_code == 403, r.text
    assert _balance(client, victim, victim_agent) == Decimal("50")


def test_lifecycle_actions_enforce_party_roles(client):
    employer_tok = _login(client)
    worker_tok = _login(client)
    outsider_tok = _login(client)
    employer = _create_agent(client, employer_tok, "seller")
    worker = _create_agent(client, worker_tok, "buyer")
    _deposit(client, employer_tok, employer, "50")

    c = client.post("/v1/contracts", headers=_auth(employer_tok), json=_contract_body(employer, worker))
    assert c.status_code == 201, c.text
    assert c.json()["status"] == "draft"
    cid = c.json()["id"]

    assert client.post(f"/v1/contracts/{cid}/propose", headers=_auth(worker_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{cid}/propose", headers=_auth(employer_tok)).status_code == 200

    # Only the worker may accept (which escrows the employer's funds).
    assert client.post(f"/v1/contracts/{cid}/accept", headers=_auth(outsider_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{cid}/accept", headers=_auth(employer_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{cid}/accept", headers=_auth(worker_tok)).status_code == 200

    # Only the employer may release escrow to the worker.
    assert client.post(f"/v1/contracts/{cid}/complete", headers=_auth(worker_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{cid}/complete", headers=_auth(outsider_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{cid}/cancel", headers=_auth(outsider_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{cid}/dispute", headers=_auth(outsider_tok)).status_code == 403

    r = client.post(f"/v1/contracts/{cid}/complete", headers=_auth(employer_tok))
    assert r.status_code == 200, r.text
    assert _balance(client, worker_tok, worker) == Decimal("40")


def _proposed_contract(client, employer_tok: str, employer: str, worker: str) -> str:
    c = client.post("/v1/contracts", headers=_auth(employer_tok), json=_contract_body(employer, worker))
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    assert client.post(f"/v1/contracts/{cid}/propose", headers=_auth(employer_tok)).status_code == 200
    return cid


def _active_contract(client, employer_tok: str, worker_tok: str, employer: str, worker: str) -> str:
    cid = _proposed_contract(client, employer_tok, employer, worker)
    assert client.post(f"/v1/contracts/{cid}/accept", headers=_auth(worker_tok)).status_code == 200
    return cid


def _parties(client):
    employer_tok, worker_tok, outsider_tok = _login(client), _login(client), _login(client)
    employer = _create_agent(client, employer_tok, "seller")
    worker = _create_agent(client, worker_tok, "buyer")
    _deposit(client, employer_tok, employer, "200")
    return employer_tok, worker_tok, outsider_tok, employer, worker


def test_outsider_cannot_create_or_propose(client):
    employer_tok, worker_tok, outsider_tok, employer, worker = _parties(client)
    outsider_agent = _create_agent(client, outsider_tok, "buyer")

    # Outsider cannot create a contract for someone else's pair of agents,
    # nor name another user's agent as employer of their own worker.
    for body in (_contract_body(employer, worker), _contract_body(employer, outsider_agent)):
        r = client.post("/v1/contracts", headers=_auth(outsider_tok), json=body)
        assert r.status_code == 403, r.text

    c = client.post("/v1/contracts", headers=_auth(employer_tok), json=_contract_body(employer, worker))
    assert c.status_code == 201, c.text
    cid = c.json()["id"]
    assert client.post(f"/v1/contracts/{cid}/propose", headers=_auth(outsider_tok)).status_code == 403
    assert client.get(f"/v1/contracts/{cid}").json()["status"] == "draft"


def test_each_permitted_party_can_cancel_and_dispute(client):
    employer_tok, worker_tok, outsider_tok, employer, worker = _parties(client)

    for tok in (employer_tok, worker_tok):
        cid = _active_contract(client, employer_tok, worker_tok, employer, worker)
        assert client.post(f"/v1/contracts/{cid}/cancel", headers=_auth(outsider_tok)).status_code == 403
        r = client.post(f"/v1/contracts/{cid}/cancel", headers=_auth(tok))
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "cancelled"

    for tok in (employer_tok, worker_tok):
        cid = _active_contract(client, employer_tok, worker_tok, employer, worker)
        assert client.post(f"/v1/contracts/{cid}/dispute", headers=_auth(outsider_tok)).status_code == 403
        r = client.post(f"/v1/contracts/{cid}/dispute", headers=_auth(tok))
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "disputed"

    # Cancelled contracts refunded the employer's escrow in full.
    assert _balance(client, employer_tok, employer) == Decimal("120")


def test_ownership_is_checked_against_the_specific_contract_agent(client):
    employer_tok, worker_tok, outsider_tok, employer, worker = _parties(client)
    # The outsider owns several agents, none of which is party to the contract.
    _create_agent(client, outsider_tok, "seller")
    _create_agent(client, outsider_tok, "buyer")
    cid = _proposed_contract(client, employer_tok, employer, worker)
    assert client.post(f"/v1/contracts/{cid}/accept", headers=_auth(outsider_tok)).status_code == 403

    # A user whose first agent is not the employer can still act through a later one.
    multi_tok = _login(client)
    _create_agent(client, multi_tok, "buyer")
    second = _create_agent(client, multi_tok, "seller")
    _deposit(client, multi_tok, second, "40")
    c = client.post("/v1/contracts", headers=_auth(multi_tok), json=_contract_body(second, worker))
    assert c.status_code == 201, c.text
    assert c.json()["status"] == "draft"

    # The worker's owner holds an extra agent but must act as the contract's worker only.
    _create_agent(client, worker_tok, "seller")
    mcid = c.json()["id"]
    assert client.post(f"/v1/contracts/{mcid}/propose", headers=_auth(worker_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{mcid}/propose", headers=_auth(multi_tok)).status_code == 200
    assert client.post(f"/v1/contracts/{mcid}/accept", headers=_auth(multi_tok)).status_code == 403
    assert client.post(f"/v1/contracts/{mcid}/accept", headers=_auth(worker_tok)).status_code == 200
    assert client.post(f"/v1/contracts/{mcid}/complete", headers=_auth(worker_tok)).status_code == 403


def test_cookie_authenticated_mutations_require_x_requested_with(client):
    employer_tok, worker_tok, outsider_tok, employer, worker = _parties(client)
    cid = _proposed_contract(client, employer_tok, employer, worker)

    saved = client.default_token
    client.default_token = None  # rely on the session cookie only
    try:
        cookie = {"Cookie": f"ancap_token={worker_tok}"}
        r = client.post(f"/v1/contracts/{cid}/accept", headers=cookie)
        assert r.status_code == 403, r.text
        assert "X-Requested-With" in r.json()["detail"]
        assert client.get(f"/v1/contracts/{cid}").json()["status"] == "proposed"

        r = client.post(f"/v1/contracts/{cid}/accept", headers={**cookie, "X-Requested-With": "XMLHttpRequest"})
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "active"

        # A valid cookie for a non-party is still rejected by the ownership check.
        r = client.post(
            f"/v1/contracts/{cid}/complete",
            headers={"Cookie": f"ancap_token={outsider_tok}", "X-Requested-With": "XMLHttpRequest"},
        )
        assert r.status_code == 403, r.text
    finally:
        client.default_token = saved
