from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title="TaskFlow SaaS",
    description="TaskFlow SaaS API - Task Management Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to TaskFlow SaaS API"}
