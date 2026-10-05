# Security Architecture & Defense Posture

This document provides a documentation-level security assessment of the **Document Management System**, detailing existing defense controls, implementation statuses, and prioritized security recommendations.

---

## 🛡️ Security Controls & Implementation Matrix

| Security Domain | Control Mechanism | Implementation Status | Codebase Verification Source |
| :--- | :--- | :--- | :--- |
| **File Ingestion** | Magic-Byte (%PDF) Verification | **Implemented** | `backend/src/model/contents.py` (Line 88) |
| **File Ingestion** | Upload Size Guard (3 MB) | **Implemented** | `backend/src/constants/constant.py`, `contents.py`, `upload.tsx` |
| **File Ingestion** | Case-Insensitive Extension Check | **Implemented** | `backend/src/model/contents.py` (Line 79) |
| **Credential Security** | Argon2 Password Hashing | **Implemented** | `backend/src/api/security.py`, `backend/src/api/users.py` |
| **Data Exposure** | Password Exclusion in DTOs | **Implemented** | `UserPublic` in `backend/src/api/users.py` |
| **SQL Injection** | Parameterized SQL Queries | **Implemented** | SQLModel / SQLAlchemy parameterized statements |
| **Cross-Origin Requests**| CORS Configuration | **Partially Implemented** | `backend/src/api/api.py` (Permissive wildcard `*` active) |
| **Session Security** | Stateless Bearer Token / JWT | **Not Implemented** | Authenticated user stored in client `localStorage` |
| **Rate Limiting** | Endpoint Request Throttling | **Not Implemented** | No rate-limiting middleware configured |

---

## 🔍 Detailed Security Controls

### 1. Defense-in-Depth File Validation
The backend enforces a 4-tier validation pipeline before allowing any uploaded file stream to reach PyMuPDF or the OCR engine:
1. **Empty Payload Check**: Rejects 0-byte uploads.
2. **Size Enforcement**: Rejects any file payload $> 3,145,728$ bytes (3 MB).
3. **Extension Inspection**: Ensures the file ends with `.pdf`.
4. **Binary Signature Verification**: Inspects the first 1024 bytes of the binary stream for the `%PDF` magic byte header.

### 2. Modern Password Hashing
Passwords submitted during registration or profile updates are hashed using **Argon2** via `pwdlib[argon2]`. Plaintext passwords are never persisted to the database and are omitted from all public response schemas.

### 3. SQL Injection Immunity
All database interactions in `database.py`, `users.py`, `document.py`, and `categories.py` utilize SQLModel / SQLAlchemy query builders with automatic parameter binding. Raw driver executions in `seed_static_categories()` use parameterized query dictionaries (e.g. `{"name": cat_name}`).
