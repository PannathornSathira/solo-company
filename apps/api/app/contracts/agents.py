from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class AgentDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    company_id: UUID
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    objective: str = Field(max_length=2000)
    responsibilities: list[str] = Field(max_length=20)
    runtime_model_alias: str = Field(min_length=1, max_length=80)
    prompt_version: str = Field(min_length=1, max_length=40)
    enabled: bool
    created_at: AwareDatetime
    updated_at: AwareDatetime


class AgentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    role: str | None = Field(default=None, min_length=1, max_length=120)
    objective: str | None = Field(default=None, max_length=2000)
    responsibilities: list[str] | None = Field(default=None, max_length=20)
    runtime_model_alias: str | None = Field(default=None, min_length=1, max_length=80)
    prompt_version: str | None = Field(default=None, min_length=1, max_length=40)
    enabled: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "AgentUpdate":
        if (
            self.name is None
            and self.role is None
            and self.objective is None
            and self.responsibilities is None
            and self.runtime_model_alias is None
            and self.prompt_version is None
            and self.enabled is None
        ):
            raise ValueError("At least one field must be provided in AgentUpdate")
        return self
