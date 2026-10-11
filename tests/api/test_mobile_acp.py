"""Mobile ACP Wallet public API tests."""

import uuid

import app.api.routers.mobile_acp as mobile_acp
from app.services import rate_limit as rl_module


def test_smart_pay_capabilities(client, monkeypatch):
    monkeypatch.setenv("MOBILE_SMART_PAY_ENABLED", "true")
    monkeypatch.setenv("MOBILE_SMART_PAY_AI_FALLBACK_ENABLED", "false")
    monkeypatch.setenv("MOBILE_SMART_PAY_AUTO_SWAP_ENABLED", "false")
    mobile_acp.get_settings.cache_clear()
    try:
        r = client.get("/v1/mobile/smart-pay/capabilities")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["enabled"] is True
        assert data["smartQrParseEnabled"] is True
        assert data["smartQrAiFallbackEnabled"] is False
        assert data["autoSwapEnabled"] is False
        assert data["supportedNetworks"] == ["acp", "bsc"]
        assert any(asset["symbol"] == "ACP" for asset in data["supportedAssets"])
        assert data["minAcpFeeReserve"] == "1.0"
    finally:
        mobile_acp.get_settings.cache_clear()


def test_smart_pay_parse_acp_address_with_amount_and_memo(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    r = client.post(
        "/v1/mobile/smart-pay/parse",
        json={
            "source": "camera",
            "rawPayload": f"{addr}?amount=1.25&memo=coffee",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()["paymentIntent"]
    assert data["network"] == "acp"
    assert data["parseMethod"] == "deterministic"
    assert data["recipient"]["address"] == addr
    assert data["amount"]["value"] == "1.25"
    assert data["amount"]["currencySymbol"] == "ACP"
    assert data["memo"]["value"] == "coffee"
    assert data["metadata"]["detectedStandard"] in ("acp_uri", "acp_address")


def test_smart_pay_parse_eip681_token_transfer(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    r = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    assert r.status_code == 200, r.text
    data = r.json()["paymentIntent"]
    assert data["network"] == "bsc"
    assert data["asset"]["kind"] == "erc20"
    assert data["asset"]["tokenAddress"] == contract
    assert data["recipient"]["address"] == recipient
    assert data["amount"]["atomicValue"] == "25000000"
    assert data["metadata"]["detectedStandard"] == "eip681"


def test_smart_pay_parse_raw_evm_address_needs_review(client):
    address = "0x3333333333333333333333333333333333333333"
    r = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "paste", "rawPayload": address},
    )
    assert r.status_code == 200, r.text
    data = r.json()["paymentIntent"]
    assert data["status"] == "needs_review"
    assert data["network"] == "unknown"
    assert "unknown_network" in data["riskFlags"]
    assert data["recipient"]["address"] == address


def test_smart_pay_parse_unsupported_payload(client):
    r = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": "pay me maybe"},
    )
    assert r.status_code == 400
    assert "Unsupported or malformed QR payload" in r.text


def test_smart_pay_quote_acp_direct_send(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": f"{addr}?amount=2.5"},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    r = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    assert r.status_code == 200, r.text
    quote = r.json()["quote"]
    assert quote["mode"] == "direct_send"
    assert quote["sourceAsset"]["symbol"] == "ACP"
    assert quote["targetAsset"]["symbol"] == "ACP"
    assert quote["paymentIntentId"] == payment_intent_id


def test_smart_pay_quote_bsc_usdt_from_acp(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    r = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    assert r.status_code == 200, r.text
    quote = r.json()["quote"]
    assert quote["mode"] == "swap_then_send"
    assert quote["sourceAsset"]["symbol"] == "ACP"
    assert quote["targetAsset"]["symbol"] == "USDT"
    assert len(quote["route"]) == 3
    assert quote["route"][0]["kind"] == "bridge"
    # Bridge 1 ACP ↔ 10 wACP: indicative lock face = USDT target → 10× wACP out.
    from decimal import Decimal

    bridge_step = quote["route"][0]
    swap_step = quote["route"][1]
    bridged = Decimal(str(bridge_step.get("estimatedOut") or bridge_step.get("estimated_out")))
    usdt_out = Decimal(str(swap_step.get("estimatedOut") or swap_step.get("estimated_out")))
    assert bridged == usdt_out * 10


def test_smart_pay_execute_receipt_and_recover(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": f"{addr}?amount=1"},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 100,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    assert exec_res.status_code == 200, exec_res.text
    exec_payload = exec_res.json()
    execution = exec_payload["execution"]
    session_token = exec_payload["sessionToken"]
    assert session_token
    assert execution["status"] == "awaiting_local_signature"
    assert execution["nextAction"] == "sign_direct_send_tx"
    assert execution["progress"] == {
        "totalRouteSteps": 1,
        "observedTxCount": 0,
        "remainingRouteSteps": 1,
        "pendingRoles": ["payment"],
    }
    assert execution["routePlan"] == [
        {
            "stepIndex": 1,
            "action": "transfer",
            "network": "acp",
            "fromAsset": "ACP",
            "toAsset": "ACP",
            "amount": "1",
            "recipient": addr,
            "status": "ready",
            "signingHint": "Sign transfer transaction locally from wallet",
        }
    ]
    execution_id = execution["id"]

    unauth_status_res = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}",
        headers={"Authorization": ""},
    )
    assert unauth_status_res.status_code == 401
    assert unauth_status_res.json()["detail"] == "Smart Pay execution access required"

    status_res = client.get(f"/v1/mobile/smart-pay/payments/{execution_id}?sessionToken={session_token}", headers={"Authorization": ""})
    assert status_res.status_code == 200
    assert status_res.json()["execution"]["id"] == execution_id
    assert status_res.json()["sessionToken"] == session_token

    receipt_res = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt?sessionToken={session_token}",
        headers={"Authorization": ""},
    )
    assert receipt_res.status_code == 200, receipt_res.text
    receipt = receipt_res.json()
    assert receipt["paymentExecutionId"] == execution_id
    assert receipt["paymentIntentId"] == payment_intent_id
    assert receipt["sourceAssetSpent"] == "ACP"
    assert receipt["targetAssetPaid"] == "ACP"
    assert receipt["targetAmountPaid"] == "1"
    assert receipt["recipientAddress"] == addr
    assert receipt["routeSummary"] == ["1. transfer ACP -> ACP on acp"]
    assert receipt["txRefs"] == []

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={"clientKnownTxs": ["fixture-tx-alpha"]},
        headers={"Authorization": ""},
    )
    assert recover_res.status_code == 200, recover_res.text
    recover_payload = recover_res.json()
    recovered = recover_payload["execution"]
    assert recover_payload["sessionToken"] == session_token
    assert recovered["status"] == "completed"
    assert recovered["recoverable"] is False
    assert recovered["nextAction"] is None
    assert recovered["progress"] == {
        "totalRouteSteps": 1,
        "observedTxCount": 1,
        "remainingRouteSteps": 0,
        "pendingRoles": [],
    }
    assert recovered["txRefs"][0]["role"] == "payment"
    assert recovered["txRefs"][0]["network"] == "acp"
    assert recovered["txRefs"][0]["txid"] == "fixture-tx-alpha"
    assert recovered["txRefs"][0]["explorerUrl"] == "https://ancap.cloud/explorer/tx/fixture-tx-alpha"

    recovered_receipt_res = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt?sessionToken={session_token}",
        headers={"Authorization": ""},
    )
    assert recovered_receipt_res.status_code == 200
    recovered_receipt = recovered_receipt_res.json()
    assert recovered_receipt["txRefs"][0]["txid"] == "fixture-tx-alpha"
    assert recovered_receipt["txRefs"][0]["explorerUrl"] == "https://ancap.cloud/explorer/tx/fixture-tx-alpha"


