from decimal import Decimal
from uuid import UUID

from tests.conftest import unique_name
from tests.conftest import unique_email


def _create_agent(client, role: str) -> str:
  r = client.post(
    "/v1/agents",
    json={"display_name": unique_name(f"contract_{role}"), "public_key": "x" * 32, "roles": [role]},
  )
  assert r.status_code == 201, r.text
  return r.json()["id"]


def _fund_agent(client, agent_id: str, amount: str = "100", currency: str = "VUSD", token: str | None = None) -> None:
  headers = {"Idempotency-Key": unique_name("idk_contract_deposit")}
  if token:
    headers["Authorization"] = f"Bearer {token}"
  r = client.post(
    "/v1/ledger/deposit",
    json={
      "account_owner_type": "agent",
      "account_owner_id": agent_id,
      "amount": {"amount": amount, "currency": currency},
    },
    headers=headers,
  )
  assert r.status_code == 201, r.text


def _get_balance(client, agent_id: str, currency: str = "VUSD", token: str | None = None) -> Decimal:
  headers = {"Authorization": f"Bearer {token}"} if token else None
  r = client.get(
    "/v1/ledger/balance",
    params={"owner_type": "agent", "owner_id": agent_id},
    headers=headers,
  )
  assert r.status_code == 200, r.text
  payload = r.json()
  for item in payload.get("balances") or []:
    if item.get("currency") == currency:
      try:
        return Decimal(str(item.get("amount") or "0"))
      except Exception:
        return Decimal("0")
  return Decimal("0")


def _register_and_login(client) -> str:
  email = unique_email()
  password = "password123"
  reg = client.post("/v1/auth/users", json={"email": email, "password": password, "display_name": "Contracts Lifecycle"})
  assert reg.status_code in (201, 400), reg.text
  login = client.post("/v1/auth/login", json={"email": email, "password": password})
  assert login.status_code == 200, login.text
  return login.json()["access_token"]


def _create_agent_authed(client, token: str, role: str) -> str:
  r = client.post(
    "/v1/agents",
    headers={"Authorization": f"Bearer {token}"},
    json={"display_name": unique_name(f"contract_{role}"), "public_key": "x" * 32, "roles": [role]},
  )
  assert r.status_code == 201, r.text
  return r.json()["id"]


def test_fixed_contract_lifecycle_and_payout(client, base_vertical_id):
  employer = _create_agent(client, "seller")
  worker = _create_agent(client, "buyer")
  _fund_agent(client, employer, amount="50")
  before_employer = _get_balance(client, employer)
  before_worker = _get_balance(client, worker)

  body = {
    "employer_agent_id": employer,
    "worker_agent_id": worker,
    "scope_type": "generic",
    "scope_ref_id": None,
    "title": "Fixed job",
    "description": "Do X once",
    "payment_model": "fixed",
    "fixed_amount_value": "25",
    "currency": "VUSD",
    "max_runs": 1,
    "risk_policy_id": None,
    "created_from_order_id": None,
  }
  c = client.post("/v1/contracts", json=body)
  assert c.status_code == 201, c.text
  cjson = c.json()
  cid = cjson["id"]

  # propose (if needed) -> accept -> complete triggers payout
  if cjson.get("status") == "draft":
    p = client.post(f"/v1/contracts/{cid}/propose")
    assert p.status_code == 200, p.text
    assert p.json()["status"] == "proposed"

  a = client.post(f"/v1/contracts/{cid}/accept")
  assert a.status_code == 200, a.text
  assert a.json()["status"] == "active"

  # accept -> escrow (worker should not be paid yet)
  after_employer_accept = _get_balance(client, employer)
  after_worker_accept = _get_balance(client, worker)
  assert after_worker_accept == before_worker
  assert after_employer_accept <= before_employer - Decimal("25")

  pay = client.get(f"/v1/contracts/{cid}/payments")
  assert pay.status_code == 200, pay.text
  assert Decimal(pay.json()["escrowed_total"]) >= Decimal("25")
  assert Decimal(pay.json()["paid_total"]) == Decimal("0")
  assert Decimal(pay.json()["pending_total"]) >= Decimal("25")

  comp = client.post(f"/v1/contracts/{cid}/complete")
  assert comp.status_code == 200, comp.text
  assert comp.json()["status"] == "completed"

  after_worker = _get_balance(client, worker)
  assert after_worker >= before_worker + Decimal("25")

  pay2 = client.get(f"/v1/contracts/{cid}/payments")
  assert pay2.status_code == 200, pay2.text
  assert Decimal(pay2.json()["paid_total"]) >= Decimal("25")
  assert Decimal(pay2.json()["pending_total"]) == Decimal("0")

  # idempotent-ish: second complete does not pay again
  again = client.post(f"/v1/contracts/{cid}/complete")
  assert again.status_code in (200, 400), again.text
  after_again = _get_balance(client, worker)
  assert after_again == after_worker


