"""initial DevCoach schema"""
from alembic import op
from sqlalchemy import inspect
from app.database import Base
from app.models import *

revision = "0001_initial"
down_revision = None

def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