def test_smart_pay_recover_multi_step_route_stays_pending_until_all_route_txs_are_known(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    execution_id = exec_res.json()["execution"]["id"]

    partial_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={"clientKnownTxs": ["fixture-bridge", "fixture-swap"]},
    )
    assert partial_recover.status_code == 200, partial_recover.text
    partial = partial_recover.json()["execution"]
    assert partial["status"] == "pending_reconciliation"
    assert partial["recoverable"] is True
    assert partial["nextAction"] is None
    assert partial["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 2,
        "remainingRouteSteps": 1,
        "pendingRoles": ["merchant_payout"],
    }
    assert partial["txRefs"][0] == {
        "role": "bridge",
        "network": "acp",
        "txid": "fixture-bridge",
        "explorerUrl": "https://ancap.cloud/explorer/tx/fixture-bridge",
        "routeStepIndex": 1,
    }
    assert partial["txRefs"][1] == {
        "role": "swap",
        "network": "bsc",
        "txid": "fixture-swap",
        "explorerUrl": "https://bscscan.com/tx/fixture-swap",
        "routeStepIndex": 2,
    }

    final_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={"clientKnownTxs": ["fixture-bridge", "fixture-swap", "fixture-payment"]},
    )
    assert final_recover.status_code == 200, final_recover.text
    final = final_recover.json()["execution"]
    assert final["status"] == "completed"
    assert final["recoverable"] is False
    assert final["nextAction"] is None
    assert final["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 3,
        "remainingRouteSteps": 0,
        "pendingRoles": [],
    }
    assert final["txRefs"][2] == {
        "role": "merchant_payout",
        "network": "bsc",
        "txid": "fixture-payment",
        "explorerUrl": "https://bscscan.com/tx/fixture-payment",
        "routeStepIndex": 3,
    }