def test_fixed_contract_cancel_refunds_remaining_escrow(client, base_vertical_id):
  employer = _create_agent(client, "seller")
  worker = _create_agent(client, "buyer")
  _fund_agent(client, employer, amount="50")
  before_employer = _get_balance(client, employer)

  body = {
    "employer_agent_id": employer,
    "worker_agent_id": worker,
    "scope_type": "generic",
    "scope_ref_id": None,
    "title": "Fixed job cancel",
    "description": "Cancel before complete",
    "payment_model": "fixed",
    "fixed_amount_value": "25",
    "currency": "VUSD",
    "max_runs": 1,
    "risk_policy_id": None,
    "created_from_order_id": None,
  }
  c = client.post("/v1/contracts", json=body)
  assert c.status_code == 201, c.text
  cjson = c.json()
  cid = cjson["id"]

  if cjson.get("status") == "draft":
    client.post(f"/v1/contracts/{cid}/propose")
  client.post(f"/v1/contracts/{cid}/accept")

  cancelled = client.post(f"/v1/contracts/{cid}/cancel")
  assert cancelled.status_code == 200, cancelled.text
  assert cancelled.json()["status"] == "cancelled"

  after_employer = _get_balance(client, employer)
  assert after_employer >= before_employer

  pay = client.get(f"/v1/contracts/{cid}/payments")
  assert pay.status_code == 200, pay.text
  assert Decimal(pay.json()["pending_total"]) == Decimal("0")


def test_per_run_contract_payout_uses_succeeded_runs(client, base_vertical_id):
  token = _register_and_login(client)
  # Worker must be owned by the authenticated user for /v1/runs worker enforcement.
  worker = _create_agent_authed(client, token, "buyer")
  employer = _create_agent(client, "seller")
  _fund_agent(client, employer, amount="100")

  body = {
    "employer_agent_id": employer,
    "worker_agent_id": worker,
    "scope_type": "strategy_version",
    "scope_ref_id": None,
    "title": "Per-run job",
    "description": "Run strategy multiple times",
    "payment_model": "per_run",
    "fixed_amount_value": "10",
    "currency": "VUSD",
    "max_runs": 3,
    "risk_policy_id": None,
    "created_from_order_id": None,
  }
  c = client.post("/v1/contracts", json=body)
  assert c.status_code == 201, c.text
  cid = c.json()["id"]

  # Make contract active
  client.post(f"/v1/contracts/{cid}/propose")
  a = client.post(f"/v1/contracts/{cid}/accept", headers={"Authorization": f"Bearer {token}"})
  assert a.status_code == 200, a.text
  assert a.json()["status"] == "active"

  # Prepare strategy + pool
  strat = client.post(
    "/v1/strategies",
    json={
      "name": unique_name("contract_strategy"),
      "vertical_id": base_vertical_id,
      "owner_agent_id": worker,
    },
  )
  assert strat.status_code == 201, strat.text
  sid = strat.json()["id"]
  workflow = {
    "vertical_id": base_vertical_id,
    "version": "1.0",
    "steps": [
      {"id": "s1", "action": "const", "args": {"value": 1}, "save_as": "x"},
    ],
  }
  ver = client.post(f"/v1/strategies/{sid}/versions", json={"semver": "1.0.0", "workflow": workflow})
  assert ver.status_code == 201, ver.text
  vid = ver.json()["id"]

  pool = client.post(
    "/v1/pools",
    json={"name": unique_name("contract_pool"), "risk_profile": "experimental"},
  )
  assert pool.status_code == 201, pool.text
  pool_id = pool.json()["id"]

  # worker was created with the freshly-registered user's token, so balance
  # checks must use the same token (the auto-attached default user does not
  # own this agent).
  balance_before_runs = _get_balance(client, worker, token=token)

  # Create two successful runs under this contract
  for _ in range(2):
    r = client.post(
      "/v1/runs",
      headers={"Idempotency-Key": unique_name("idk_contract_run"), "Authorization": f"Bearer {token}"},
      json={
        "strategy_version_id": vid,
        "pool_id": pool_id,
        "params": {},
        "limits": {},
        "dry_run": True,
        "run_mode": "mock",
        "contract_id": cid,
      },
    )
    assert r.status_code == 201, r.text

  after_runs = _get_balance(client, worker, token=token)
  # per_run: payout is executed per succeeded run
  assert after_runs >= balance_before_runs + Decimal("20")

  comp = client.post(f"/v1/contracts/{cid}/complete")
  assert comp.status_code == 200, comp.text
  assert comp.json()["status"] == "completed"
  after_complete = _get_balance(client, worker, token=token)
  # complete should not create additional payouts for per_run model
  assert after_complete == after_runs

