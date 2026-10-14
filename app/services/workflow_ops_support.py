"""Workflow context validation, credential encryption, quality and delivery."""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import re
import html
import ipaddress
import logging
from datetime import UTC, datetime

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException
from app.services.crypto_secrets import resolve_secret_material
from app.services.webhook_url_policy import validate_webhook_url_async, UnsafeWebhookUrl


class _CredentialLogFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        if "api.telegram.org/bot" in message:
            record.msg = re.sub(r"api\.telegram\.org/bot[^/\s]+", "api.telegram.org/bot[redacted]", message)
            record.args = ()
        return True


logging.getLogger("httpx").addFilter(_CredentialLogFilter())


def now():
    return datetime.now(UTC)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def bounded_json(value, limit=200000):
    try:
        raw = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError):
        raise HTTPException(422, "Invalid JSON") from None
    if len(raw.encode()) > limit:
        raise HTTPException(422, "Payload exceeds workflow limits")
    return value


def secret_key():
    material = resolve_secret_material(dedicated=None, secret_key_suffix=b"|workflow-ops-v1", development_fallback=b"development-workflow-ops-only", purpose="Workflow connector encryption")
    return hashlib.sha256(material).digest()


def seal(secret, owner):
    nonce = os.urandom(12)
    return base64.urlsafe_b64encode(nonce + AESGCM(secret_key()).encrypt(nonce, secret.encode(), str(owner).encode())).decode()


def unseal(box, owner):
    data = base64.urlsafe_b64decode(box)
    return AESGCM(secret_key()).decrypt(data[:12], data[12:], str(owner).encode()).decode()


async def validate_connection(body):
    allowed = {"webhook": {"url"}, "telegram": {"chat_id"}, "google_sheets": {"spreadsheet_id", "range"}, "hubspot": set(), "anthropic": {"model"}}
    if set(body.config) - allowed[body.kind]:
        raise HTTPException(422, "Unsupported connector settings")
    if body.kind == "webhook":
        if len(body.secret.strip()) < 16:
            raise HTTPException(422, "Webhook signing secret requires at least 16 characters")
        if not body.config.get("url", "").startswith("https://"):
            raise HTTPException(422, "Webhook requires public HTTPS")
        try:
            await validate_webhook_url_async(body.config["url"])
        except UnsafeWebhookUrl:
            raise HTTPException(422, "Unsafe webhook destination") from None
    elif not body.secret.strip():
        raise HTTPException(422, "Connector credential is required")
    if body.kind == "telegram" and not re.fullmatch(r"-?\d{1,20}", body.config.get("chat_id", "")):
        raise HTTPException(422, "Numeric Telegram chat ID required")
    if body.kind == "telegram" and not re.fullmatch(r"\d{5,20}:[A-Za-z0-9_-]{20,100}", body.secret):
        raise HTTPException(422, "Invalid Telegram bot credential")
    if body.kind == "google_sheets":
        if not re.fullmatch(r"[a-zA-Z0-9_-]{15,150}", body.config.get("spreadsheet_id", "")):
            raise HTTPException(422, "Invalid spreadsheet ID")
        if not re.fullmatch(r"[a-zA-Z0-9_!:' -]{1,100}", body.config.get("range", "Sheet1!A:D")):
            raise HTTPException(422, "Invalid sheet range")
    if body.kind == "anthropic" and not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", body.config.get("model", "claude-sonnet-4-6")):
        raise HTTPException(422, "Invalid model")


async def post_public(url, *, content=None, payload=None, headers=None):
    # Resolve and pin every outgoing destination; never follow redirects.
    target = await validate_webhook_url_async(url)
    if not target.pinned_ip or not ipaddress.ip_address(target.pinned_ip).is_global:
        raise HTTPException(422, "Connector requires a public network destination")
    request_headers = {**(headers or {}), "Host": target.hostname}
    async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False) as client:
        response = await client.post(target.pinned_request_url(), json=payload, content=content, headers=request_headers, extensions={"sni_hostname": target.hostname})
        if response.status_code >= 300:
            raise HTTPException(502, "Connector rejected the delivery")
        return response


