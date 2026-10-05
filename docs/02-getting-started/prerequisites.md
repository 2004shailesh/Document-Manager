# Prerequisites & System Requirements

Before setting up the **Document Management System** on a clean workstation, ensure your machine satisfies the required software, runtime, and tool versions.

---

## 💻 Hardware & Operating System Requirements

| Specification | Minimum Requirement | Recommended |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS 12+, or Ubuntu 22.04 LTS | Any modern 64-bit OS |
| **Processor (CPU)** | Dual-Core 2.0 GHz (x86_64 or ARM64) | Quad-Core 2.5 GHz+ (for fast OCR ONNX inference) |
| **Memory (RAM)** | 4 GB | 8 GB+ (OCR model loading & Python/Node dev servers) |
| **Disk Space** | 2 GB free disk space | 5 GB+ (for Node modules, Python venv, and OCR models) |

---

## 🛠️ Required Software & Runtime Tools

### 1. Python `>= 3.12`
- **Required Version**: Python `3.12.0` or higher (verified on Python 3.12.3).
- **Verification Command**:
  ```bash
  python --version
  # Output should show: Python 3.12.x
  ```
- **Virtual Environment Tool**: Standard library `venv` module.

### 2. Node.js & pnpm / npm
- **Required Version**: Node.js `18.0.0` or higher (Node 20+ LTS recommended).
- **Package Manager**: `pnpm` (version `^9.0` recommended) or standard `npm`.
- **Verification Commands**:
  ```bash
  node --version
  pnpm --version
  # or
  npm --version
  ```

### 3. PostgreSQL Database `>= 14`
- **Required Version**: PostgreSQL version 14, 15, 16, or 17.
- **Port**: Default port `5432`.
- **Default Database**: A maintenance database (typically `postgres`) must exist to allow the backend to auto-provision the application database.
- **Verification Command**:
  ```bash
  psql --version
  ```

### 4. Git
- **Required Version**: Git 2.30+.
- **Verification Command**:
  ```bash
  git --version
  ```

---

## 📦 System Dependencies & Build Tools Note

- **PyMuPDF & RapidOCR**: These Python packages include pre-compiled binary wheels for Windows, macOS, and Linux. No external C++ compilers or Tesseract system binaries are required.
- **RapidOCR ONNX Runtime**: Uses `onnxruntime` on CPU by default. No CUDA/GPU drivers are required for local development.
