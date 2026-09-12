"""Add user activity timestamp for real streak tracking."""
from alembic import op
import sqlalchemy as sa

revision = "0006_user_activity"
down_revision = "0005_admin"

def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "last_activity_at" not in columns:
        op.add_column("users", sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True))

def downgrade():
    op.drop_column("users", "last_activity_at")