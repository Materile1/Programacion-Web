"""Use new-user defaults without rewriting existing account progress."""
from alembic import op

revision = "0007_user_defaults"
down_revision = "0006_user_activity"

def upgrade():
    op.alter_column("users", "level", server_default="0")
    op.alter_column("users", "streak", server_default="0")

def downgrade():
    op.alter_column("users", "level", server_default="7")
    op.alter_column("users", "streak", server_default="12")