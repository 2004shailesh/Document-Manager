# Testing Strategy & Guidelines

This document outlines the testing architecture, current testing status, and recommendations for implementing comprehensive backend and frontend test suites.

---

## 📊 Current Testing Status

- **Backend**: The `.pytest_cache` directory exists in the project root, confirming pytest compatibility in the environment. However, no automated unit or integration tests (`tests/` directory or `test_*.py` files) are currently committed in the repository.
- **Frontend**: No test framework (such as Vitest or Jest) is currently configured in `frontend/package.json`.

---

## 🧪 Recommended Backend Testing Suite (Pytest)

### 1. Recommended Dependencies
Add to `[project.optional-dependencies] dev` in `pyproject.toml`:
```toml
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
]
```

### 2. Proposed Test Suite Structure
```text
backend/tests/
├── conftest.py                   # Test fixtures (in-memory SQLite / PostgreSQL test DB, TestClient)
├── test_pdf_validation.py        # Magic-byte validation, extension checking & 3MB size guards
├── test_ocr_extraction.py        # PyMuPDF vector text extraction and RapidOCR image fallback
├── test_categorizer.py           # ML classification pipeline, keyword hits & 'Others' fallback
├── test_api_users.py             # User registration, Argon2 password verification & login
└── test_api_documents.py         # Multipart PDF upload, listing filters & binary BLOB streaming
```

### 3. Example Test Case: PDF Validation
```python
import pytest
from src.model.contents import InvalidFileTypeError, validate_pdf_file


def test_validate_pdf_rejects_empty():
    with pytest.raises(InvalidFileTypeError, match="Uploaded file is empty"):
        validate_pdf_file(b"", "sample.pdf")


def test_validate_pdf_rejects_non_pdf_extension():
    with pytest.raises(InvalidFileTypeError, match="Only PDF files"):
        validate_pdf_file(b"%PDF-1.4 test data", "sample.png")


def test_validate_pdf_rejects_missing_magic_bytes():
    with pytest.raises(InvalidFileTypeError, match="not a valid PDF document"):
        validate_pdf_file(b"NOT A REAL PDF HEADER", "sample.pdf")


def test_validate_pdf_accepts_valid_stream():
    # Should not raise exception
    validate_pdf_file(b"%PDF-1.7\nSample binary content", "invoice.pdf")
```

---

## 🧪 Recommended Frontend Testing Suite (Vitest)

### Recommended Setup:
```bash
cd frontend
pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

Add script to `package.json`:
```json
"test": "vitest run",
"test:watch": "vitest"
```
