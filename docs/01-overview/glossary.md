# Glossary of Terms

This glossary defines technical terms, domain concepts, and abbreviations used throughout the codebase and documentation.

---

## 📖 Terms & Definitions

### A
- **API (Application Programming Interface)**: The set of HTTP REST endpoints provided by FastAPI for client-server communication.
- **Argon2**: The password-hashing algorithm implemented via `pwdlib` (`pwdlib[argon2]`), designed to resist GPU/ASIC cracking attacks.
- **ASGI (Asynchronous Server Gateway Interface)**: The Python specification for asynchronous web servers and frameworks; Uvicorn serves the application as an ASGI runner.

### B
- **Backfill**: The automatic startup process (`backfill_uncategorized_documents`) that scans existing documents without category associations, runs OCR if needed, and links them to categories.
- **BLOB (Binary Large Object)**: Raw binary file data (PDF payload) stored directly inside the PostgreSQL `documents.body` column (`BYTEA` data type).

### C
- **Category**: A high-level document classification domain entity (`Invoice`, `Contracts`, `Reports`, `Notes`, `Medical`, `Others`).
- **Category Keyword**: A reference domain word or phrase stored in the `category_keyword` table used by the categorization engine to calculate category match density.
- **CORS (Cross-Origin Resource Sharing)**: HTTP headers that allow web browsers running on `http://localhost:5173` to make API calls to `http://localhost:8000`.

### D
- **Defense-in-Depth**: A security design principle where multiple layers of validation (file size check, file extension check, and binary magic-byte inspection) verify an upload.
- **DTO (Data Transfer Object)**: A Pydantic / SQLModel schema (`UserCreate`, `UserPublic`, `DocumentDetailPublic`) defining the shape of request and response payloads.
- **Dual-Pass Extraction**: The extraction architecture that extracts vector text first via PyMuPDF and falls back to OCR on rendered page pixmaps only when no text is found.

### J
- **Junction Table**: An intermediate relational table (`document_categories`, `user_document`) that models relationships between entities using composite foreign primary keys.

### M
- **Magic Bytes**: The byte sequence `b"%PDF"` located in the first 1024 bytes of a PDF file, used to identify legitimate PDF binary streams.
- **Multinomial Naive Bayes (MultinomialNB)**: A probabilistic supervised learning classifier suited for text classification with discrete word frequency features.

### O
- **OCR (Optical Character Recognition)**: The process of converting rasterized pixel images of printed or handwritten text into machine-readable character strings.
- **ONNX Runtime**: The cross-platform inference engine used by `RapidOCR` to execute deep-learning OCR models on CPU.

### P
- **Pixmap**: A raster image representation of a rendered PDF page generated at 150 DPI by PyMuPDF before being processed by RapidOCR.
- **PyMuPDF**: The Python binding for the MuPDF C library used for PDF stream parsing, vector text extraction, and page rasterization.

### R
- **RapidOCR**: An efficient ONNX-based text detector and recognizer optimized for CPU inference without external binary dependencies.

### S
- **SQLModel**: A Python ORM library designed by Tiangolo that unifies SQLAlchemy ORM models with Pydantic validation models.
- **Strict Mode**: A React 19 development mode tool for highlighting potential component side-effects during render cycles.

### T
- **TF-IDF (Term Frequency-Inverse Document Frequency)**: A numerical statistic reflecting how important a word is to a document relative to a corpus.
