# Backend Source Code Structure

This document details the layout, module boundaries, and internal dependencies of the Python backend package located in `backend/src/`.

---

## 🗂️ Backend Source Tree

```text
backend/
├── document_management_system.egg-info/  # Setuptools editable build metadata
└── src/
    ├── __init__.py                       # Package identifier
    │
    ├── api/                              # REST API routing layer & DTO schemas
    │   ├── __init__.py
    │   ├── api.py                        # Central FastAPI app, CORS, lifespan & router mounting
    │   ├── categories.py                 # Category master data endpoints (Read-only)
    │   ├── document.py                   # PDF upload, streaming download & document CRUD
    │   ├── security.py                   # PasswordHash singleton using pwdlib
    │   └── users.py                      # User registration, login & ownership endpoints
    │
    ├── constants/                        # Configuration & environment variable ingestion
    │   ├── __init__.py
    │   └── constant.py                   # DB URL assembly, size limits (3MB), confidence thresholds
    │
    ├── data/                             # Persistence & relational data models
    │   ├── __init__.py
    │   └── database.py                   # Engine, session dependency, SQLModel models, seeders & backfill
    │
    └── model/                            # Document text extraction & classification pipeline
        ├── __init__.py
        ├── categorizer.py                # TF-IDF + Naive Bayes, category keyword scanning & scoring
        └── contents.py                   # Defense-in-depth PDF validation, PyMuPDF & RapidOCR
```

---

## 📦 Package Module Responsibilities

### 1. `src.api.api`
- Instantiates the root `FastAPI` instance.
- Defines the `@asynccontextmanager lifespan(app)` function which triggers database creation and master data seeding.
- Configures global `CORSMiddleware`.
- Mounts `/users`, `/categories`, and `/documents` routers.
- Exposes root status (`GET /`) and health diagnostics (`GET /health`).

### 2. `src.api.users`
- Defines DTOs: `UserCreate`, `UserLogin`, `UserPublic`, `UserUpdate`, `UserDocumentSummary`.
- Exposes CRUD and authentication endpoints for user accounts.
- Hashes passwords using `src.api.security.password_hash`.
- Traverses 1-to-Many user-document ownership mappings via `UserDocument`.

### 3. `src.api.categories`
- Defines DTOs: `CategoryPublic`, `CategoryDocumentSummary`.
- Exposes read-only master data endpoints (`GET /categories/`, `GET /categories/{id}`).
- Traverses Many-to-Many category-document associations via `DocumentCategories`.

### 4. `src.api.document`
- Defines DTOs: `DocumentPublic`, `DocumentDetailPublic`, `DocumentUpdate`, `CategorySummary`.
- Implements `resolve_categories()` to flexibly match numeric IDs, category names, or aliases.
- Handles multipart PDF uploads, validates file structure, triggers dual-pass extraction and classification, and persists records.
- Streams original PDF binaries as file downloads with `Content-Disposition: attachment`.

### 5. `src.constants.constant`
- Ingests `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DEFAULT_DB`.
- Assembles URL-encoded `DATABASE_URL`.
- Declares constraints: `MAX_FILE_SIZE_MB = 3`, `MAX_FILE_SIZE_BYTES = 3,145,728`, `ML_CONFIDENCE_THRESHOLD = 0.50`, `MAX_MATCHED_KEYWORDS = 10`.

### 6. `src.data.database`
- Creates the SQLAlchemy/SQLModel `engine` with `pool_pre_ping=True`.
- Provides the `get_session()` generator for FastAPI dependency injection.
- Defines SQLModel entities: `User`, `Category`, `Document`, `DocumentCategories`, `UserDocument`, `CategoryKeyword`.
- Implements lifecycle functions: `ensure_database_exists()`, `seed_static_categories()`, `seed_category_keywords()`, `backfill_uncategorized_documents()`, `create_db_and_tables()`.

### 7. `src.model.contents`
- Validates PDF files via `validate_pdf_file()` (empty check, 3MB limit, `.pdf` extension, `%PDF` magic bytes).
- Manages singleton `RapidOCR` instance (`get_ocr_engine()`).
- Extracts vector text using PyMuPDF (`page.get_text()`) and falls back to OCR on rendered 150 DPI PNG pixmaps for scanned pages.

### 8. `src.model.categorizer`
- Implements `DocumentCategorizer` pipeline with TF-IDF Vectorizer + Multinomial Naive Bayes.
- Contains `BASE_TRAINING_CORPUS` (28 multi-domain samples).
- Executes keyword scanning against the database `category_keyword` table.
- Implements `predict()` (single category) and `predict_multi()` (multi-category assignment with `Others` fallback).
