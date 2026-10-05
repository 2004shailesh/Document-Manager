# Features Catalog

This catalog outlines all features identified and verified in the **Document Management System** codebase, categorized by their implementation status.

---

## ✅ Implemented Features

### 1. Document Ingestion & Validation
- **Strict PDF Enforcement**: Accepts only valid PDF documents; immediately rejects files with non-`.pdf` extensions or missing `%PDF` magic bytes.
- **Upload Size Guard**: Rejects uploads exceeding 3 MB (`3,145,728 bytes`) at both the frontend file picker and backend validation layers.
- **Multipart Upload Endpoint**: `POST /documents/` endpoint accepting file binary streams, optional user ownership (`owner_user_id`), and optional explicit category assignments (`category_ids`).

### 2. Dual-Pass Text Extraction & OCR
- **Fast-Path Digital Extraction**: Extracts text instantly from digital vector PDFs via PyMuPDF.
- **Automated OCR Fallback**: Automatically renders scanned or image-only pages to 150 DPI PNG pixmaps and runs OCR inference using `RapidOCR` with ONNX Runtime on CPU.
- **Singleton Engine Reuse**: The OCR engine is cached in memory as a singleton to eliminate per-request ONNX session initialization latency.

### 3. Hybrid Document Classification
- **Multi-Category Assignment**: Assigns multiple categories to a single document if the text matches domain keywords across multiple categories.
- **Hybrid Scoring**: Combines Machine Learning posterior probabilities (TF-IDF + Multinomial Naive Bayes) with exact database keyword density (`category_keyword` table).
- **Core Domain Categories**:
  - `1`: `Invoice` (Receipts, billing, tax, POs, remittances)
  - `2`: `Contracts` (NDAs, MSAs, legal agreements, terms)
  - `3`: `Reports` (Financial statements, audits, executive summaries)
  - `4`: `Notes` (Meeting minutes, memos, action items)
  - `5`: `Medical` (Prescriptions, lab reports, discharge summaries, radiology)
  - `6`: `Others` (Default fallback for unrecognized documents)
- **Automatic Fallback**: Assigns category `Others` when confidence is zero or no domain keywords match.

### 4. User Management & Security
- **User Registration**: `POST /users/` creates user accounts with unique, indexed email validation.
- **Password Hashing**: Uses modern Argon2 password hashing via `pwdlib` (`pwdlib[argon2]`).
- **User Authentication**: `POST /users/login` verifies user email and password hashes.
- **User Profile Operations**: `GET /users/`, `GET /users/{id}`, and partial `PATCH /users/{id}` for name, email, and password updates.

### 5. Document Management & Binary Storage
- **Database BLOB Persistence**: Full PDF binary stored in PostgreSQL `documents.body` (`BYTEA`).
- **Paginated Document Listing**: `GET /documents/` with `offset`, `limit`, and optional `category_id` filtering.
- **Document Detail View**: `GET /documents/{document_id}` returns metadata, extracted text preview, owner details, and associated category summaries.
- **Binary Streaming Download**: `GET /documents/{document_id}/download` streams the original PDF with `Content-Disposition: attachment` headers.
- **Document Metadata Update**: `PATCH /documents/{document_id}` updates document name and re-links categories.

### 6. Database Lifespan & Master Data Synchronization
- **Automatic Database Provisioning**: `ensure_database_exists()` connects to PostgreSQL maintenance database and provisions the target application database if missing.
- **Static Category Resequencing**: `seed_static_categories()` eliminates duplicate category names and normalizes IDs to 1..6.
- **Keyword Seeding**: `seed_category_keywords()` idempotently populates reference domain keywords into `category_keyword`.
- **Automatic Uncategorized Document Backfill**: `backfill_uncategorized_documents()` scans existing unmapped documents, runs OCR if missing, and assigns categories on server boot.

### 7. Frontend User Experience
- **Interactive Dashboard**: Dynamically computes category document counts for the logged-in user, renders themed category cards with emojis, and allows drilling down into documents.
- **4-Way In-Memory Document Sorting**:
  - `Name A → Z` (Alphabetical ascending)
  - `Name Z → A` (Alphabetical descending)
  - `Old to New` (Chronological ascending by `uploaded_at` timestamp)
  - `New to Old` (Chronological descending by `uploaded_at` timestamp)
- **Client-Side Document Caching**: Fetches all user documents on load and executes category filtering and sorting in memory via React `useMemo` for zero-latency UI interactions.
- **Instant Document Download**: One-click download from the dashboard triggering native browser PDF save via direct binary blob streaming.
- **Real-Time Upload Feedback**: Progress indicators during OCR processing and instant display of assigned category pill badges.
- **Client-Side Session State**: Persists user session in `localStorage` and dynamically updates navigation header actions.

---

## 🟡 Partially Implemented Features

### 1. User Session Security
- **Current State**: `POST /users/login` verifies credentials and returns the sanitized `UserPublic` object. The frontend stores this object in `localStorage`.
- **Limitation**: No cryptographically signed JSON Web Tokens (JWT) or secure HTTP-only session cookies are issued. Endpoints do not validate Bearer tokens on subsequent requests.

### 2. Category Management
- **Current State**: Categories are seeded and exposed via read-only GET endpoints (`GET /categories/`, `GET /categories/{id}`, `GET /categories/{id}/documents`).
- **Limitation**: No administrative API endpoints or UI exist to dynamically add, rename, or delete categories at runtime.

---

## ⭕ Planned / TODO Features (Not Implemented)

- **Asynchronous Processing Queue**: Background task queue (e.g., Celery / ARQ / Redis) for processing large batches of multi-page PDFs asynchronously.
- **Cloud Object Storage**: Offloading PDF binaries from PostgreSQL `BYTEA` to AWS S3, MinIO, or Google Cloud Storage.
- **Search & Full-Text Indexing**: Elasticsearch / PostgreSQL Full-Text Search (`tsvector`) across all extracted document text.
- **Role-Based Access Control (RBAC)**: Admin vs. Standard User permissions.
- **Automated Test Suite**: Unit and integration test suites for backend APIs and frontend React components.
