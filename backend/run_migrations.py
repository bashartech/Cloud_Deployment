"""Script to run database migrations manually."""
import os
import sys
from sqlmodel import SQLModel, create_engine
from alembic import command
from alembic.config import Config

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the models to ensure they're registered with SQLModel metadata
from models.task import Task
from models.conversation import Conversation
from models.chat_message import ChatMessage

def run_migrations():
    """Run database migrations."""
    # Create the alembic config
    alembic_cfg = Config("alembic.ini")

    print("Running database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()