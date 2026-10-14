"""End-to-end paid workflow path on the test client (ledger credits — no Stripe, no broadcast).

Path: register → select workflow → credits payment → execute → result → receipt → platform fee proof.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4


def _register(client):
    email = f"investor_smoke_{uuid4().hex[:12]}@test.com"
    res = client.post(
        "/v1/auth/users",
        json={"email": email, "password": "password123", "display_name": "investor smoke"},
        headers={"Authorization": ""},
    )
    assert res.status_code in (200, 201), res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user = client.get("/v1/users/me", headers=headers).json()
    return user, headers


def _deposit(client, user_id: str, headers: dict[str, str], amount: str = "50") -> None:
    response = client.post(
        "/v1/ledger/deposit",
        json={
            "account_owner_type": "user",
            "account_owner_id": user_id,
            "amount": {"amount": amount, "currency": "ACP"},
            "reference": "investor-paid-path-smoke",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text


def test_investor_paid_path_register_pay_execute_receipt_fee(client):
    user, headers = _register(client)
    _deposit(client, user["id"], headers, amount="50")

    catalog = client.get("/v1/workflow-store/templates", headers=headers)
    assert catalog.status_code == 200, catalog.text
    payload = catalog.json()
    items = payload["items"] if isinstance(payload, dict) and "items" in payload else payload
    slugs = {item["slug"] for item in items}
    assert "token-risk-report" in slugs

    run = client.post(
        "/v1/workflow-store/runs",
        json={
            "workflow_slug": "token-risk-report",
            "payment_currency": "ACP",
            "unlock_full_result": True,
            "inputs": {
                "project_name": "Investor Smoke Token",
                "token_symbol": "ISM",
                "chain": "Base",
            },
        },
        headers=headers,
    )
    assert run.status_code == 201, run.text
    run_payload = run.json()
    run_id = run_payload["id"]
    assert Decimal(run_payload["price"]["amount"]) > 0

    reserve = client.post(
        f"/v1/workflow-store/runs/{run_id}/payment-intents",
        json={"payment_method": "credits", "note": "investor paid-path smoke"},
        headers=headers,
    )
    assert reserve.status_code == 201, reserve.text
    assert reserve.json()["run"]["status"] == "paid"

    execute = client.post(f"/v1/workflow-store/runs/{run_id}/execute", headers=headers)
    assert execute.status_code == 200, execute.text
    executed = execute.json()["item"]
    assert executed["status"] == "completed"

    receipt = executed["receipt"]
    proof = receipt["proof"]
    assert proof["payment_intent_status"] == "captured"
    assert proof.get("payment_intent_id")
    assert executed.get("result"), "paid run must return a result artifact"
    assert proof.get("llm_usage") or executed["result"].get("llm_usage")

    # Platform fee / margin is the investor-visible earnings proof on the receipt.
    fee = proof.get("platform_fee") or proof.get("margin_snapshot")
    assert fee is not None, "receipt must expose platform fee or margin snapshot"
    if isinstance(fee, dict) and fee.get("amount") is not None:
        assert Decimal(str(fee["amount"])) >= 0

    fetched = client.get(f"/v1/workflow-store/runs/{run_id}", headers=headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["id"] == run_id
    assert fetched.json()["receipt"]["proof"]["payment_intent_status"] == "captured"


def test_portfolio_offer_slugs_exist_in_workflow_catalog():
    """Slugs referenced by frontend projectOffers must exist as templates or bundles."""
    from app.services.workflow_execution import WORKFLOW_BUNDLES, WORKFLOW_TEMPLATES
    from pathlib import Path
    import re

    offers_path = Path(__file__).resolve().parents[2] / "frontend-app" / "src" / "lib" / "projectOffers.ts"
    text = offers_path.read_text(encoding="utf-8")
    referenced: set[str] = set()
    for block in re.findall(r"workflowSlugs:\s*\[(.*?)\]", text, flags=re.S):
        referenced.update(re.findall(r'"([a-z0-9-]+)"', block))
    catalog = {item.slug for item in WORKFLOW_TEMPLATES} | {item.slug for item in WORKFLOW_BUNDLES}
    missing = sorted(referenced - catalog)
    assert missing == [], f"projectOffers references unknown workflow slugs: {missing}"
