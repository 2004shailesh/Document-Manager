# Environment Security & Configuration Hygiene

This document covers secret management, CORS policy restrictions, and injection protection.

---

## 🔒 Secret Management & Environment Isolation

1. **`.env` Exclusion**:
   - The `.gitignore` file includes `.env` and `.env.local` to prevent committing secrets to source control.
   - Developers configure secrets using `.env.example` as a template.
2. **URL Encoding for Special Characters**:
   - `backend/src/constants/constant.py` uses `urllib.parse.quote_plus` to safely encode passwords with special characters before assembling connection strings.
3. **Hardcoded Fallbacks Remediation**:
   - The codebase currently includes a fallback default password (`Shailesh@123`) in `constant.py`.
   - In production environments, this variable must always be set explicitly via `DB_PASSWORD` or the application should fail on startup.

---

## 🌐 CORS Policy Analysis & Hardening

Currently, `backend/src/api/api.py` configures CORS with open wildcards:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production Hardening Recommendation:
Restrict `allow_origins` to explicitly trusted frontend domain names:

```python
import os

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```
