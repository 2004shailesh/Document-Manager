# Environment Configuration Setup

The **Document Management System** follows 12-Factor App principles by reading its runtime configuration from environment variables with safe development defaults.

---

## 📄 Configuration Template (`.env.example`)

A sample template is provided at the repository root: `.env.example`.

To set up your local environment, copy `.env.example` to `.env`:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

---

## ⚙️ Environment Variables Reference

| Variable Name | Required | Default in Code | Purpose | Safe Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `DB_HOST` | No | `localhost` | Hostname or IP address of the PostgreSQL server | `localhost` or `127.0.0.1` |
| `DB_PORT` | No | `5432` | Port number of the PostgreSQL service | `5432` |
| `DB_USER` | No | `postgres` | Database superuser or application role username | `postgres` |
| `DB_PASSWORD` | **Yes (Prod)** | `Shailesh@123` | Password for PostgreSQL authentication | `your_secure_password_here` |
| `DB_NAME` | No | `Document` | Name of the primary application database | `Document` |
| `DEFAULT_DB` | No | `postgres` | Maintenance database used for auto-provisioning | `postgres` |

---

## 🔐 Connection String Assembly

The application reads these variables in `backend/src/constants/constant.py` and dynamically constructs the SQLAlchemy/SQLModel connection string:

```python
# Encodes special characters in passwords (such as '@', ':', '/') to ensure safe URL parsing
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
```

---

## 🔒 Security Best Practices

1. **Never Commit `.env` to Version Control**: The `.gitignore` file is configured to exclude `.env` files.
2. **Special Characters in Passwords**: If your database password contains characters like `@`, `#`, or `/`, the application automatically encodes them using `urllib.parse.quote_plus()`.
3. **Frontend API URL**: In local development, the React frontend connects directly to `http://localhost:8000`. (See [`docs/DOCUMENTATION_ISSUES.md`](file:///c:/Users/shail/OneDrive/Desktop/project/docs/DOCUMENTATION_ISSUES.md) regarding extracting this to Vite environment variables).
