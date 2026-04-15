from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260408_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False),
        sa.Column("rubric_json", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_questions_type", "questions", ["type"])

    op.create_table(
        "test_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
    )
    op.create_index("ix_test_sessions_candidate_id", "test_sessions", ["candidate_id"])

    op.create_table(
        "session_questions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["test_sessions.id"]),
        sa.UniqueConstraint("session_id", "sequence_no", name="uq_session_sequence"),
    )
    op.create_index("ix_session_questions_session_id", "session_questions", ["session_id"])

    op.create_table(
        "submissions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_question_id", sa.String(length=36), nullable=False),
        sa.Column("submission_type", sa.String(length=32), nullable=False),
        sa.Column("text_answer", sa.Text(), nullable=True),
        sa.Column("code_answer", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_question_id"], ["session_questions.id"]),
    )
    op.create_index("ix_submissions_session_question_id", "submissions", ["session_question_id"])

    op.create_table(
        "ai_interactions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_question_id", sa.String(length=36), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("ai_response", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_question_id"], ["session_questions.id"]),
    )
    op.create_index("ix_ai_interactions_session_question_id", "ai_interactions", ["session_question_id"])

    op.create_table(
        "evaluator_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_question_id", sa.String(length=36), nullable=False),
        sa.Column("evaluator_type", sa.String(length=32), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_question_id"], ["session_questions.id"]),
    )
    op.create_index("ix_evaluator_runs_session_question_id", "evaluator_runs", ["session_question_id"])

    op.create_table(
        "dimension_scores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("dimension_name", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["test_sessions.id"]),
    )
    op.create_index("ix_dimension_scores_session_id", "dimension_scores", ["session_id"])

    op.create_table(
        "final_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), nullable=False, unique=True),
        sa.Column("recommendation", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("chart_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["test_sessions.id"]),
    )
    op.create_index("ix_final_reports_session_id", "final_reports", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_final_reports_session_id", table_name="final_reports")
    op.drop_table("final_reports")
    op.drop_index("ix_dimension_scores_session_id", table_name="dimension_scores")
    op.drop_table("dimension_scores")
    op.drop_index("ix_evaluator_runs_session_question_id", table_name="evaluator_runs")
    op.drop_table("evaluator_runs")
    op.drop_index("ix_ai_interactions_session_question_id", table_name="ai_interactions")
    op.drop_table("ai_interactions")
    op.drop_index("ix_submissions_session_question_id", table_name="submissions")
    op.drop_table("submissions")
    op.drop_index("ix_session_questions_session_id", table_name="session_questions")
    op.drop_table("session_questions")
    op.drop_index("ix_test_sessions_candidate_id", table_name="test_sessions")
    op.drop_table("test_sessions")
    op.drop_index("ix_questions_type", table_name="questions")
    op.drop_table("questions")
    op.drop_table("candidates")
