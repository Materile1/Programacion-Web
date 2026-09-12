"""Add administrator flag."""
from alembic import op
import sqlalchemy as sa

revision = "0005_admin"
down_revision = "0004_interview"

def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "is_admin" not in columns:
        op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column("users", "is_admin")