# Backend Architecture

This document describes the internal architecture of the FastAPI backend service, including the lifespan lifecycle manager, router modularization, dependency injection, and data access layer.

---

## 🏗️ Backend Module Breakdown

```mermaid
flowchart TD
    MainWrapper["main.py (Root Wrapper)"] --> AppInit["backend/src/api/api.py (app = FastAPI)"]
    
    subgraph LifespanLifecycle["FastAPI Lifespan Management"]
        Lifespan["@asynccontextmanager lifespan(app)"]
        Lifespan --> AutoProv["ensure_database_exists()"]
        AutoProv --> CreateTables["SQLModel.metadata.create_all()"]
        CreateTables --> SchemaVerif["ALTER TABLE dynamic schema checks"]
        SchemaVerif --> SeedCats["seed_static_categories() (1..6)"]
        SeedCats --> SeedKeywords["seed_category_keywords()"]
        SeedKeywords --> Backfill["backfill_uncategorized_documents()"]
    end

    subgraph Routers["Domain Routers"]
        UsersRouter["users.py (/users)"]
        CategoriesRouter["categories.py (/categories)"]
        DocumentsRouter["document.py (/documents)"]
        RootRouter["api.py (/ & /health)"]
    end

    subgraph ServiceLayer["Service Engines"]
        Security["security.py (pwdlib / Argon2)"]
        ContentsService["contents.py (PDF Validation, PyMuPDF, RapidOCR)"]
        CategorizerService["categorizer.py (TF-IDF + Naive Bayes + Keyword Scan)"]
    end

    subgraph DataLayer["Data Layer (database.py)"]
        Engine["create_engine(DATABASE_URL, pool_pre_ping=True)"]
        GetSession["get_session() -> Generator[Session]"]
        Models["SQLModel Models (User, Document, Category, etc.)"]
    end

    AppInit --> Lifespan
    AppInit --> UsersRouter
    AppInit --> CategoriesRouter
    AppInit --> DocumentsRouter
    AppInit --> RootRouter

    UsersRouter --> Security
    UsersRouter --> GetSession
    CategoriesRouter --> GetSession
    DocumentsRouter --> ContentsService
    DocumentsRouter --> CategorizerService
    DocumentsRouter --> GetSession

    GetSession --> Engine
    Engine --> Models
```

---

## ⚙️ Core Backend Architectural Patterns

### 1. Lifespan Context Manager
FastAPI's modern `@asynccontextmanager` pattern (`backend/src/api/api.py:lifespan`) manages the application startup and shutdown lifecycle:
- On startup: Executes `create_db_and_tables()` in `database.py`, provisioning the PostgreSQL database, verifying table schemas, seeding static categories and domain keywords, and running backfill classification on unmapped documents.
- On shutdown: Safely releases resources.

### 2. Domain Router Decoupling
The backend avoids monolithic route files by segregating endpoints into domain-specific `APIRouter` instances:
- `Users` (`prefix="/users"`, `tags=["Users"]`): User signup, login, profile retrieval, and user-document ownership traversal.
- `Categories` (`prefix="/categories"`, `tags=["Categories"]`): Read-only category master data lookups and category-document relationship traversal.
- `Documents` (`prefix="/documents"`, `tags=["Documents"]`): Multipart file upload, PDF magic-byte validation, OCR extraction, classification, and binary BLOB streaming downloads.

### 3. Dependency Injection (DI) with Typed Annotations
All database operations use FastAPI's dependency injection system via `get_session()` in `database.py`:
```python
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```
Endpoints declare session dependencies using Python 3.12 type annotations:
```python
session: Annotated[Session, Depends(get_session)]
```
This guarantees automatic session cleanup, transaction rollback on exceptions, and frictionless unit testing via dependency overrides.

### 4. Resilient Database Engine Configuration
The SQLModel/SQLAlchemy engine is initialized with `pool_pre_ping=True`:
```python
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
```
This validates connections before executing queries, automatically reconnecting if a connection in the pool was terminated by PostgreSQL.
