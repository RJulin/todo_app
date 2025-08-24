from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api_router
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="A simple todo application API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with no prefix to keep endpoints at /api/todoapp/...
app.include_router(api_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Todo API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 