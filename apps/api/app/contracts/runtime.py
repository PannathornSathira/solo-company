from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.contracts.work_items import WorkItem

RunStatus = Literal[
    "pending", "awaiting_approval", "running", "completed", "failed"
]


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective_id: UUID
    work_items: list[WorkItem] = Field(min_length=2, max_length=5)


class PlanRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feedback: str = Field(min_length=1, max_length=4000)


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    company_id: UUID
    objective_id: UUID
    status: RunStatus
    graph_version: str = Field(min_length=1, max_length=40)
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None
    error_code: str | None = Field(default=None, max_length=80)
    created_at: AwareDatetime
    updated_at: AwareDatetime


class Artifact(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    company_id: UUID
    run_id: UUID
    work_item_id: UUID | None = None
    artifact_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    content_markdown: str = Field(max_length=200000)
    version: int = Field(ge=1)
    created_at: AwareDatetime
    updated_at: AwareDatetime
