# Neon PostgreSQL Integration with SQLModel Skill

## Purpose
Integrate a Python web application (FastAPI/SQLModel) with Neon PostgreSQL database, creating proper database schema with user isolation and efficient indexing.

## Prerequisites
- Python 3.11+
- SQLModel installed
- Neon PostgreSQL database created with credentials
- Environment variables configured (DATABASE_URL, etc.)

## Step-by-Step Process

### Step 1: Environment Configuration
1. Create `.env` file in project root with:
```
DATABASE_URL="postgresql://username:password@ep-xxx.region.provider.neon.tech/dbname?sslmode=require"
```

2. Ensure `python-dotenv` is installed:
```bash
pip install python-dotenv
```

### Step 2: Model Definition
1. Create model in `models/task.py`:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key reference to users.id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

2. Create `models/__init__.py` to make it a package:
```bash
touch models/__init__.py
```

### Step 3: Database Connection Setup
1. Create `db.py`:
```python
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

def get_database_url():
    """Get database URL from environment with fallback."""
    return os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")

def get_engine():
    """Create database engine with current environment."""
    database_url = get_database_url()
    return create_engine(database_url, echo=True)

engine = get_engine()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """Create all database tables from SQLModel models."""
    global engine
    engine = get_engine()  # Reload to get latest environment
    SQLModel.metadata.create_all(engine)
```

### Step 4: Table Creation
1. Run table creation with proper environment loading:
```python
import os
import sys
from dotenv import load_dotenv

# Load environment before importing modules
load_dotenv('.env')  # From root directory

from sqlmodel import SQLModel
from models.task import Task  # This registers model with metadata
from db import get_engine

# Create engine and tables
engine = get_engine()
SQLModel.metadata.create_all(engine)
```

## Common Error Possibilities & Solutions

### Error 1: Module Import Issues
**Symptoms**: `ModuleNotFoundError: No module named 'models.task'`
**Cause**: Directory not recognized as package
**Solution**: Create `models/__init__.py` file

### Error 2: Environment Variables Not Loading
**Symptoms**: Connecting to default SQLite instead of Neon
**Cause**: Environment variables loaded after module import
**Solution**: Load environment variables BEFORE importing database modules

### Error 3: Missing PostgreSQL Driver
**Symptoms**: `ModuleNotFoundError: No module named 'psycopg2'`
**Cause**: PostgreSQL driver not installed
**Solution**: Install PostgreSQL driver: `pip install psycopg2-binary`

### Error 4: Connection Authentication Failures
**Symptoms**: Authentication errors, SSL issues
**Cause**: Incorrect credentials or SSL settings
**Solution**: Verify Neon connection string format with proper SSL parameters

### Error 5: Circular Imports
**Symptoms**: Import errors between model files
**Cause**: Improper import structure
**Solution**: Use `TYPE_CHECKING` pattern or direct imports

### Error 6: Tables Not Appearing in DB Interface
**Symptoms**: Command succeeds but tables not visible in Neon console
**Cause**: Transaction not committed, or interface refresh needed
**Solution**: Ensure `create_all()` executes properly and refresh database interface

## Data Flow Process
1. **User Action**: User creates/updates/deletes tasks via frontend
2. **Authentication**: JWT token verified, user_id extracted
3. **Database Operation**: SQLModel creates appropriate SQL with user_id filter
4. **Storage**: Data stored in Neon DB with user_id linking
5. **Retrieval**: Only records matching authenticated user_id returned
6. **Display**: User sees only their own tasks

## Security Features
- User isolation via user_id foreign key
- JWT-based authentication for all operations
- Server-side filtering to prevent unauthorized access
- SSL encryption for all database connections

## Performance Optimizations
- Index on `user_id` field for efficient filtering
- Index on `completed` field for status-based queries
- Connection pooling via SQLAlchemy engine

## Verification Steps
1. Run table creation command
2. Query `information_schema.tables` to verify table exists
3. Test with sample data insertion
4. Verify user isolation works correctly
5. Confirm indexes are created properly

## Troubleshooting Commands
```bash
# Check if tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

# Check table structure
SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'tasks';

# Verify user isolation
SELECT COUNT(*) FROM tasks WHERE user_id = 'specific_user_id';
```

## Integration Checklist
- [ ] Environment variables loaded before module imports
- [ ] PostgreSQL driver installed (`psycopg2-binary`)
- [ ] Models directory has `__init__.py`
- [ ] Database URL format correct for Neon
- [ ] SSL settings properly configured
- [ ] Indexes created on user_id and frequently queried fields
- [ ] User isolation implemented in all queries
- [ ] Error handling for database connections implemented

# COMMAND TO CREATE TABLE IN NEON DB

the correct command I used to create the table in Neon DB:

  .venv/Scripts/python.exe -c "
  import os
  import sys
  from dotenv import load_dotenv

  # Load environment from the project root directory where .env is located   
  load_dotenv('../.env')  # Load from parent directory (root project)        

  print('DATABASE_URL after loading from root:', os.getenv('DATABASE_URL'))  

  from sqlmodel import SQLModel
  from models.task import Task  # This registers model with metadata
  from db import get_engine

  # Create engine and tables - now using the correct database URL
  engine = get_engine()
  print('Connected to database:', engine.url)
  SQLModel.metadata.create_all(engine)
  print('Task table created successfully in Neon database!')
  "

  Key correction: The path in load_dotenv('../.env') was crucial - it loads the .env file from the project root directory, ensuring that the DATABASE_URL 
environment variable is properly set to the Neon PostgreSQL URL instead of defaulting to SQLite.

  The original issue was that the environment wasn't loaded from the correct 
path, so the script was defaulting to sqlite:///./todo_app.db instead of connecting to Neon PostgreSQL.
