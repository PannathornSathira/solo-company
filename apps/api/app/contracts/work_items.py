from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

WorkItemStatus = Literal[
    "proposed", "approved", "running", "review", "done", "failed"
]


class WorkItem(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    company_id: UUID
    objective_id: UUID
    parent_id: UUID | None
    assigned_agent_id: UUID
    title: str = Field(min_length=1, max_length=200)
    instructions: str = Field(min_length=1, max_length=10000)
    deliverable_type: str = Field(min_length=1, max_length=80)
    status: WorkItemStatus
    position: int = Field(ge=1)
    created_at: AwareDatetime
    updated_at: AwareDatetime
