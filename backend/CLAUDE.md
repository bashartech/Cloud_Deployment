# Backend Guidelines
## Stack
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL
## Project Structure
- `main.py` - FastAPI app entry point
- `models.py` - SQLModel database models
- `routes/` - API route handlers
- `db.py` - Database connection
## API Conventions
- All routes under `/api/`
- Return JSON responses
- Use Pydantic models for request/response
- Handle errors with HTTPException
## Database
- Use SQLModel for all database operations
- Connection string from environment variable: DATABASE_URL
## Running
uvicorn main:app --reload --port 8000