def test_smart_pay_recover_preserves_explorer_link_metadata_from_structured_client_refs(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    execution_id = exec_res.json()["execution"]["id"]

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={
            "clientKnownTxs": ["fixture-swap-proof"],
            "clientKnownRefs": [
                {
                    "txid": "fixture-bridge-proof",
                    "network": "acp",
                    "role": "bridge",
                    "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
                },
                {
                    "txid": "fixture-merchant-proof",
                    "network": "bsc",
                    "role": "merchant_payout",
                    "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
                },
            ],
        },
    )
    assert recover_res.status_code == 200, recover_res.text
    recovered = recover_res.json()["execution"]
    assert recovered["status"] == "completed"
    assert recovered["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 3,
        "remainingRouteSteps": 0,
        "pendingRoles": [],
    }
    assert recovered["txRefs"] == [
        {
            "role": "bridge",
            "network": "acp",
            "txid": "fixture-bridge-proof",
            "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
            "routeStepIndex": 1,
        },
        {
            "role": "swap",
            "network": "bsc",
            "txid": "fixture-swap-proof",
            "explorerUrl": "https://bscscan.com/tx/fixture-swap-proof",
            "routeStepIndex": 2,
        },
        {
            "role": "merchant_payout",
            "network": "bsc",
            "txid": "fixture-merchant-proof",
            "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
            "routeStepIndex": 3,
        },
    ]


def test_smart_pay_recover_progress_counts_only_route_matched_refs_when_extra_refs_are_present(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    execution_id = exec_res.json()["execution"]["id"]

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={
            "clientKnownRefs": [
                {
                    "txid": "fixture-bridge-proof",
                    "network": "acp",
                    "role": "bridge",
                    "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
                },
                {
                    "txid": "fixture-merchant-proof",
                    "network": "bsc",
                    "role": "merchant_payout",
                    "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
                },
                {
                    "txid": "fixture-refund-proof",
                    "network": "acp",
                    "role": "refund",
                    "explorerUrl": "https://ancap.cloud/acp/tx/fixture-refund-proof",
                },
            ],
        },
    )
    assert recover_res.status_code == 200, recover_res.text
    recovered = recover_res.json()["execution"]
    assert recovered["status"] == "pending_reconciliation"
    assert recovered["recoverable"] is True
    assert recovered["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 2,
        "remainingRouteSteps": 1,
        "pendingRoles": ["swap"],
    }
    assert recovered["txRefs"] == [
        {
            "role": "bridge",
            "network": "acp",
            "txid": "fixture-bridge-proof",
            "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
            "routeStepIndex": 1,
        },
        {
            "role": "merchant_payout",
            "network": "bsc",
            "txid": "fixture-merchant-proof",
            "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
            "routeStepIndex": 3,
        },
        {
            "role": "refund",
            "network": "acp",
            "txid": "fixture-refund-proof",
            "explorerUrl": "https://ancap.cloud/acp/tx/fixture-refund-proof",
            "routeStepIndex": None,
        },
    ]

    receipt_res = client.get(f"/v1/mobile/smart-pay/payments/{execution_id}/receipt")
    assert receipt_res.status_code == 200, receipt_res.text
    assert receipt_res.json()["txRefs"] == recovered["txRefs"]


def test_smart_pay_recover_does_not_remap_mismatched_explicit_route_step_refs(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    execution_id = exec_res.json()["execution"]["id"]

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={
            "clientKnownRefs": [
                {
                    "txid": "fixture-wrong-step",
                    "network": "bsc",
                    "role": "merchant_payout",
                    "explorerUrl": "https://bscscan.com/tx/fixture-wrong-step",
                    "routeStepIndex": 1,
                }
            ],
        },
    )
    assert recover_res.status_code == 200, recover_res.text
    recovered = recover_res.json()["execution"]
    assert recovered["status"] == "pending_reconciliation"
    assert recovered["recoverable"] is True
    assert recovered["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 0,
        "remainingRouteSteps": 3,
        "pendingRoles": ["bridge", "swap", "merchant_payout"],
    }
    assert recovered["txRefs"] == [
        {
            "role": "merchant_payout",
            "network": "bsc",
            "txid": "fixture-wrong-step",
            "explorerUrl": "https://bscscan.com/tx/fixture-wrong-step",
            "routeStepIndex": 1,
        }
    ]

    receipt_res = client.get(f"/v1/mobile/smart-pay/payments/{execution_id}/receipt")
    assert receipt_res.status_code == 200, receipt_res.text
    assert receipt_res.json()["txRefs"] == recovered["txRefs"]


