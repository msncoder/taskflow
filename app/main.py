from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    BadRequestException,
    unauthorized_handler,
    forbidden_handler,
    not_found_handler,
    conflict_handler,
    bad_request_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.db.session import close_db


app = FastAPI(
    title="TaskFlow SaaS",
    description="TaskFlow SaaS API - Task Management Platform",
    version="0.1.0",
)


# Register exception handlers
app.add_exception_handler(UnauthorizedException, unauthorized_handler)
app.add_exception_handler(ForbiddenException, forbidden_handler)
app.add_exception_handler(NotFoundException, not_found_handler)
app.add_exception_handler(ConflictException, conflict_handler)
app.add_exception_handler(BadRequestException, bad_request_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Lifecycle events
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_db()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to TaskFlow SaaS API"}
