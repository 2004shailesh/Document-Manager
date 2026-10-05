# Local Setup & Runtime Troubleshooting

This guide contains verified resolutions for common setup, database, OCR, and networking issues.

---

## ⚠️ Common Issues & Solutions

### 1. Backend Fails to Start: "Database provisioning error: FATAL: password authentication failed"
- **Cause**: The password specified in `.env` or `backend/src/constants/constant.py` (`DB_PASSWORD`) does not match the actual password for the `postgres` user in your local PostgreSQL installation.
- **Solution**:
  1. Open `.env` and update `DB_PASSWORD` to your actual PostgreSQL password.
  2. If you forgot your local PostgreSQL password, alter it via `psql`:
     ```sql
     ALTER USER postgres WITH PASSWORD 'your_new_password';
     ```
  3. Re-launch `uvicorn main:app --reload`.

---

### 2. Backend Fails to Start: "ConnectionRefusedError: [Errno 111] Connect call failed"
- **Cause**: The PostgreSQL service is stopped or listening on a non-standard port.
- **Solution**:
  - Check if PostgreSQL service is running:
    ```powershell
    # Windows
    Get-Service -Name postgresql*
    Start-Service -Name postgresql-x64-16
    ```
  - Verify that `DB_PORT=5432` and `DB_HOST=localhost` in `.env`.

---

### 3. Port Already in Use: "ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)"
- **Cause**: Another instance of Uvicorn or another application is occupying port `8000`.
- **Solution**:
  - Identify and terminate the occupying process:
    ```powershell
    # Windows (PowerShell)
    Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
    ```
    ```bash
    # macOS / Linux
    lsof -ti:8000 | xargs kill -9
    ```

---

### 4. Frontend Shows "Cannot connect to server" on Login / Register / Upload
- **Cause**: The backend FastAPI server is either not running or running on a port other than `8000`.
- **Solution**:
  1. Ensure `uvicorn main:app --reload --host 127.0.0.1 --port 8000` is active in your backend terminal.
  2. Verify that `http://127.0.0.1:8000/health` returns `{"status": "healthy"}` in your browser.

---

### 5. Document Upload Returns: "Selected file is incorrect. Only PDF files (.pdf) are allowed"
- **Cause**: The uploaded file either does not end with `.pdf` or is missing the `%PDF` binary header (e.g., a text or image file renamed to `.pdf`).
- **Solution**:
  - Upload a genuine PDF document created by a PDF generator or scanner.

---

### 6. Document Upload Returns: "File size exceeds the maximum allowed limit of 3 MB"
- **Cause**: The file exceeds the hard constraint `MAX_FILE_SIZE_MB = 3` (`3,145,728 bytes`).
- **Solution**:
  - Compress the PDF or upload a smaller test PDF file under 3 MB.

---

### 7. ModuleNotFoundError: No module named 'src'
- **Cause**: Running Uvicorn from an arbitrary subfolder without the project root in `sys.path`.
- **Solution**:
  - Always run `uvicorn main:app --reload` from the **project root directory** (where `main.py` resides), or run `python main.py`. `main.py` automatically injects the root directory and `backend/` into Python's `sys.path`.
