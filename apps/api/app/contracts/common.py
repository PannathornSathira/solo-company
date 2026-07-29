from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RunErrorCode = Literal[
    "INVALID_OBJECTIVE_STATE",
    "AGENT_CONFIGURATION_INVALID",
    "OBJECTIVE_VALIDATION_FAILED",
    "PROMPT_VERSION_NOT_FOUND",
    "PLAN_GENERATION_FAILED",
    "PLAN_PERSISTENCE_FAILED",
    "PLAN_APPROVAL_FAILED",
    "SPECIALIST_EXECUTION_FAILED",
    "ARTIFACT_PERSISTENCE_FAILED",
    "BRIEF_SYNTHESIS_FAILED",
    "RUN_RECOVERY_FAILED",
    "RUNTIME_FAILED",
]

ErrorCode = Literal[
    "NOT_FOUND",
    "VALIDATION_ERROR",
    "STATE_CONFLICT",
    "ACTIVE_RUN_EXISTS",
    "PLAN_NOT_AWAITING_APPROVAL",
    "APPROVAL_ALREADY_CLAIMED",
    "RUN_NOT_RETRYABLE",
    "RUNTIME_UNAVAILABLE",
    "INTERNAL_ERROR",
    *RunErrorCode.__args__,
]


class Health(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"


class Error(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