def test_smart_pay_recover_deduplicates_known_txs_case_insensitively(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": f"{addr}?amount=1"},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 100,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    session_token = exec_res.json()["sessionToken"]
    execution_id = exec_res.json()["execution"]["id"]

    first_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={"clientKnownTxs": ["fixture-tx-alpha"]},
        headers={"Authorization": ""},
    )
    assert first_recover.status_code == 200, first_recover.text
    first_execution = first_recover.json()["execution"]
    assert first_execution["txRefs"] == [
        {
            "role": "payment",
            "network": "acp",
            "txid": "fixture-tx-alpha",
            "explorerUrl": "https://ancap.cloud/explorer/tx/fixture-tx-alpha",
            "routeStepIndex": 1,
        }
    ]

    duplicate_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={"clientKnownTxs": ["FIXTURE-TX-ALPHA", "fixture-tx-alpha", " FiXtUrE-Tx-AlPhA "]},
        headers={"Authorization": ""},
    )
    assert duplicate_recover.status_code == 200, duplicate_recover.text
    duplicate_execution = duplicate_recover.json()["execution"]
    assert duplicate_execution["status"] == "completed"
    assert duplicate_execution["progress"] == {
        "totalRouteSteps": 1,
        "observedTxCount": 1,
        "remainingRouteSteps": 0,
        "pendingRoles": [],
    }
    assert duplicate_execution["txRefs"] == [
        {
            "role": "payment",
            "network": "acp",
            "txid": "fixture-tx-alpha",
            "explorerUrl": "https://ancap.cloud/explorer/tx/fixture-tx-alpha",
            "routeStepIndex": 1,
        }
    ]

    receipt_res = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt?sessionToken={session_token}",
        headers={"Authorization": ""},
    )
    assert receipt_res.status_code == 200, receipt_res.text
    assert receipt_res.json()["txRefs"] == [
        {
            "role": "payment",
            "network": "acp",
            "txid": "fixture-tx-alpha",
            "explorerUrl": "https://ancap.cloud/explorer/tx/fixture-tx-alpha",
            "routeStepIndex": 1,
        }
    ]


def test_smart_pay_recover_prefers_structured_refs_over_duplicate_plain_txids(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    session_token = exec_res.json()["sessionToken"]
    execution_id = exec_res.json()["execution"]["id"]

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={
            "clientKnownTxs": ["fixture-bridge-proof", "fixture-merchant-proof"],
            "clientKnownRefs": [
                {
                    "txid": "fixture-bridge-proof",
                    "network": "acp",
                    "role": "bridge",
                    "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
                },
                {
                    "txid": "fixture-merchant-proof",
                    "network": "bsc",
                    "role": "merchant_payout",
                    "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
                },
            ],
        },
        headers={"Authorization": ""},
    )
    assert recover_res.status_code == 200, recover_res.text
    recovered = recover_res.json()["execution"]
    assert recovered["status"] == "pending_reconciliation"
    assert recovered["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 2,
        "remainingRouteSteps": 1,
        "pendingRoles": ["swap"],
    }
    assert recovered["txRefs"] == [
        {
            "role": "bridge",
            "network": "acp",
            "txid": "fixture-bridge-proof",
            "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
            "routeStepIndex": 1,
        },
        {
            "role": "merchant_payout",
            "network": "bsc",
            "txid": "fixture-merchant-proof",
            "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
            "routeStepIndex": 3,
        },
    ]


def test_smart_pay_recover_accepts_explorer_links_inside_client_known_txs(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": f"{addr}?amount=1"},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 100,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    session_token = exec_res.json()["sessionToken"]
    execution_id = exec_res.json()["execution"]["id"]

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={
            "clientKnownTxs": [
                "https://ancap.cloud/acp/transactions/fixture-tx-alpha?source=wallet"
            ]
        },
        headers={"Authorization": ""},
    )
    assert recover_res.status_code == 200, recover_res.text
    recovered = recover_res.json()["execution"]
    assert recovered["status"] == "completed"
    assert recovered["txRefs"] == [
        {
            "role": "payment",
            "network": "acp",
            "txid": "fixture-tx-alpha",
            "explorerUrl": "https://ancap.cloud/acp/transactions/fixture-tx-alpha?source=wallet",
            "routeStepIndex": 1,
        }
    ]