def spreadsheet_cell(value):
    text = str(value)
    return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r")) else text


async def deliver(connection, run, output):
    from urllib.parse import quote
    secret = unseal(connection.secret_box, connection.owner_user_id)
    config = connection.config_json
    payload = {"operation_id": str(run.id), "event": "workflow.reviewed", "output": output}
    text = json.dumps(output, ensure_ascii=False, default=str)[:3000]
    headers = {"Idempotency-Key": str(run.id), "Content-Type": "application/json"}
    if connection.kind == "webhook":
        raw = json.dumps(payload, ensure_ascii=False, default=str).encode()
        headers["X-ANCAP-Signature"] = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
        response = await post_public(config["url"], content=raw, headers=headers)
    elif connection.kind == "telegram":
        response = await post_public(f"https://api.telegram.org/bot{secret}/sendMessage", payload={"chat_id": config["chat_id"], "text": f"ANCAP report {run.id}\n{text}"})
        if response.json().get("ok") is not True:
            raise HTTPException(502, "Telegram delivery was not accepted")
    elif connection.kind == "google_sheets":
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{config['spreadsheet_id']}/values/{quote(config.get('range','Sheet1!A:D'),safe='')}:append?valueInputOption=RAW"
        response = await post_public(url, payload={"values": [[str(run.id), now().isoformat(), spreadsheet_cell(text)]]}, headers={"Authorization": f"Bearer {secret}"})
    elif connection.kind == "hubspot":
        response = await post_public("https://api.hubapi.com/crm/v3/objects/notes", payload={"properties": {"hs_timestamp": now().isoformat(), "hs_note_body": html.escape(f"ANCAP report {run.id}\n{text}")}}, headers={"Authorization": f"Bearer {secret}"})
    else:
        raise HTTPException(422, "Model connections cannot receive deliveries")
    return {"connection_id": str(connection.id), "state": "delivered", "http_status": response.status_code, "at": now().isoformat()}


def quality_passport(result, usage, sources, definition):
    text = json.dumps(result, ensure_ascii=False, default=str).lower()
    checks = [{"name": "structured_output", "passed": isinstance(result, dict) and bool(result.get("deliverable"))}, {"name": "model_execution", "passed": not bool(usage.get("fallback_used", True))}]
    for case in definition.get("test_cases", []):
        checks.append({"name": case["name"], "passed": all(value.lower() in text for value in case.get("required_text", []))})
    return {"scope": "structure_and_declared_tests_not_fact_verification", "checked_at": now().isoformat(), "output_hash": digest(result), "definition_hash": digest(definition), "sources": sources, "checks": checks, "passed": all(c["passed"] for c in checks), "model": usage.get("model"), "provider": usage.get("provider"), "fallback_used": usage.get("fallback_used", True)}


async def market_snapshot(coin_ids):
    if not coin_ids:
        return {}, []
    if any(not re.fullmatch(r"[a-z0-9-]{1,80}", coin) for coin in coin_ids):
        raise HTTPException(422, "Invalid coin ID")
    async with httpx.AsyncClient(timeout=10, follow_redirects=False, trust_env=False) as client:
        response = await client.get("https://api.coingecko.com/api/v3/simple/price", params={"ids": ",".join(coin_ids), "vs_currencies": "usd", "include_24hr_change": "true", "include_last_updated_at": "true"})
        response.raise_for_status()
        payload = response.json()
    if not isinstance(payload, dict) or any(coin not in payload for coin in coin_ids):
        raise HTTPException(502, "Market data missing; report not generated")
    return payload, [{"url": "https://api.coingecko.com/api/v3/simple/price", "retrieved_at": now().isoformat(), "coin_ids": coin_ids, "kind": "market_data"}]
