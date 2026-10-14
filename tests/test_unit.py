"""Unit tests (no database required)."""
import pytest
from pydantic import ValidationError

from app.schemas import Money, StrategyCreateRequest
from app.schemas.strategies import WorkflowSpec, WorkflowStep
from app.schemas.verticals import VerticalSpec, ActionSpec, MetricSpec, ResourceType
from app.services.auth import hash_password, verify_password, create_access_token, decode_token


def test_money_schema():
    m = Money(amount="123.45", currency="USD")
    assert m.amount == "123.45"
    assert m.currency == "USD"
    with pytest.raises(ValidationError):
        Money(amount="not-a-number", currency="USD")


def test_workflow_spec_schema():
    spec = WorkflowSpec(
        vertical_id="00000000-0000-0000-0000-000000000001",
        version="1.0",
        steps=[WorkflowStep(id="s1", action="fetch", args={"x": 1})],
    )
    assert spec.version == "1.0"
    assert len(spec.steps) == 1
    assert spec.steps[0].action == "fetch"


def test_strategy_create_request():
    r = StrategyCreateRequest(
        name="My Strategy",
        vertical_id="00000000-0000-0000-0000-000000000001",
        owner_agent_id="00000000-0000-0000-0000-000000000002",
    )
    assert r.name == "My Strategy"
    r2 = StrategyCreateRequest(
        name="My S",
        vertical_id="v",
        owner_agent_id="a",
        summary="Brief",
    )
    assert r2.summary == "Brief"


def test_vertical_spec_schema():
    spec = VerticalSpec(
        allowed_actions=[ActionSpec(name="act", args_schema={"type": "object"})],
        required_resources={ResourceType.data_feed},
        metrics=[MetricSpec(name="m", value_schema={"type": "number"})],
        risk_spec={},
    )
    assert len(spec.allowed_actions) == 1
    assert ResourceType.data_feed in spec.required_resources


def test_password_hash_verify():
    h = hash_password("secret123")
    assert h != "secret123"
    assert verify_password("secret123", h) is True
    assert verify_password("wrong", h) is False


def test_jwt_create_decode(monkeypatch):
    from app.services import auth
    monkeypatch.setattr(auth.settings, "secret_key", "local-test-signing-key-" * 3)
    token = create_access_token("user-123")
    assert isinstance(token, str)
    sub = decode_token(token)
    assert sub == "user-123"
    assert decode_token("invalid") is None
