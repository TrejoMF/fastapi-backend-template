from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routes import user_routes
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created.")
    yield
    # Code to run on shutdown (if any)
    print("Shutting down...")

app = FastAPI(lifespan=lifespan, title="User Management API", version="0.1.0")

# Include routers
app.include_router(user_routes.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the User Management API"}

# Run the application with uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
