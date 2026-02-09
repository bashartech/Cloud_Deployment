from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables explicitly
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is not installed, environment variables should be loaded by the system
    pass

# Import JWT middleware
try:
    from .middleware.jwt_middleware import JWTBearer
except ImportError:
    from middleware.jwt_middleware import JWTBearer

# Import event publisher for initialization
try:
    from .utils.event_publisher import get_event_publisher
except ImportError:
    from utils.event_publisher import get_event_publisher

app = FastAPI(title="Todo App Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT authentication middleware for protected routes
# We'll use JWTBearer as a dependency in individual routes rather than global middleware
# to have more control over which routes are protected

@app.on_event("startup")
async def startup_event():
    """Initialize Dapr client and event publisher on startup."""
    # Initialize the event publisher
    _ = get_event_publisher()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    # Close the event publisher's HTTP client
    from .utils.event_publisher import _event_publisher
    if _event_publisher:
        await _event_publisher.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo App Backend!"}

# Include routes
try:
    from .routes import tasks
    from .routes import chat
    from .health import router as health_router
except (ImportError, ValueError):
    from routes import tasks
    from routes import chat
    from health import router as health_router

app.include_router(tasks.router, prefix="/api")
app.include_router(chat.router)
app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
