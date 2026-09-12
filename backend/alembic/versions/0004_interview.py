"""Add technical interview questions and sessions."""
from alembic import op
import sqlalchemy as sa

revision = "0004_interview"
down_revision = "0003_review_content"

def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = inspector.get_table_names()
    if "interview_questions" not in tables:
        op.create_table(
            "interview_questions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("kind", sa.String(length=20), nullable=False),
            sa.Column("prompt", sa.Text(), nullable=False),
            sa.Column("expected_points", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("test_cases", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("time_limit_seconds", sa.Integer(), nullable=False, server_default="120"),
            sa.Column("source", sa.String(length=30), nullable=False, server_default="seed"),
        )
    if "interview_sessions" not in tables:
        op.create_table(
            "interview_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "interview_answers" not in tables:
        op.create_table(
            "interview_answers",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("session_id", sa.Integer(), sa.ForeignKey("interview_sessions.id"), nullable=False),
            sa.Column("question_id", sa.Integer(), sa.ForeignKey("interview_questions.id"), nullable=False),
            sa.Column("answer", sa.Text(), nullable=False),
            sa.Column("score", sa.Float(), nullable=False, server_default="0"),
            sa.Column("feedback", sa.Text(), nullable=False, server_default=""),
            sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        )

def downgrade():
    op.drop_table("interview_answers")
    op.drop_table("interview_sessions")
    op.drop_table("interview_questions")