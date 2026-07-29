"""Add runtime retry requests and active-run protection

Revision ID: 0003_runtime_reliability
Revises: 0002_runtime_idempotency
Create Date: 2026-07-28 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_runtime_reliability"
down_revision: Union[str, None] = "0002_runtime_idempotency"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_agent_runs_active_objective",
        "agent_runs",
        ["company_id", "objective_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('pending', 'awaiting_approval', 'running')"
        ),
        sqlite_where=sa.text(
            "status IN ('pending', 'awaiting_approval', 'running')"
        ),
    )
    op.create_table(
        "run_retry_requests",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("company_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("run_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("retry_target", sa.String(length=40), nullable=False),
        sa.Column("work_item_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["agent_runs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["work_item_id"],
            ["work_items.id"],
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "run_id",
            "idempotency_key",
            name="uq_run_retry_requests_run_key",
        ),
    )
    op.create_index(
        "ix_run_retry_requests_company_id",
        "run_retry_requests",
        ["company_id"],
    )
    op.create_index(
        "ix_run_retry_requests_run_id",
        "run_retry_requests",
        ["run_id"],
    )


def downgrade() -> None:
    op.drop_table("run_retry_requests")
    op.drop_index("uq_agent_runs_active_objective", table_name="agent_runs")
