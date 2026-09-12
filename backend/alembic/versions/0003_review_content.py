"""Add review snippets and content source metadata."""
from alembic import op
import sqlalchemy as sa

revision = "0003_review_content"
down_revision = "0002_google_progress_runner"

def upgrade():
    inspector = sa.inspect(op.get_bind())
    challenge_columns = {column["name"] for column in inspector.get_columns("challenges")}
    if "source" not in challenge_columns:
        op.add_column("challenges", sa.Column("source", sa.String(length=30), nullable=False, server_default="seed"))
    if "review_snippets" not in inspector.get_table_names():
        op.create_table(
            "review_snippets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("language", sa.String(length=30), nullable=False, server_default="python"),
            sa.Column("code", sa.Text(), nullable=False),
            sa.Column("known_issues", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("difficulty", sa.String(length=30), nullable=False, server_default="Intermedio"),
            sa.Column("source", sa.String(length=30), nullable=False, server_default="seed"),
        )

def downgrade():
    op.drop_table("review_snippets")
    op.drop_column("challenges", "source")