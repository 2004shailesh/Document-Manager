# Linting & Code Formatting Guide

This document details the configuration, CLI commands, and automated enforcement for code linters and formatters in the repository.

---

## 🛠️ Tool Configuration Matrix

| Tool | Domain | Configuration File | Key Settings |
| :--- | :--- | :--- | :--- |
| **Black** | Python Formatter | `pyproject.toml` (`[tool.black]`) | `line-length = 100`, `target-version = ["py312"]` |
| **isort** | Python Import Sorter | `pyproject.toml` (`[tool.isort]`) | `profile = "black"`, `line_length = 100`, `known_first_party = ["src"]` |
| **mypy** | Python Type Checker | `pyproject.toml` (`[tool.mypy]`) | `python_version = "3.12"`, `pydantic.mypy` plugin enabled |
| **ESLint 10** | TypeScript / React Linter | `frontend/eslint.config.js` | `@eslint/js`, `typescript-eslint`, React Hooks rules |
| **Prettier** | Frontend Formatter | `frontend/.prettierrc` | `semi: true`, `singleQuote: true`, `tabWidth: 2`, `printWidth: 100` |

---

## 🐍 Backend Linting & Formatting Commands

### 1. Format Code with Black
```bash
black backend main.py
```

### 2. Sort Imports with isort
```bash
isort backend main.py
```

### 3. Run Static Type Analysis with mypy
```bash
mypy backend
```

---

## ⚛️ Frontend Linting & Formatting Commands

From the `frontend/` directory:

### 1. Run ESLint Linter
```bash
pnpm run lint
```

### 2. Auto-Fix ESLint Errors
```bash
pnpm run lint:fix
```

### 3. Format Source Files with Prettier
```bash
pnpm run format
```

### 4. Check Formatting without Modifying Files
```bash
pnpm run format:check
```

---

## 💻 VS Code Auto-Formatting Configuration

Configured in `.vscode/settings.json`:
- `editor.formatOnSave: true`
- `editor.defaultFormatter: esbenp.prettier-vscode` (for `.ts`, `.tsx`, `.json`)
- `editor.defaultFormatter: ms-python.black-formatter` (for `.py`)
- Python extraPaths: `["./backend"]` to support autocomplete and path discovery.
