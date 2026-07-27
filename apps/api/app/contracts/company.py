from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class Company(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(max_length=2000)
    mission: str = Field(max_length=2000)
    working_rules: list[str] = Field(max_length=20)
    created_at: AwareDatetime
    updated_at: AwareDatetime


class CompanyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    mission: str | None = Field(default=None, max_length=2000)
    working_rules: list[str] | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "CompanyUpdate":
        if (
            self.name is None
            and self.description is None
            and self.mission is None
            and self.working_rules is None
        ):
            raise ValueError("At least one field must be provided in CompanyUpdate")
        return self