def test_smart_pay_recover_accepts_structured_locator_in_client_known_ref_txid(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    session_token = exec_res.json()["sessionToken"]
    execution_id = exec_res.json()["execution"]["id"]

    recover_res = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={
            "clientKnownRefs": [
                {
                    "txid": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
                    "role": "bridge",
                },
                {
                    "txid": "https://bscscan.com/tx/fixture-merchant-proof",
                    "role": "merchant_payout",
                },
            ]
        },
        headers={"Authorization": ""},
    )
    assert recover_res.status_code == 200, recover_res.text
    recovered = recover_res.json()["execution"]
    assert recovered["status"] == "pending_reconciliation"
    assert recovered["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 2,
        "remainingRouteSteps": 1,
        "pendingRoles": ["swap"],
    }
    assert recovered["txRefs"] == [
        {
            "role": "bridge",
            "network": "acp",
            "txid": "fixture-bridge-proof",
            "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
            "routeStepIndex": 1,
        },
        {
            "role": "merchant_payout",
            "network": "bsc",
            "txid": "fixture-merchant-proof",
            "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
            "routeStepIndex": 3,
        },
    ]


def test_smart_pay_recover_keeps_existing_structured_ref_metadata_when_plain_duplicates_repeat_later(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    session_token = exec_res.json()["sessionToken"]
    execution_id = exec_res.json()["execution"]["id"]

    first_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={
            "clientKnownRefs": [
                {
                    "txid": "fixture-bridge-proof",
                    "network": "acp",
                    "role": "bridge",
                    "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
                }
            ]
        },
        headers={"Authorization": ""},
    )
    assert first_recover.status_code == 200, first_recover.text

    duplicate_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover?sessionToken={session_token}",
        json={"clientKnownTxs": [" FIXTURE-BRIDGE-PROOF ", "fixture-bridge-proof"]},
        headers={"Authorization": ""},
    )
    assert duplicate_recover.status_code == 200, duplicate_recover.text
    duplicate_execution = duplicate_recover.json()["execution"]
    assert duplicate_execution["txRefs"][0] == {
        "role": "bridge",
        "network": "acp",
        "txid": "fixture-bridge-proof",
        "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
        "routeStepIndex": 1,
    }
    assert duplicate_execution["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 1,
        "remainingRouteSteps": 2,
        "pendingRoles": ["swap", "merchant_payout"],
    }

    receipt_res = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt?sessionToken={session_token}",
        headers={"Authorization": ""},
    )
    assert receipt_res.status_code == 200, receipt_res.text
    assert receipt_res.json()["txRefs"][0] == {
        "role": "bridge",
        "network": "acp",
        "txid": "fixture-bridge-proof",
        "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
        "routeStepIndex": 1,
    }


def test_smart_pay_payment_history_lists_latest_executions_with_receipts(client):
    first_addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    second_addr = "acp1qg7l6f5d9s4lm7v3x0j6l3r0f8c0q5t7t2k7d3m4"

    first_parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": f"{first_addr}?amount=1"},
    )
    first_payment_intent_id = first_parsed.json()["paymentIntent"]["id"]
    first_quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": first_payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 100,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    first_quote_id = first_quote_res.json()["quote"]["quoteId"]
    first_exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": first_payment_intent_id,
            "quoteId": first_quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    first_execution_id = first_exec_res.json()["execution"]["id"]
    first_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{first_execution_id}/recover",
        json={"clientKnownTxs": ["fixture-first-hop"]},
    )
    assert first_recover.status_code == 200, first_recover.text

    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    second_payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    second_parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": second_payload},
    )
    second_payment_intent_id = second_parsed.json()["paymentIntent"]["id"]
    second_quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": second_payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    second_quote_id = second_quote_res.json()["quote"]["quoteId"]
    second_exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": second_payment_intent_id,
            "quoteId": second_quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    second_execution_id = second_exec_res.json()["execution"]["id"]

    history_res = client.get("/v1/mobile/smart-pay/payments?limit=1")
    assert history_res.status_code == 200, history_res.text
    limited = history_res.json()["payments"]
    assert len(limited) == 1
    assert limited[0]["execution"]["id"] == second_execution_id
    assert limited[0]["receipt"]["paymentExecutionId"] == second_execution_id
    assert limited[0]["paymentIntent"]["id"] == second_payment_intent_id
    assert limited[0]["quote"]["quoteId"] == second_quote_id

    full_history_res = client.get("/v1/mobile/smart-pay/payments?limit=5")
    assert full_history_res.status_code == 200, full_history_res.text
    payments = full_history_res.json()["payments"]
    assert [item["execution"]["id"] for item in payments[:2]] == [second_execution_id, first_execution_id]

    completed_entry = next(item for item in payments if item["execution"]["id"] == first_execution_id)
    assert completed_entry["execution"]["status"] == "completed"
    assert completed_entry["execution"]["recoverable"] is False
    assert completed_entry["receipt"]["txRefs"][0]["txid"] == "fixture-first-hop"
    assert completed_entry["receipt"]["recipientAddress"] == first_addr

    pending_entry = next(item for item in payments if item["execution"]["id"] == second_execution_id)
    assert pending_entry["execution"]["status"] == "awaiting_local_signature"
    assert pending_entry["receipt"]["paymentExecutionId"] == second_execution_id
    assert pending_entry["paymentIntent"]["recipient"]["address"] == recipient
    assert pending_entry["quote"]["route"][0]["kind"] == "bridge"


