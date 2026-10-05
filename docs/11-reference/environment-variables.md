# Environment Variables Reference

This document provides a reference of all environment variables referenced throughout the codebase.

---

## 📋 Environment Variables Table

| Variable Name | Required | Default in Code | Purpose | Expected Type | Safe Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DB_HOST` | No | `localhost` | Hostname or IP address of the PostgreSQL server | `string` | `localhost` or `postgres-host` |
| `DB_PORT` | No | `5432` | Port number of PostgreSQL service | `string` / `int` | `5432` |
| `DB_USER` | No | `postgres` | Database username | `string` | `postgres` or `app_user` |
| `DB_PASSWORD` | **Yes (Prod)** | `Shailesh@123` | Password for PostgreSQL authentication | `string` | `your_secure_password_here` |
| `DB_NAME` | No | `Document` | Application database name | `string` | `Document` or `doc_manager_prod` |
| `DEFAULT_DB` | No | `postgres` | Maintenance DB for auto-provisioning | `string` | `postgres` |

---

## ⚙️ Application-Level Constants Reference

Defined in `backend/src/constants/constant.py`:

| Constant Name | Value | Purpose |
| :--- | :--- | :--- |
| `MAX_FILE_SIZE_MB` | `3` | Maximum allowed file upload size in megabytes |
| `MAX_FILE_SIZE_BYTES` | `3,145,728` | Calculated byte limit ($3 \times 1024 \times 1024$) |
| `ML_CONFIDENCE_THRESHOLD` | `0.50` | Minimum confidence threshold for classification |
| `MAX_MATCHED_KEYWORDS` | `10` | Maximum number of matched keyword strings returned in DTOs |
| `PDF_MAGIC_SIGNATURE` | `b"%PDF"` | Binary header signature for PDF verification |
