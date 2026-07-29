from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(
        self, value: datetime | None, dialect: sa.Dialect
    ) -> datetime | None:
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class Base(DeclarativeBase):
    pass


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    mission: Mapped[str] = mapped_column(String(2000), nullable=False)
    working_rules: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class AgentDefinitionModel(Base):
    __tablename__ = "agent_definitions"
    __table_args__ = (
        UniqueConstraint("company_id", "slug", name="uq_agent_definitions_company_slug"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    objective: Mapped[str] = mapped_column(String(2000), nullable=False)
    responsibilities: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    runtime_model_alias: Mapped[str] = mapped_column(String(80), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(40), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class ObjectiveModel(Base):
    __tablename__ = "objectives"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    desired_outcome: Mapped[str] = mapped_column(String(4000), nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False, default="")
    constraints: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class WorkItemModel(Base):
    __tablename__ = "work_items"
    __table_args__ = (
        CheckConstraint("position >= 1", name="ck_work_items_positive_position"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    objective_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("objectives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("work_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_agent_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agent_definitions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    deliverable_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="proposed")
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class AgentRunModel(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "objective_id",
            "approval_idempotency_key",
            name="uq_agent_runs_approval_idempotency",
        ),
        Index(
            "uq_agent_runs_active_objective",
            "company_id",
            "objective_id",
            unique=True,
            postgresql_where=sa.text(
                "status IN ('pending', 'awaiting_approval', 'running')"
            ),
            sqlite_where=sa.text(
                "status IN ('pending', 'awaiting_approval', 'running')"
            ),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    objective_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("objectives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    graph_version: Mapped[str] = mapped_column(String(40), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    approval_idempotency_key: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class RunRetryRequestModel(Base):
    __tablename__ = "run_retry_requests"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "idempotency_key",
            name="uq_run_retry_requests_run_key",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    retry_target: Mapped[str] = mapped_column(String(40), nullable=False)
    work_item_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("work_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )


class RunEventModel(Base):
    __tablename__ = "run_events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_run_events_run_sequence"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    summary: Mapped[str] = mapped_column(String(240), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )


class ArtifactModel(Base):
    __tablename__ = "artifacts"
    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_artifacts_positive_version"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_item_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("work_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    artifact_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow
    )
