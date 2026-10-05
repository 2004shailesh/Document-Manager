# Running the Project Locally

This guide provides the exact verified commands to run the backend and frontend development servers concurrently.

---

## 🏃 Quick Start Commands

To run the entire system locally, open two terminal windows:

### Terminal 1: Start Backend API Service
From the repository root with virtual environment activated:

```bash
# Activate virtual environment if not active
.venv\Scripts\activate      # Windows
# or: source .venv/bin/activate  # macOS/Linux

# Run Uvicorn development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Alternative backend launch commands:
```bash
# Using python script entrypoint directly
python main.py

# Or using the installed CLI entrypoint (if pip installed in editable mode)
document-server
```

### Terminal 2: Start Frontend Web Application
From the repository root:

```bash
cd frontend
pnpm run dev
# or: npm run dev
```

---

## 🌐 Network Ports & Service URLs

| Service | Protocol / Host | Port | Purpose | Interactive URL |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Web App** | HTTP (`localhost`) | `5173` | React 19 SPA Web Interface | `http://localhost:5173` |
| **Backend API Gateway** | HTTP (`127.0.0.1`) | `8000` | FastAPI REST Endpoints | `http://localhost:8000` |
| **Swagger UI Documentation** | HTTP (`127.0.0.1`) | `8000` | Interactive OpenAPI Testbed | `http://localhost:8000/docs` |
| **ReDoc Documentation** | HTTP (`127.0.0.1`) | `8000` | Clean OpenAPI Specification | `http://localhost:8000/redoc` |
| **Health Check Endpoint** | HTTP (`127.0.0.1`) | `8000` | DB Connectivity & Status | `http://localhost:8000/health` |
| **PostgreSQL Database** | TCP (`localhost`) | `5432` | Relational Storage Engine | `localhost:5432` |

---

## 🩺 Verifying System Health

### 1. Test Backend & Database Connectivity
Run the following curl / PowerShell command:

```bash
# Windows PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

# macOS / Linux (curl)
curl -s http://127.0.0.1:8000/health
```

Expected Response (`HTTP 200 OK`):
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Verify API Root
```bash
curl -s http://127.0.0.1:8000/
```

Expected Response (`HTTP 200 OK`):
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

### 3. Open Frontend UI
Navigate to `http://localhost:5173` in your web browser. You should see the login screen or dashboard.

---

## 🛑 Stopping the Servers

In each terminal window, press `Ctrl + C` to gracefully terminate the Uvicorn server and Vite development server.
