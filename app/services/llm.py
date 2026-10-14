from __future__ import annotations

import hashlib
from contextvars import ContextVar
import json
import time
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import LlmUsageEvent
from app.schemas import WorkflowTemplatePublic
from app.services.workflow_execution import execute_workflow_template

# Credentials and limits are request-local; shared Settings are never overwritten.
workflow_provider_credentials: ContextVar[dict | None] = ContextVar("workflow_provider_credentials", default=None)


# Sensitive medical / adult-hospitality SKUs: always use vetted template deliverables
# (never raw LLM JSON alone) so compliance blocks cannot be dropped.
_COMPLIANCE_LOCKED_SLUGS = frozenset(
    {
        "aeterna-substance-coding",
        "aeterna-adhd-support",
        "aeterna-aurea-vita",
        "aeterna-down-syndrome-support",
        "entertainment-tesla-coil-party",
        "antique-fire-restore",
    }
)


# Retryable status codes: transient failures we should retry
_RETRYABLE_STATUS_CODES = {429, 502, 503, 504}


def _classify_failure(exc: Exception) -> str:
    """Classify LLM failure into: unavailable | invalid_model | auth_error | balance_error | timeout | unknown."""
    msg = str(exc).lower()
    code = getattr(exc, "response", None)
    if isinstance(code, httpx.Response):
        status = code.status_code
        if status in (401, 403):
            return "auth_error"
        if status == 402:
            return "balance_error"
        if status == 404:
            return "invalid_model"
        if status in (429, 502, 503, 504):
            return "unavailable"
        if status >= 500:
            return "unavailable"
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    if any(k in msg for k in ("unavailable", "503", "connection")):
        return "unavailable"
    if any(k in msg for k in ("401", "403", "forbidden", "unauthorized")):
        return "auth_error"
    if any(k in msg for k in ("balance", "insufficient")):
        return "balance_error"
    if any(k in msg for k in ("model", "not found")):
        return "invalid_model"
    return "unknown"


def _is_retryable(exc: Exception) -> bool:
    code = getattr(exc, "response", None)
    if isinstance(code, httpx.Response):
        return code.status_code in _RETRYABLE_STATUS_CODES
    msg = str(exc).lower()
    return any(k in msg for k in ("timeout", "unavailable", "503", "connection"))


class LlmExecutionResult:
    __slots__ = ("result", "usage_event_id", "provider", "model", "status",
                 "fallback_used", "provider_status", "failure_reason", "retry_count")

    def __init__(
        self,
        result: dict[str, Any],
        usage_event_id: str | None,
        provider: str,
        model: str,
        status: str,
        fallback_used: bool,
        provider_status: str = "unknown",
        failure_reason: str | None = None,
        retry_count: int = 0,
    ):
        self.result = result
        self.usage_event_id = usage_event_id
        self.provider = provider
        self.model = model
        self.status = status
        self.fallback_used = fallback_used
        self.provider_status = provider_status
        self.failure_reason = failure_reason
        self.retry_count = retry_count


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / 4))


def _extract_anthropic_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in payload.get("content") or []:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text") or ""))
    return "\n".join(part for part in parts if part).strip()


def _parse_model_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {
        "status": "completed",
        "deliverable": {
            "summary": stripped[:4000],
            "raw_text": stripped,
        },
        "execution_summary": {
            "mode": "llm_text",
            "artifact_kind": "model_generated_text",
            "sections_generated": 1,
        },
    }


def _workflow_prompt(template: WorkflowTemplatePublic, inputs: dict[str, Any]) -> str:
    markets_extra = ""
    if (template.category or "").lower() == "markets" or "market" in (template.slug or ""):
        markets_extra = (
            "This is a Markets analysis workflow.\n"
            "Provide scenario analysis (bullish/base/bearish), catalysts, invalidation levels, and evidence gaps.\n"
            "You MAY discuss possible quote direction and relative probabilities as scenarios.\n"
            "You MUST include an explicit disclaimer that this is not investment advice and outcomes are uncertain.\n"
            "Do NOT claim certainty, guaranteed returns, or that the user will profit.\n"
            "Do NOT instruct specific trade sizes or broker orders.\n"
        )
    return (
        "You are ANCAP's paid AI-workflow execution engine.\n"
        "Return ONLY valid JSON. Do not include markdown fences.\n"
        "Do not promise token price certainty, yield, listing approval, or guaranteed investment returns.\n"
        f"{markets_extra}"
        "The JSON must include: status, workflow_slug, template_title, delivery, deliverable, execution_summary.\n\n"
        f"Workflow slug: {template.slug}\n"
        f"Workflow title: {template.title}\n"
        f"Category: {template.category}\n"
        f"Summary: {template.summary}\n"
        f"Expected output items: {json.dumps(template.output_items, ensure_ascii=False)}\n"
        f"Buyer inputs: {json.dumps(inputs or {}, ensure_ascii=False, sort_keys=True)}\n"
    )


