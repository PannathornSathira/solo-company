import json
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue, model_validator

MAX_EVENT_PAYLOAD_BYTES = 16_384

EventType = Literal[
    "run.created",
    "plan.proposed",
    "plan.revision_requested",
    "plan.approved",
    "work.started",
    "work.progress",
    "artifact.created",
    "work.completed",
    "work.failed",
    "brief.created",
    "run.completed",
    "run.failed",
]


class RunEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    company_id: UUID
    run_id: UUID
    sequence: int = Field(ge=1)
    event_type: EventType
    summary: str = Field(min_length=1, max_length=240)
    payload_json: dict[str, JsonValue] = Field(default_factory=dict)
    created_at: AwareDatetime

    @model_validator(mode="after")
    def payload_is_bounded(self) -> "RunEvent":
        size = len(
            json.dumps(
                self.payload_json,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode()
        )
        if size > MAX_EVENT_PAYLOAD_BYTES:
            raise ValueError(f"payload_json exceeds {MAX_EVENT_PAYLOAD_BYTES} bytes")
        return self
