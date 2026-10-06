"""
================================================================================
FastAPI Central Application & Router Aggregator
================================================================================
Author: Senior Software Engineer & Cloud Deployment Architect
Framework: FastAPI + SQLModel + PostgreSQL

Key Architectural Features:
1. Decoupled Modular Design:
   - Aggregates domain-specific routers (`users`, `categories`, `documents`).
2. Production Lifespan Management:
   - Initializes schemas and static category seed data on application startup.
3. System Health Checks & Sanitized Diagnostics:
   - Provides safe `/` root navigation and resilient `/health` checks.
4. Cloud CORS & Environment Integration:
   - Origin filtering controlled dynamically via `ALLOWED_ORIGINS`.
================================================================================
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from src.api.categories import router as categories_router
from src.api.document import router as documents_router
from src.api.users import router as users_router
from src.constants.constant import ALLOWED_ORIGINS, DEBUG, ENVIRONMENT, HOST, PORT
from src.data.database import create_db_and_tables, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")

# ==============================================================================
# SECTION 1: APPLICATION LIFECYCLE (LIFESPAN CONTEXT MANAGER)
# ==============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager:
    Runs when the application starts up: provisions DB schemas and seeds initial data.
    Cleanly handles shutdown when stopping.
    """
    logger.info("Initializing Document Management API...")
    create_db_and_tables()
    logger.info("Database verified and tables initialized.")
    yield
    logger.info("Shutting down Document Management API...")


# ==============================================================================
# SECTION 2: FASTAPI APPLICATION INITIALIZATION
# ==============================================================================

app = FastAPI(
    title="Document Management API",
    description=(
        "Production-ready Document Management API featuring independent domain modules:\n"
        "- **Users API**: User registration, password hashing, and user document tracking.\n"
        "- **Categories API**: Category master data management and category-based document filtering.\n"
        "- **Documents API**: PDF upload, magic-byte validation, RapidOCR text extraction, and BLOB downloads."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable secure CORS with explicit allowed origins and Vercel/Render regex patterns
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$|^https://.*\.onrender\.com$|^http://localhost(:\d+)?$|^http://127\.0\.0\.1(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# SECTION 3: SYSTEM & HEALTH CHECK ENDPOINTS
# ==============================================================================


@app.get(
    "/",
    tags=["System"],
    summary="API Root & Navigation Guide",
)
def root() -> dict[str, str]:
    """Root endpoint to check if API is running and navigate documentation."""
    return {
        "title": "Document Management API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "message": "Welcome to the Document Management API. Explore interactive docs at /docs.",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="System Health & Database Connectivity Check",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    """Validates active connectivity to the PostgreSQL database without leaking internal state."""
    try:
        with Session(engine) as session:
            session.exec(select(1)).first()
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        return {
            "status": "degraded",
            "database": "unavailable",
        }


# ==============================================================================
# SECTION 4: MOUNT INDEPENDENT DOMAIN ROUTERS
# ==============================================================================

app.include_router(users_router)
app.include_router(categories_router)
app.include_router(documents_router)


# ==============================================================================
# SECTION 5: SERVER ENTRYPOINT
# ==============================================================================
def run() -> None:
    """CLI Entrypoint for running the Uvicorn server with dynamic host and port binding."""
    import uvicorn

    uvicorn.run(
        "src.api.api:app",
        host=HOST,
        port=PORT,
        reload=DEBUG and ENVIRONMENT == "development",
    )


if __name__ == "__main__":
    run()
