from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260408_0002"
down_revision = "20260408_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evaluator_runs",
        sa.Column("source", sa.String(length=32), nullable=False, server_default="fallback"),
    )
    op.add_column("evaluator_runs", sa.Column("raw_output", sa.Text(), nullable=True))
    op.add_column("evaluator_runs", sa.Column("error_message", sa.Text(), nullable=True))
    op.alter_column("evaluator_runs", "source", server_default=None)

    op.add_column(
        "final_reports",
        sa.Column("source", sa.String(length=32), nullable=False, server_default="fallback"),
    )
    op.add_column("final_reports", sa.Column("raw_output", sa.Text(), nullable=True))
    op.add_column("final_reports", sa.Column("error_message", sa.Text(), nullable=True))
    op.alter_column("final_reports", "source", server_default=None)


def downgrade() -> None:
    op.drop_column("final_reports", "error_message")
    op.drop_column("final_reports", "raw_output")
    op.drop_column("final_reports", "source")

    op.drop_column("evaluator_runs", "error_message")
    op.drop_column("evaluator_runs", "raw_output")
    op.drop_column("evaluator_runs", "source")