def test_smart_pay_payment_history_requires_auth_when_default_client_token_is_removed(client):
    email = f"smart_pay_history_{uuid.uuid4().hex[:12]}@test.com"
    register = client.post(
        "/v1/auth/users",
        json={"email": email, "password": "password123", "display_name": "smart-pay-history-user"},
        headers={"Authorization": ""},
    )
    assert register.status_code in (200, 201), register.text
    login = client.post(
        "/v1/auth/login",
        json={"email": email, "password": "password123"},
        headers={"Authorization": ""},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9?amount=1"},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 100,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
        headers=auth_headers,
    )
    execution_id = exec_res.json()["execution"]["id"]

    mine = client.get("/v1/mobile/smart-pay/payments?limit=5", headers=auth_headers)
    assert mine.status_code == 200, mine.text
    payments = mine.json()["payments"]
    assert any(item["execution"]["id"] == execution_id for item in payments)

    unauth = client.get("/v1/mobile/smart-pay/payments", headers={"Authorization": ""})
    assert unauth.status_code == 401, unauth.text
    assert unauth.json()["detail"] == "Not authenticated"


def test_smart_pay_owner_auth_can_refresh_receipt_and_recover_without_original_session_token(client):
    owner_email = f"smart_pay_owner_{uuid.uuid4().hex[:12]}@test.com"
    owner_register = client.post(
        "/v1/auth/users",
        json={"email": owner_email, "password": "password123", "display_name": "smart-pay-owner"},
        headers={"Authorization": ""},
    )
    assert owner_register.status_code in (200, 201), owner_register.text
    owner_login = client.post(
        "/v1/auth/login",
        json={"email": owner_email, "password": "password123"},
        headers={"Authorization": ""},
    )
    assert owner_login.status_code == 200, owner_login.text
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}

    other_email = f"smart_pay_other_{uuid.uuid4().hex[:12]}@test.com"
    other_register = client.post(
        "/v1/auth/users",
        json={"email": other_email, "password": "password123", "display_name": "smart-pay-other"},
        headers={"Authorization": ""},
    )
    assert other_register.status_code in (200, 201), other_register.text
    other_login = client.post(
        "/v1/auth/login",
        json={"email": other_email, "password": "password123"},
        headers={"Authorization": ""},
    )
    assert other_login.status_code == 200, other_login.text
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
        headers=owner_headers,
    )
    assert exec_res.status_code == 200, exec_res.text
    execution_id = exec_res.json()["execution"]["id"]
    session_token = exec_res.json()["sessionToken"]
    assert session_token

    owner_status = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}",
        headers=owner_headers,
    )
    assert owner_status.status_code == 200, owner_status.text
    owner_status_payload = owner_status.json()
    assert owner_status_payload["execution"]["id"] == execution_id
    assert owner_status_payload["sessionToken"] == session_token

    owner_receipt = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt",
        headers=owner_headers,
    )
    assert owner_receipt.status_code == 200, owner_receipt.text
    assert owner_receipt.json()["paymentExecutionId"] == execution_id

    owner_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={
            "clientKnownRefs": [
                {
                    "txid": "fixture-bridge-proof",
                    "network": "acp",
                    "role": "bridge",
                    "explorerUrl": "https://ancap.cloud/acp/tx/fixture-bridge-proof",
                },
                {
                    "txid": "fixture-merchant-proof",
                    "network": "bsc",
                    "role": "merchant_payout",
                    "explorerUrl": "https://bscscan.com/tx/fixture-merchant-proof",
                },
            ],
            "clientKnownTxs": ["fixture-swap-proof"],
        },
        headers=owner_headers,
    )
    assert owner_recover.status_code == 200, owner_recover.text
    owner_recover_payload = owner_recover.json()
    assert owner_recover_payload["sessionToken"] == session_token
    assert owner_recover_payload["execution"]["status"] == "completed"
    assert owner_recover_payload["execution"]["progress"] == {
        "totalRouteSteps": 3,
        "observedTxCount": 3,
        "remainingRouteSteps": 0,
        "pendingRoles": [],
    }

    owner_receipt_after_recover = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt",
        headers=owner_headers,
    )
    assert owner_receipt_after_recover.status_code == 200, owner_receipt_after_recover.text
    assert owner_receipt_after_recover.json()["txRefs"] == owner_recover_payload["execution"]["txRefs"]

    other_status = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}",
        headers=other_headers,
    )
    assert other_status.status_code == 401, other_status.text
    assert other_status.json()["detail"] == "Smart Pay execution access required"

    other_receipt = client.get(
        f"/v1/mobile/smart-pay/payments/{execution_id}/receipt",
        headers=other_headers,
    )
    assert other_receipt.status_code == 401, other_receipt.text
    assert other_receipt.json()["detail"] == "Smart Pay execution access required"

    other_recover = client.post(
        f"/v1/mobile/smart-pay/payments/{execution_id}/recover",
        json={"clientKnownTxs": ["fixture-intruder"]},
        headers=other_headers,
    )
    assert other_recover.status_code == 401, other_recover.text
    assert other_recover.json()["detail"] == "Smart Pay execution access required"


