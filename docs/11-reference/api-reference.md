# OpenAPI Reference Specifications

This document provides complete, OpenAPI-aligned endpoint specifications, request schemas, and sample response payloads.

---

## 🧭 System Endpoints

### `GET /` — API Root & Navigation Guide
- **Summary**: Returns API version and documentation URLs.
- **Auth**: None
- **Response (`200 OK`)**:
  ```json
  {
    "title": "Document Management API",
    "version": "1.0.0",
    "status": "online",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "message": "Welcome to the Document Management API. Explore interactive docs at /docs."
  }
  ```

### `GET /health` — Health Check
- **Summary**: Validates active PostgreSQL database connectivity.
- **Auth**: None
- **Response (`200 OK`)**:
  ```json
  {
    "status": "healthy",
    "database": "connected"
  }
  ```

---

## 👤 Users Endpoints (`/users`)

### `POST /users/` — Register User
- **Summary**: Creates a new user profile with Argon2 password hashing.
- **Request Body (`UserCreate`)**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (`201 Created`) (`UserPublic`)**:
  ```json
  {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
  }
  ```
- **Errors**: `409 Conflict` if email already exists.

### `POST /users/login` — User Login
- **Summary**: Verifies user credentials against hashed password.
- **Request Body (`UserLogin`)**:
  ```json
  {
    "email": "jane.doe@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (`200 OK`) (`UserPublic`)**:
  ```json
  {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
  }
  ```
- **Errors**: `401 Unauthorized` if email/password is invalid.

### `GET /users/{user_id}/documents` — User Document Summaries
- **Summary**: Lists all documents owned by user with category IDs and category names.
- **Parameters**: `user_id` (Path, integer)
- **Response (`200 OK`) (`list[UserDocumentSummary]`)**:
  ```json
  [
    {
      "id": 5,
      "name": "hospital_bill.pdf",
      "size_bytes": 84520,
      "extracted_text": "Medical Bill Patient Name...",
      "uploaded_at": "2026-09-25T08:00:00Z",
      "category_ids": [1, 5],
      "categories": ["Invoice", "Medical"]
    }
  ]
  ```

---

## 📑 Documents Endpoints (`/documents`)

### `POST /documents/` — Upload PDF Document
- **Summary**: Ingests, validates, extracts text, classifies, and stores a PDF file.
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: `UploadFile` (.pdf, max 3MB)
  - `owner_user_id`: `int` (Optional)
  - `category_ids`: `list[str]` (Optional)
- **Response (`201 Created`) (`DocumentDetailPublic`)**:
  ```json
  {
    "id": 10,
    "name": "lease_agreement.pdf",
    "size_bytes": 145000,
    "extracted_text": "COMMERCIAL LEASE AGREEMENT...",
    "uploaded_at": "2026-09-25T08:30:00Z",
    "owner_user_id": 1,
    "categories": [
      { "id": 2, "name": "Contracts" }
    ],
    "predicted_category": "Contracts",
    "prediction_confidence": 0.85,
    "matched_keywords": ["agreement", "lease", "covenants"]
  }
  ```

### `GET /documents/{document_id}/download` — Stream PDF BLOB
- **Summary**: Downloads the binary PDF stream.
- **Headers**: `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="..."`
- **Response (`200 OK`)**: Raw binary stream.