async def _call_teneta_claude(prompt: str, timeout: int = 45) -> tuple[str, dict[str, Any]]:
    settings = get_settings()
    overrides = workflow_provider_credentials.get() or {}
    if not (overrides.get("api_key") or settings.anthropic_api_key):
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")
    base_url = ("https://api.anthropic.com" if overrides.get("api_key") else settings.anthropic_base_url).rstrip("/")
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{base_url}/v1/messages",
            headers={
                "x-api-key": overrides.get("api_key") or settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": overrides.get("model") or settings.llm_model,
                "max_tokens": min(settings.llm_max_tokens, overrides.get("max_tokens", settings.llm_max_tokens)),
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        payload = response.json()
    return _extract_anthropic_text(payload), payload


async def _call_openai(prompt: str, timeout: int = 45) -> tuple[str, dict[str, Any]]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"authorization": f"Bearer {settings.openai_api_key}", "content-type": "application/json"},
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": settings.llm_max_tokens,
            },
        )
        response.raise_for_status()
        payload = response.json()
    text = payload.get("choices", [{}])[0].get("message", {}).get("content") or ""
    return str(text), payload


async def _call_ollama(prompt: str, timeout: int = 45) -> tuple[str, dict[str, Any]]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={"model": settings.llm_model, "prompt": prompt, "stream": False, "options": {"num_predict": min(settings.llm_max_tokens, (workflow_provider_credentials.get() or {}).get("max_tokens", settings.llm_max_tokens))}},
        )
        response.raise_for_status()
        payload = response.json()
    return str(payload.get("response") or ""), payload


async def _store_usage_event(
    session: AsyncSession,
    *,
    owner_user_id: str | UUID | None,
    workflow_run_id: str | UUID | None,
    provider: str,
    model: str,
    prompt: str,
    output_text: str,
    latency_ms: int,
    status: str,
    error: str | None,
    metadata: dict[str, Any],
    provider_status: str = "unknown",
    failure_reason: str | None = None,
    retry_count: int = 0,
) -> LlmUsageEvent:
    row = LlmUsageEvent(
        owner_user_id=owner_user_id,
        workflow_run_id=workflow_run_id,
        provider=provider,
        model=model,
        prompt_hash=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        input_tokens_estimate=_estimate_tokens(prompt),
        output_tokens_estimate=_estimate_tokens(output_text or ""),
        latency_ms=latency_ms,
        status=status,
        error=(error[:1000] if error else None),
        provider_status=provider_status,
        failure_reason=failure_reason,
        retry_count=retry_count,
        cost_currency="ACP",
        cost_amount=Decimal("0"),
        metadata_json=metadata,
    )
    session.add(row)
    await session.flush()
    return row


async def _call_with_retry(
    provider: str,
    prompt: str,
    max_retries: int = 2,
) -> tuple[str, dict[str, Any], int, str, str | None]:
    """Call LLM with exponential backoff retry.
    Returns (text, raw_payload, retry_count, provider_status, failure_reason).
    """
    settings = get_settings()
    timeout = settings.llm_timeout_seconds

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            if provider == "openai":
                output_text, raw = await _call_openai(prompt, timeout)
            elif provider == "ollama":
                output_text, raw = await _call_ollama(prompt, timeout)
            else:
                output_text, raw = await _call_teneta_claude(prompt, timeout)
            return output_text, raw, attempt, "ok", None
        except Exception as exc:
            last_exc = exc
            if not _is_retryable(exc) or attempt >= max_retries:
                break
            # Exponential backoff: 1s, 2s
            time.sleep(2 ** attempt)

    reason = _classify_failure(last_exc) if last_exc else "unknown"
    provider_status = "failed" if reason in ("auth_error", "balance_error", "invalid_model") else "degraded"
    return "", {}, max_retries, provider_status, reason