def test_smart_pay_receipt_404_for_unknown_execution(client):
    r = client.get("/v1/mobile/smart-pay/payments/pe_missing/receipt")
    assert r.status_code == 404


def test_smart_pay_quote_rejects_low_acp_fee_reserve(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "camera", "rawPayload": f"{addr}?amount=1"},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    r = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP"],
                "maxSlippageBps": 100,
                "minAcpFeeReserve": "0.1",
            },
        },
    )
    assert r.status_code == 409


def test_mobile_config_ok(client):
    r = client.get("/v1/mobile/config")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["minAppVersion"] == "1.0.0"
    assert data["acpDecimals"] == 8
    assert data["wacpDecimals"] == 18
    assert "docs" in data
    assert data["docs"]["bridge"] == "https://ancap.cloud/docs/wacp/bridge"
    assert data["docs"]["risks"] == "https://ancap.cloud/docs/wacp/risks"
    assert data["docs"]["reserve"] == "https://ancap.cloud/docs/wacp/reserve"
    assert data["docs"]["contracts"] == "https://ancap.cloud/docs/wacp/contracts"
    assert data["docs"]["walletSecurity"] == "https://ancap.cloud/docs/mobile/security"


def test_mobile_health(client):
    r = client.get("/v1/mobile/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_acp_network_status(client, monkeypatch):
    monkeypatch.setattr(mobile_acp.wallet_acp, "_rpc_call", lambda *a, **k: 42)
    r = client.get("/v1/acp/network/status")
    assert r.status_code == 200
    data = r.json()
    assert data["rpcStatus"] == "ok"
    assert data["blockHeight"] == 42
    assert data["minFeeAcp"]


def test_acp_address_balance(client, monkeypatch):
    monkeypatch.setattr(
        mobile_acp.wallet_acp,
        "_load_balance_result",
        lambda addr: {"address": addr, "units": "100000000", "acp": "1", "utxo_count": 1},
    )
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    r = client.get(f"/v1/acp/address/{addr}/balance")
    assert r.status_code == 200
    data = r.json()
    assert data["address"] == addr
    assert data["acp"] == "1"
    assert data["utxo_count"] == 1


def test_acp_address_balance_invalid(client):
    r = client.get("/v1/acp/address/not-an-address/balance")
    assert r.status_code == 400


def test_acp_estimate_fee(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    r = client.post(
        "/v1/acp/tx/estimate-fee",
        json={"from": addr, "to": addr, "amountAcp": "1"},
    )
    assert r.status_code == 200
    assert r.json()["feeAcp"]


def test_acp_broadcast_requires_auth_or_device(client, monkeypatch):
    """Broadcast is not an open relay: anonymous callers without a registered device get 401."""
    monkeypatch.setattr(mobile_acp.wallet_acp, "_require_acp_rpc_url", lambda: "http://rpc.test")
    r = client.post(
        "/v1/acp/tx/broadcast",
        json={"rawTx": "deadbeef" * 8},
        headers={"Authorization": ""},
    )
    assert r.status_code == 401


def test_acp_broadcast_unknown_device_token_rejected(client, monkeypatch):
    monkeypatch.setattr(mobile_acp.wallet_acp, "_require_acp_rpc_url", lambda: "http://rpc.test")
    r = client.post(
        "/v1/acp/tx/broadcast",
        json={"rawTx": "deadbeef" * 8},
        headers={"Authorization": "", "X-Device-Token": "not-a-registered-device"},
    )
    assert r.status_code == 401


def test_acp_broadcast_invalid_hex(client, monkeypatch):
    monkeypatch.setattr(mobile_acp.wallet_acp, "_require_acp_rpc_url", lambda: "http://rpc.test")
    r = client.post("/v1/acp/tx/broadcast", json={"rawTx": "gg" * 20})
    assert r.status_code == 400


def test_acp_broadcast_ok(client, monkeypatch):
    monkeypatch.setattr(mobile_acp.wallet_acp, "_require_acp_rpc_url", lambda: "http://rpc.test")
    monkeypatch.setattr(
        mobile_acp.wallet_acp,
        "_rpc_call",
        lambda *a, **k: {"accepted": True, "txid": "abc123"},
    )
    r = client.post("/v1/acp/tx/broadcast", json={"rawTx": "deadbeef" * 8})
    assert r.status_code == 200
    data = r.json()
    assert data["accepted"] is True
    assert data["txid"] == "abc123"


def test_acp_broadcast_rate_limited(client, monkeypatch):
    """Exhaust the per-IP broadcast limit; subsequent requests return 429.

    rate_limit.py is configured to use its in-memory fallback when REDIS_URL
    is empty (the default). The per-IP key is built from the test client's IP.
    """
    monkeypatch.setattr(mobile_acp.wallet_acp, "_require_acp_rpc_url", lambda: "http://rpc.test")
    monkeypatch.setattr(
        mobile_acp.wallet_acp,
        "_rpc_call",
        lambda *a, **k: {"accepted": True, "txid": "abc123"},
    )

    # Ensure clean in-memory state before the test
    rl_module.clear_rate_limit_state()

    # Limit = mobile_broadcast_rate_limit_per_minute = 10 per minute
    limit = 10
    for i in range(limit):
        r = client.post("/v1/acp/tx/broadcast", json={"rawTx": "deadbeef" * 8})
        assert r.status_code == 200, f"request {i+1} should succeed, got {r.status_code}: {r.text}"

    # Next one must be rate-limited
    r = client.post("/v1/acp/tx/broadcast", json={"rawTx": "deadbeef" * 8})
    assert r.status_code == 429, r.text
    assert r.json()["detail"]["code"] == "RATE_LIMITED"
    assert "retry_after_seconds" in r.json()["detail"]


def test_smart_pay_parse_ocr_invoice_text(client):
    addr = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9"
    raw = f"Invoice #A-100\nPay to: {addr}\nTotal due: 3.25 ACP"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "ocr", "rawPayload": raw},
    )
    assert parsed.status_code == 200, parsed.text
    intent = parsed.json()["paymentIntent"]
    assert intent["recipient"]["address"] == addr
    assert intent["amount"]["value"] == "3.25"
    assert intent["parseMethod"] == "heuristic"


