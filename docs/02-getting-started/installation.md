# Installation Guide

Follow these step-by-step instructions to clone the repository and install all required backend and frontend dependencies on your local machine.

---

## 📥 Step 1: Clone the Repository

```bash
git clone <repository-url> project
cd project
```

---

## 🐍 Step 2: Backend Environment Setup & Package Installation

### 1. Create a Python Virtual Environment
Using Python 3.12:

```bash
# Windows (PowerShell or Command Prompt)
python -m venv .venv

# macOS / Linux
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux (Bash / Zsh)
source .venv/bin/activate
```

### 3. Upgrade pip and Build Tools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install Backend Dependencies

You can install dependencies using either the standard requirements file or in editable developer mode:

#### Option A: Install via requirements.txt (Production Pinned)
```bash
pip install -r requirements.txt
```

#### Option B: Install via pyproject.toml (Editable Mode with Dev Tools)
```bash
pip install -e .[dev]
```

This installs all core dependencies (`fastapi`, `uvicorn`, `sqlmodel`, `psycopg2-binary`, `pymupdf`, `rapidocr-onnxruntime`, `python-multipart`, `Pillow`, `pwdlib[argon2]`, `scikit-learn`, `joblib`) along with development linters (`black`, `isort`, `mypy`).

---

## ⚛️ Step 3: Frontend Package Installation

### 1. Navigate to the Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies using pnpm or npm

#### Using pnpm (Recommended):
```bash
pnpm install
```

#### Or using npm:
```bash
npm install
```

This installs all client dependencies (`react`, `react-dom`, `react-router-dom`) and development plugins (`vite`, `@vitejs/plugin-react`, `eslint`, `prettier`, `typescript`).

### 3. Return to Project Root

```bash
cd ..
```

---

## 🔍 Step 4: Verification of Installed Packages

Verify that both environments are properly configured:

```bash
# Verify Python packages
python -c "import fastapi, sqlmodel, pymupdf, rapidocr_onnxruntime, sklearn; print('Backend dependencies successfully verified!')"

# Verify Frontend build tools
cd frontend && pnpm run format:check && cd ..
```
