from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

ObjectiveStatus = Literal[
    "draft",
    "planning",
    "awaiting_approval",
    "approved",
    "running",
    "completed",
    "failed",
]


class Objective(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    company_id: UUID
    title: str = Field(min_length=1, max_length=200)
    desired_outcome: str = Field(min_length=1, max_length=4000)
    context: str = Field(max_length=10000)
    constraints: list[str] = Field(max_length=30)
    status: ObjectiveStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime


class ObjectiveCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    desired_outcome: str = Field(min_length=1, max_length=4000)
    context: str = Field(default="", max_length=10000)
    constraints: list[str] = Field(default_factory=list, max_length=30)
