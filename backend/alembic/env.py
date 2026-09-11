from app.database import Base
from app.config import get_settings
from app.models import *
from alembic import context

target_metadata = Base.metadata
config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

def run_migrations_online():
    from sqlalchemy import engine_from_config, pool
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()

run_migrations_online()
