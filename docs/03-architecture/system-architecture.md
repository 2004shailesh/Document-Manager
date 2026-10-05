# System Architecture

This document presents the high-level architecture, subsystem boundaries, data storage patterns, and inter-service communications of the **Document Management System**.

---

## 🏛️ System Block Architecture

```mermaid
flowchart TB
    subgraph PresentationTier["1. Presentation Tier (Client)"]
        Browser["Web Browser (User Interface)"]
        SPA["React 19 SPA (Vite + TypeScript)"]
        SessionStore["Client Session State (localStorage)"]
        Browser --> SPA
        SPA <--> SessionStore
    end

    subgraph APITier["2. API Gateway & Routing Tier (FastAPI)"]
        FastAPIApp["FastAPI Central App (api.py)"]
        Lifespan["Lifespan Startup / Shutdown Handler"]
        CORS["CORS Middleware (*)"]
        
        subgraph DomainRouters["Domain APIRouters"]
            UsersRouter["Users Router (/users)"]
            CategoriesRouter["Categories Router (/categories)"]
            DocumentsRouter["Documents Router (/documents)"]
        end
    end

    subgraph ServiceTier["3. Business Logic & Processing Tier"]
        AuthService["Password Hashing Engine (pwdlib / Argon2)"]
        
        subgraph Pipeline["Document Processing Pipeline"]
            Validator["Defense-in-Depth PDF Validator (contents.py)"]
            PyMuPDF["PyMuPDF Dual-Pass Extractor"]
            RapidOCR["RapidOCR ONNX Inference Engine (Singleton)"]
            Categorizer["Hybrid ML & Keyword Categorizer (categorizer.py)"]
        end
    end

    subgraph DataTier["4. Persistence Tier (PostgreSQL)"]
        SQLModelEngine["SQLModel Engine (pool_pre_ping=True)"]
        
        subgraph Tables["PostgreSQL Tables"]
            T_Users[("users")]
            T_Documents[("documents (BYTEA)")]
            T_Categories[("categories (1..6)")]
            T_DocCats[("document_categories")]
            T_UserDocs[("user_document")]
            T_CatKeywords[("category_keyword")]
        end
    end

    SPA -- "HTTP / REST (JSON & Multipart)" --> FastAPIApp
    FastAPIApp --> CORS
    FastAPIApp --> Lifespan
    FastAPIApp --> DomainRouters

    UsersRouter --> AuthService
    UsersRouter --> SQLModelEngine

    CategoriesRouter --> SQLModelEngine

    DocumentsRouter --> Validator
    Validator --> PyMuPDF
    PyMuPDF -- "Digital Text (Fast Path)" --> Categorizer
    PyMuPDF -- "Scanned PDF Fallback (150 DPI Pixmap)" --> RapidOCR
    RapidOCR --> Categorizer
    Categorizer <--> SQLModelEngine
    DocumentsRouter --> SQLModelEngine

    Lifespan --> SQLModelEngine
    SQLModelEngine --> Tables
```

---

## 🧩 Architectural Subsystems & Boundaries

### 1. Presentation Tier
- Implemented as a Single Page Application (SPA) using React 19 and TypeScript.
- Built using Vite, compiled to static HTML/JS/CSS assets.
- Manages view rendering, client-side routing via React Router DOM v7, and asynchronous HTTP calls using standard browser `fetch()`.

### 2. API Gateway & Routing Tier
- Implemented in FastAPI (`backend/src/api/api.py`).
- Manages HTTP connection lifecycles, parses incoming multipart/form-data payloads, serializes outgoing DTO responses, and executes dependency injection for database sessions.
- Domain routers are cleanly isolated by resource:
  - `Users` (`backend/src/api/users.py`)
  - `Categories` (`backend/src/api/categories.py`)
  - `Documents` (`backend/src/api/document.py`)

### 3. Processing & Machine Learning Tier
- **Validation Engine**: Guarantees that only valid PDF byte streams under 3 MB enter the system.
- **Dual-Pass Extraction Engine**: Uses PyMuPDF for zero-overhead vector text extraction, seamlessly switching to RapidOCR ONNX inference on rasterized 150 DPI page pixmaps when digital text is absent.
- **Classification Engine**: Combines a trained TF-IDF + Multinomial Naive Bayes pipeline with live PostgreSQL keyword dictionary boosting.

### 4. Relational Persistence Tier
- Managed via PostgreSQL and SQLModel.
- Stores user accounts, category metadata, domain keywords, junction associations, extracted OCR text, and the raw binary document payloads.