def test_smart_pay_execute_includes_multi_step_route_plan(client):
    contract = "0x1111111111111111111111111111111111111111"
    recipient = "0x2222222222222222222222222222222222222222"
    payload = f"ethereum:{contract}@56/transfer?address={recipient}&uint256=25000000"
    parsed = client.post(
        "/v1/mobile/smart-pay/parse",
        json={"source": "photo", "rawPayload": payload},
    )
    payment_intent_id = parsed.json()["paymentIntent"]["id"]
    quote_res = client.post(
        "/v1/mobile/smart-pay/quote",
        json={
            "paymentIntentId": payment_intent_id,
            "sourcePreference": {
                "preferredAsset": "ACP",
                "allowedAssets": ["ACP", "wACP", "USDT"],
                "maxSlippageBps": 150,
                "minAcpFeeReserve": "1.0",
            },
        },
    )
    assert quote_res.status_code == 200, quote_res.text
    quote_id = quote_res.json()["quote"]["quoteId"]
    exec_res = client.post(
        "/v1/mobile/smart-pay/execute",
        json={
            "paymentIntentId": payment_intent_id,
            "quoteId": quote_id,
            "confirmationAccepted": True,
            "deviceContext": {"platform": "android", "appVersion": "1.1.0"},
        },
    )
    assert exec_res.status_code == 200, exec_res.text
    route_plan = exec_res.json()["execution"]["routePlan"]
    assert len(route_plan) == 3
    assert route_plan[0]["action"] == "bridge"
    assert route_plan[-1]["action"] == "transfer"
    assert route_plan[-1]["recipient"] == recipient

