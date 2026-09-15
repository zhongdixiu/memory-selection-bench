from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Status(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNSUPPORTED = "UNSUPPORTED"
    BLOCKED = "BLOCKED"
    TIMEOUT = "TIMEOUT"
    NOT_RUN = "NOT_RUN"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class Track(StrEnum):
    NATIVE = "native"
    CONFIGURED = "configured"
    ENHANCED = "enhanced"
    R0 = "r0"
    R1 = "r1"
    P_NATIVE = "p-native"


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: str
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    occurred_at: str


class Scope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["user_public", "domain", "project", "agent_private"]
    scope_id: str
    project_id: str | None = None


class WriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str
    namespace: str
    principal_id: str
    source_id: str
    source_session_id: str
    source_agent_id: str
    source_domain_id: str
    source_timezone: str = "Asia/Shanghai"
    messages: list[Message] = Field(min_length=1)
    write_mode: Literal["conversation", "direct_record"] = "conversation"
    requested_scope: Scope


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str
    namespace: str
    principal_id: str
    query: str
    top_k: int = Field(default=5, ge=1, le=100)
    purpose: Literal["current", "history"] = "current"


class SearchHit(BaseModel):
    native_id: str
    text: str
    score: float | None = None
    native_metadata: dict[str, Any] = Field(default_factory=dict)
    source_refs: list[str] | None = None
    observed_at: str


class WriteReceipt(BaseModel):
    request_id: str
    status: Status
    accepted: bool = False
    processed: bool | None = None
    native_ids: list[str] = Field(default_factory=list)
    received_at: str
    elapsed_ms: int
    raw: Any = None
    error: str | None = None


class SearchResult(BaseModel):
    request_id: str
    status: Status
    hits: list[SearchHit] = Field(default_factory=list)
    elapsed_ms: int
    raw: Any = None
    error: str | None = None
    rerank_configured: bool = False
    rerank_requested: bool = False
    rerank_applied: bool = False


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    tenant_id: str
    owner_user_id: str | None = None
    agent_id: str
    domain_id: str
    allowed_projects: list[str] = Field(default_factory=list)
    allowed_agent_private: list[str] = Field(default_factory=list)


class AssertionSpec(BaseModel):
    required_propositions: list[str] = Field(default_factory=list)
    forbidden_propositions: list[str] = Field(default_factory=list)
    required_tokens: list[str] = Field(default_factory=list)
    forbidden_tokens: list[str] = Field(default_factory=list)
    source_message_ids: list[str] = Field(default_factory=list)
    source_check: Literal["none", "any", "per_claim"] = "none"


class Operation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    op: Literal["write", "search", "await_observable"]
    request_id: str | None = None
    receipt_ref: str | None = None
    principal_id: str | None = None
    source_id: str | None = None
    source_session_id: str | None = None
    source_agent_id: str = "email_agent"
    source_domain_id: str = "email"
    scope_kind: Literal["user_public", "domain", "project", "agent_private"] | None = None
    scope_id: str | None = None
    project_id: str | None = None
    write_mode: Literal["conversation", "direct_record"] = "conversation"
    messages: list[Message] = Field(default_factory=list)
    query: str | None = None
    purpose: Literal["current", "history"] = "current"
    assertions: AssertionSpec | None = None

    @model_validator(mode="after")
    def validate_operation(self) -> "Operation":
        if self.op == "write":
            needed = (self.request_id, self.principal_id, self.source_id, self.source_session_id, self.scope_kind, self.scope_id)
            if not all(needed) or not self.messages:
                raise ValueError("write operation is missing required fields")
        elif self.op == "search":
            if not self.request_id or not self.principal_id or not self.query or self.assertions is None:
                raise ValueError("search operation is missing required fields")
        elif not self.receipt_ref:
            raise ValueError("await_observable requires receipt_ref")
        return self


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    group: Literal["fact", "negative", "user", "domain", "project", "conflict", "temporal", "experience"]
    title: str
    operations: list[Operation] = Field(min_length=1)

