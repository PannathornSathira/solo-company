from pydantic import BaseModel, ConfigDict, Field


class PlanItemDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assigned_agent_slug: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    title: str = Field(min_length=1, max_length=200)
    instructions: str = Field(min_length=1, max_length=10000)
    deliverable_type: str = Field(min_length=1, max_length=80)


class PlanDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_items: list[PlanItemDraft] = Field(min_length=2, max_length=5)


class ArtifactDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    content_markdown: str = Field(min_length=1, max_length=200000)


class ExecutiveBriefDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    content_markdown: str = Field(min_length=1, max_length=200000)
