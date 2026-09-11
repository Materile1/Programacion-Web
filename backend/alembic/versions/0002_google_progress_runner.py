"""Add OAuth profile and persisted challenge test cases."""
from alembic import op
import sqlalchemy as sa

revision = "0002_google_progress_runner"
down_revision = "0001_initial"

def upgrade():
    inspector = sa.inspect(op.get_bind())
    if "avatar" not in {column["name"] for column in inspector.get_columns("users")}:
        op.add_column("users", sa.Column("avatar", sa.String(length=500), nullable=True))
    if "test_cases" not in {column["name"] for column in inspector.get_columns("challenges")}:
        op.add_column("challenges", sa.Column("test_cases", sa.Text(), nullable=False, server_default="[]"))

def downgrade():
    op.drop_column("challenges", "test_cases")
    op.drop_column("users", "avatar")