async def execute_paid_workflow_with_llm(
    session: AsyncSession,
    *,
    template: WorkflowTemplatePublic,
    inputs: dict[str, Any] | None,
    owner_user_id: str | UUID | None,
    workflow_run_id: str | UUID | None,
) -> LlmExecutionResult:
    settings = get_settings()
    overrides = workflow_provider_credentials.get() or {}
    provider = (overrides.get("provider") or settings.llm_provider or "teneta_claude").strip().lower()
    model = overrides.get("model") or settings.llm_model
    prompt = _workflow_prompt(template, inputs or {})
    started = time.perf_counter()
    metadata: dict[str, Any] = {"workflow_slug": template.slug, "provider_configured": provider}

    if template.slug in _COMPLIANCE_LOCKED_SLUGS:
        fallback = execute_workflow_template(template, inputs or {})
        latency_ms = int((time.perf_counter() - started) * 1000)
        fallback["llm_usage"] = {
            "status": "compliance_locked",
            "provider": provider,
            "model": model,
            "fallback_used": True,
            "note": "Vetted template deliverable forced for sensitive medical / adult-hospitality SKU.",
        }
        summary = fallback.setdefault("execution_summary", {})
        if isinstance(summary, dict):
            summary["mode"] = "compliance_locked_template"
        return LlmExecutionResult(
            result=fallback,
            usage_event_id=None,
            provider=provider,
            model=model,
            status="compliance_locked",
            fallback_used=True,
        )

    if provider == "disabled":
        fallback = execute_workflow_template(template, inputs or {})
        latency_ms = int((time.perf_counter() - started) * 1000)
        fallback["llm_usage"] = {
            "status": "disabled",
            "provider": provider,
            "model": model,
            "fallback_used": True,
        }
        fallback.setdefault("execution_summary", {})["mode"] = "template_fallback"
        return LlmExecutionResult(
            result=fallback,
            usage_event_id=None,
            provider=provider,
            model=model,
            status="disabled",
            fallback_used=True,
        )

    output_text, raw, retry_count, provider_status, failure_reason = await _call_with_retry(provider, prompt)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if output_text and provider_status == "ok":
        result = _parse_model_json(output_text)
        result.setdefault("status", "completed")
        result.setdefault("workflow_slug", template.slug)
        result.setdefault("template_title", template.title)
        result.setdefault("delivery", template.output_items)
        summary = result.setdefault("execution_summary", {})
        if isinstance(summary, dict):
            summary["mode"] = summary.get("mode") or "llm_generated"
            summary["llm_provider"] = provider
            summary["llm_model"] = model
        event = await _store_usage_event(
            session,
            owner_user_id=owner_user_id,
            workflow_run_id=workflow_run_id,
            provider=provider,
            model=model,
            prompt=prompt,
            output_text=output_text,
            latency_ms=latency_ms,
            status="succeeded",
            error=None,
            metadata={"raw_response_hash": _sha256_json(raw), **metadata},
            provider_status=provider_status,
            failure_reason=failure_reason,
            retry_count=retry_count,
        )
        result["llm_usage"] = {
            "event_id": str(event.id),
            "provider": provider,
            "model": model,
            "status": "succeeded",
            "provider_status": provider_status,
            "retry_count": retry_count,
        }
        return LlmExecutionResult(
            result=result,
            usage_event_id=str(event.id),
            provider=provider,
            model=model,
            status="succeeded",
            fallback_used=False,
            provider_status=provider_status,
            failure_reason=failure_reason,
            retry_count=retry_count,
        )

    # LLM call failed -> template fallback, mark degraded
    fallback = execute_workflow_template(template, inputs or {})
    summary = fallback.setdefault("execution_summary", {})
    if isinstance(summary, dict):
        summary["mode"] = "template_fallback"
        summary["llm_provider"] = provider
        summary["llm_model"] = model
        summary["degraded"] = True
        summary["degraded_reason"] = failure_reason or "llm_call_failed"
    fallback["degraded_run"] = True
    fallback["degraded_reason"] = failure_reason or "llm_call_failed"
    event = await _store_usage_event(
        session,
        owner_user_id=owner_user_id,
        workflow_run_id=workflow_run_id,
        provider=provider,
        model=model,
        prompt=prompt,
        output_text=json.dumps(fallback, default=str, ensure_ascii=False),
        latency_ms=latency_ms,
        status="fallback" if settings.llm_fallback_to_template else "failed",
        error=failure_reason,
        metadata=metadata,
        provider_status=provider_status,
        failure_reason=failure_reason,
        retry_count=retry_count,
    )
    fallback["llm_usage"] = {
        "event_id": str(event.id),
        "provider": provider,
        "model": model,
        "status": "fallback" if settings.llm_fallback_to_template else "failed",
        "provider_status": provider_status,
        "failure_reason": failure_reason,
        "retry_count": retry_count,
    }
    return LlmExecutionResult(
        result=fallback,
        usage_event_id=str(event.id),
        provider=provider,
        model=model,
        status="fallback",
        fallback_used=True,
        provider_status=provider_status,
        failure_reason=failure_reason,
        retry_count=retry_count,
    )
