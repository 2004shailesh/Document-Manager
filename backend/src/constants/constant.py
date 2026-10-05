"""
================================================================================
Application Configuration & Global Constants
================================================================================
Author: Senior Software Engineer & Cloud Deployment Architect
Purpose:
    Centralizes all environmental configurations, database connection parameters,
    CORS settings, machine learning thresholds, and file upload boundaries.

Key Design Principles:
1. 12-Factor Cloud Configuration:
   - Priority 1: Reads `DATABASE_URL` (cloud managed PostgreSQL like Render, Neon, Supabase).
   - Priority 2: Constructs connection string from individual parameters (DB_HOST, DB_PORT, etc.).
2. Database URL Normalization:
   - Normalizes legacy/cloud driver prefixes (e.g. `postgres://` or `postgresql://`)
     to `postgresql+psycopg2://` while preserving query parameters like `sslmode=require`.
3. Cloud & Container Compatibility:
   - Server host binds to `0.0.0.0` by default and dynamically listens on `$PORT`.
4. Defense-in-Depth Constraints:
   - Enforces a 3 MB file size ceiling across validation and OCR memory limits.
================================================================================
"""

import os
from urllib.parse import quote_plus

# ==============================================================================
# SECTION 1: LOCAL ENVIRONMENT FILE LOADER
# ==============================================================================


def _load_env_file(filepath: str) -> None:
    """Lightweight .env file loader for local development without external dependencies."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


# Attempt to load local environment configuration if present (root or backend)
_load_env_file(".env")
_load_env_file("backend/.env")
_load_env_file(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# ==============================================================================
# SECTION 2: RUNTIME ENVIRONMENT & SERVER BINDING
# ==============================================================================

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
DEBUG: bool = os.getenv(
    "DEBUG", "false" if ENVIRONMENT == "production" else "true"
).lower() in ("true", "1", "yes")

HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# ==============================================================================
# SECTION 3: CORS CONFIGURATION
# ==============================================================================
# Comma-separated list of allowed frontend origins (e.g. "http://localhost:5173,https://your-app.vercel.app")
DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
ALLOWED_ORIGINS_RAW: str = os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
ALLOWED_ORIGINS: list[str] = [
    origin.strip() for origin in ALLOWED_ORIGINS_RAW.split(",") if origin.strip()
]

# ==============================================================================
# SECTION 4: DATABASE CONNECTION PARAMETERS
# ==============================================================================


def build_database_url() -> str:
    """
    Constructs and normalizes the PostgreSQL database connection string.
    Prefers `DATABASE_URL` (standard in Render, Neon, Supabase, AWS RDS).
    Normalizes `postgres://` or `postgresql://` dialects to `postgresql+psycopg2://`.
    """
    raw_url = os.getenv("DATABASE_URL")
    if raw_url and raw_url.strip():
        url = raw_url.strip()
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # Fallback to discrete parameters for local development
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "Document")

    encoded_password = quote_plus(db_password) if db_password else ""
    auth = f"{db_user}:{encoded_password}@" if db_password else f"{db_user}@"
    return f"postgresql+psycopg2://{auth}{db_host}:{db_port}/{db_name}"


DATABASE_URL: str = build_database_url()

# ==============================================================================
# SECTION 5: MACHINE LEARNING & CATEGORIZATION THRESHOLDS
# ==============================================================================

MAX_MATCHED_KEYWORDS: int = 10
ML_CONFIDENCE_THRESHOLD: float = 0.50

# ==============================================================================
# SECTION 6: FILE UPLOAD & INGESTION CONSTRAINTS
# ==============================================================================

MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "3"))
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
