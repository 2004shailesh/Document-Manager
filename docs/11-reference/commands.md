# CLI Commands Reference

This reference sheet contains every verified command for installation, local development, database operations, testing, formatting, and production execution.

---

## 💻 Backend Commands

### Virtual Environment & Installation
```bash
# Create virtual environment (Python 3.12)
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# Upgrade pip and packaging tools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install editable package with dev tools
pip install -e .[dev]
```

### Running Development Server
```bash
# Standard Uvicorn development server with hot-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Using python wrapper script
python main.py

# Using CLI script entrypoint
document-server
```

### Code Quality & Static Analysis
```bash
# Format Python code with Black
black backend main.py

# Sort Python imports with isort
isort backend main.py

# Run static type checking with mypy
mypy backend
```

---

## ⚛️ Frontend Commands

From the `frontend/` directory:

### Dependencies & Development
```bash
# Install dependencies using pnpm
pnpm install

# Start Vite development server
pnpm run dev

# Preview local production build
pnpm run preview
```

### Code Quality & Production Build
```bash
# Run ESLint linter
pnpm run lint

# Auto-fix ESLint issues
pnpm run lint:fix

# Format code with Prettier
pnpm run format

# Verify code formatting without writes
pnpm run format:check

# Run TypeScript type-check and compile production bundle into dist/
pnpm run build
```

---

## 🗄️ Database Commands (PostgreSQL)

```bash
# Connect to PostgreSQL maintenance database
psql -U postgres -h localhost

# Connect to target Document database
psql -U postgres -h localhost -d Document

# List all tables in Document database
psql -U postgres -h localhost -d Document -c "\dt"

# Query seeded categories
psql -U postgres -h localhost -d Document -c "SELECT id, name FROM categories ORDER BY id;"

# Create database backup
pg_dump -h localhost -p 5432 -U postgres -d Document -F c -b -v -f "document_backup.dump"

# Restore database from backup
pg_restore -h localhost -p 5432 -U postgres -d Document_Restored -v "document_backup.dump"
```
