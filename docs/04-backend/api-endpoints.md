# API Endpoints Catalog

This document provides an exhaustive reference of all REST API endpoints exposed by the FastAPI backend service.

---

## 🧭 Endpoints Overview Table

| Method | Path | Summary | Auth Required | Request Body / Params | Response |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API Root & Navigation Guide | None | None | `dict[str, str]` |
| `GET` | `/health` | DB Connectivity Health Check | None | None | `dict[str, str]` |
| `POST` | `/users/` | Register a new user | None | `UserCreate` (JSON) | `UserPublic` (`201 Created`) |
| `POST` | `/users/login` | Authenticate user credentials | None | `UserLogin` (JSON) | `UserPublic` (`200 OK`) |
| `GET` | `/users/` | List all users (paginated) | None | `offset`, `limit` (Query) | `list[UserPublic]` |
| `GET` | `/users/{user_id}` | Get user details by ID | None | `user_id` (Path) | `UserPublic` |
| `PATCH` | `/users/{user_id}` | Partially update user info | None | `user_id` (Path), `UserUpdate` (JSON) | `UserPublic` |
| `GET` | `/users/{user_id}/documents` | Get all documents owned by user | None | `user_id` (Path) | `list[UserDocumentSummary]` |
| `GET` | `/categories/` | List all static categories | None | `offset`, `limit` (Query) | `list[CategoryPublic]` |
| `GET` | `/categories/{category_id}` | Get category by ID | None | `category_id` (Path) | `CategoryPublic` |
| `GET` | `/categories/{category_id}/documents` | Get all documents in a category | None | `category_id` (Path) | `list[CategoryDocumentSummary]` |
| `POST` | `/documents/` | Upload PDF with OCR & classification | None | `file` (File), `owner_user_id`, `category_ids` (Form) | `DocumentDetailPublic` (`201 Created`) |
| `GET` | `/documents/` | List documents (with filters) | None | `offset`, `limit`, `category_id` (Query) | `list[DocumentPublic]` |
| `GET` | `/documents/{document_id}` | Get document details by ID | None | `document_id` (Path) | `DocumentDetailPublic` |
| `GET` | `/documents/{document_id}/download` | Download original binary PDF | None | `document_id` (Path) | `application/pdf` binary stream |
| `PATCH` | `/documents/{document_id}` | Update document name or categories | None | `document_id` (Path), `DocumentUpdate` (JSON) | `DocumentDetailPublic` |

---

## 📖 Endpoint Deep-Dives

### 1. `POST /documents/` — Upload PDF Document
- **Purpose**: Ingests, validates, extracts text (OCR if scanned), classifies, and persists a PDF document.
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: `UploadFile` (Required) — PDF binary payload (max 3 MB).
  - `owner_user_id`: `int | None` (Optional Form field) — User ID to assign ownership.
  - `category_ids`: `list[str] | None` (Optional Form field) — Explicit category names or IDs.
- **Success Response (`HTTP 201 Created`)**:
  ```json
  {
    "id": 14,
    "name": "tax_invoice_2024.pdf",
    "size_bytes": 108420,
    "extracted_text": "TAX INVOICE #INV-9921\nSubtotal: $4,500.00\nTotal Due: $5,310.00",
    "uploaded_at": "2026-09-25T07:15:30.123456Z",
    "owner_user_id": 1,
    "categories": [
      { "id": 1, "name": "Invoice" }
    ],
    "predicted_category": "Invoice",
    "prediction_confidence": 0.85,
    "matched_keywords": ["tax invoice", "subtotal", "total due", "invoice"]
  }
  ```
- **Errors**:
  - `HTTP 400 Bad Request`: File not PDF, missing `%PDF` magic bytes, or file exceeds 3 MB limit.
  - `HTTP 404 Not Found`: `owner_user_id` or explicit `category_ids` not found.

---

### 2. `GET /documents/{document_id}/download` — Stream PDF BLOB
- **Purpose**: Streams the raw binary PDF BLOB stored in the database directly to the client browser for download.
- **Headers Returned**:
  - `Content-Type`: `application/pdf`
  - `Content-Disposition`: `attachment; filename="tax_invoice_2024.pdf"`
  - `Content-Length`: `<byte_count>`
- **Errors**: `HTTP 404 Not Found` if `document_id` does not exist.

---

### 3. `POST /users/login` — User Authentication
- **Purpose**: Verifies email and Argon2 password hash.
- **Request Body (`UserLogin`)**:
  ```json
  {
    "email": "analyst@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Success Response (`HTTP 200 OK`)**:
  ```json
  {
    "id": 1,
    "name": "Alex Mercer",
    "email": "analyst@example.com"
  }
  ```
- **Errors**: `HTTP 401 Unauthorized` on invalid email or password.

---

### 4. `GET /users/{user_id}/documents` — User Documents List
- **Purpose**: Retrieves all documents associated with a user, including their assigned category IDs and names.
- **Success Response (`HTTP 200 OK`)**:
  ```json
  [
    {
      "id": 14,
      "name": "tax_invoice_2024.pdf",
      "size_bytes": 108420,
      "extracted_text": "TAX INVOICE #INV-9921...",
      "uploaded_at": "2026-09-25T07:15:30.123456Z",
      "category_ids": [1],
      "categories": ["Invoice"]
    }
  ]
  ```
