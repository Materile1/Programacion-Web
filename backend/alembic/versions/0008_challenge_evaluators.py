"""Add extensible challenge evaluators and SQL setup data."""
from alembic import op
import sqlalchemy as sa

revision = "0008_challenge_evaluators"
down_revision = "0007_user_defaults"

def upgrade():
    op.add_column("challenges", sa.Column("evaluator_type", sa.String(length=30), nullable=False, server_default="python"))
    op.add_column("challenges", sa.Column("setup_sql", sa.Text(), nullable=True))

def downgrade():
    op.drop_column("challenges", "setup_sql")
    op.drop_column("challenges", "evaluator_type")