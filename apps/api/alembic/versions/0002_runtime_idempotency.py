"""Add approval idempotency to agent runs

Revision ID: 0002_runtime_idempotency
Revises: 0001_initial_schema
Create Date: 2026-07-27 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_runtime_idempotency"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agent_runs",
        sa.Column("approval_idempotency_key", sa.String(length=128), nullable=True),
    )
    op.create_unique_constraint(
        "uq_agent_runs_approval_idempotency",
        "agent_runs",
        ["company_id", "objective_id", "approval_idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_agent_runs_approval_idempotency",
        "agent_runs",
        type_="unique",
    )
    op.drop_column("agent_runs", "approval_idempotency_key")
