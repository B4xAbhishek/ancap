"""Validated requests for persistent workflow operations."""
from typing import Any, Literal
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator


class ContextDocument(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=16000)


class ProjectWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    context: str = Field(default="", max_length=16000)
    documents: list[ContextDocument] = Field(default_factory=list, max_length=10)
    retention_days: int = Field(default=30, ge=1, le=365)


class WorkflowStep(BaseModel):
    slug: str = Field(min_length=1, max_length=100)
    inputs: dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    required_text: list[str] = Field(default_factory=list, max_length=10)


class AutomationWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    project_id: str
    steps: list[WorkflowStep] = Field(min_length=1, max_length=5)
    inputs: dict[str, Any] = Field(default_factory=dict)
    coin_ids: list[str] = Field(default_factory=list, max_length=10)
    require_review: bool = True
    connection_ids: list[str] = Field(default_factory=list, max_length=3)
    provider_connection_id: str | None = None
    test_cases: list[TestCase] = Field(default_factory=list, max_length=10)


class ConnectionWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    kind: Literal["webhook", "telegram", "google_sheets", "hubspot", "anthropic"]
    config: dict[str, str] = Field(default_factory=dict)
    secret: str = Field(default="", max_length=8192)
    allow_delivery: bool = False


class ScheduleWrite(BaseModel):
    enabled: bool = False
    interval_minutes: int = Field(default=1440, ge=60, le=43200)
    monthly_budget_acp: Decimal = Field(gt=0, le=210000000)


class EnqueueRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=100, pattern=r"^[a-zA-Z0-9_:\-]+$")
    max_cost_acp: Decimal = Field(gt=0, le=210000000)
    inputs: dict[str, Any] = Field(default_factory=dict)
    rows: list[dict[str, Any]] = Field(default_factory=list, max_length=20)
    kind: Literal["manual", "test", "batch"] = "manual"

    @model_validator(mode="after")
    def batch_rows(self):
        if self.kind == "batch" and not self.rows:
            raise ValueError("Batch requires at least one row")
        if self.kind != "batch" and self.rows:
            raise ValueError("Rows require batch mode")
        return self


class ReviewWrite(BaseModel):
    decision: Literal["approve", "reject"]
    note: str = Field(default="", max_length=1000)
    edited_output: dict[str, Any] | None = None


class TrialWrite(BaseModel):
    project_name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    language: Literal["en", "ru", "uk", "de", "zh-Hant"] = "en"


class VersionSelect(BaseModel):
    version: int = Field(ge=1)


class DeliveryRetry(BaseModel):
    connection_id: str
    confirm_retry: bool = False


class ProjectMemberWrite(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    role: Literal["viewer", "editor", "remove"] = "viewer"
