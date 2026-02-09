from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('../../../.env')  # Load from project root directory

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import SQLModel and your models for autogenerate support
from sqlmodel import SQLModel
sys.path.insert(0, os.path.abspath('.'))  # Add current directory to path
from models.task import Task
from models.conversation import Conversation
from models.chat_message import ChatMessage

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use DATABASE_URL from environment if available, otherwise from config
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use DATABASE_URL from environment if available, otherwise from config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Check if we're running a revision command (autogenerate)
# If we are, we don't need to connect to the database
if context.config.cmd_opts and hasattr(context.config.cmd_opts, 'autogenerate') and context.config.cmd_opts.autogenerate:
    # For autogenerate, we just need to configure the metadata
    connectable = None
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        # For online autogenerate, we still need to connect
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            url=os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
        )
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )
            # Don't run migrations, just configure for autogenerate
else:
    # For normal migration execution
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
