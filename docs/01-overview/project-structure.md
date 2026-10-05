# Project Structure

This document describes the physical repository layout, explaining the purpose and responsibilities of every significant directory and file.

---

## 📂 Repository Directory Tree

```text
project/
├── .env.example                          # Environment variable configuration template
├── .gitignore                            # Git ignore patterns for Python, virtual environments, node_modules
├── main.py                               # Root wrapper entrypoint for running `uvicorn main:app --reload`
├── pyproject.toml                        # PEP 517/518/621 project metadata, dependencies & tool configs
├── requirements.in                       # Direct unpinned runtime dependencies
├── requirements.txt                      # Pinned production dependency lockfile
│
├── .vscode/                              # VS Code editor preferences
│   └── settings.json                     # Auto-format on save, extraPaths for backend, ESLint/Prettier setup
│
├── backend/                              # Backend Python package source
│   └── src/
│       ├── __init__.py                   # Marks backend source as importable package
│       ├── api/                          # REST API route handlers, DTOs & application entrypoint
│       │   ├── __init__.py               # API package initialization
│       │   ├── api.py                    # Central FastAPI application, lifespan context & router aggregation
│       │   ├── categories.py             # Read-only Category endpoints & Many-to-Many traversal
│       │   ├── document.py               # Document upload, PDF validation, download & CRUD endpoints
│       │   ├── security.py               # Password hashing singleton configuration (`pwdlib`)
│       │   └── users.py                  # User registration, login, profile & ownership endpoints
│       │
│       ├── constants/                    # Application-wide constants & environment variable ingestion
│       │   ├── __init__.py               # Constants package initialization
│       │   └── constant.py               # DB connection URL assembly, file size limits & ML thresholds
│       │
│       ├── data/                         # Data layer, database connection & SQLModel schema definitions
│       │   ├── __init__.py               # Data package initialization
│       │   └── database.py               # Engine creation, DB auto-provisioning, SQLModel models & seeders
│       │
│       └── model/                        # Document processing, OCR text extraction & ML classification
│           ├── __init__.py               # Model package initialization
│           ├── categorizer.py            # TF-IDF + Naive Bayes pipeline, keyword boosting & scoring
│           └── contents.py               # PDF validation, PyMuPDF digital extraction & RapidOCR engine
│
├── frontend/                             # Frontend React 19 Single Page Application
│   ├── .gitignore                        # Frontend-specific Git ignore rules (dist, node_modules)
│   ├── .npmrc                            # npm / pnpm configuration options
│   ├── .prettierignore                   # Files excluded from Prettier formatting
│   ├── .prettierrc                       # Prettier configuration rules (semi, singleQuote, tabWidth)
│   ├── eslint.config.js                  # ESLint 10 Flat Config (TypeScript + React Hooks + Prettier)
│   ├── index.html                        # HTML5 root template mounting `#root` div
│   ├── package.json                      # npm package manifest, scripts & dependencies
│   ├── pnpm-lock.yaml                    # Deterministic pnpm dependency lockfile
│   ├── README.md                         # Frontend-specific documentation & script guide
│   ├── tsconfig.json                     # TypeScript root project reference config
│   ├── tsconfig.app.json                 # TypeScript compiler options for frontend application code
│   ├── tsconfig.node.json                # TypeScript compiler options for Vite config
│   ├── vite.config.ts                    # Vite build tool and React plugin configuration
│   │
│   ├── public/                           # Static assets served at root
│   │   └── favicon.svg                   # Application SVG favicon
│   │
│   └── src/                              # React application source code
│       ├── main.tsx                      # Application mounting point using `createRoot` in StrictMode
│       ├── App.tsx                       # Root layout, Header/Footer wrappers & React Router v7 routes
│       ├── index.css                     # Global typography, color variables & layout styling
│       │
│       ├── components/                   # Reusable UI components
│       │   ├── categorycard.tsx          # Dynamic category card with themed colors & document counters
│       │   ├── categorycard.css          # Category card gradients, layout & hover animations
│       │   ├── footer.tsx                # Application footer with copyright & static links
│       │   ├── footer.css                # Footer layout & link styling
│       │   ├── header.tsx                # Responsive navigation header with user badge & logout button
│       │   ├── header.css                # Header layout, branding & navigation styling
│       │   └── sidebar.tsx               # (Unused) Sidebar navigation component
│       │
│       ├── pages/                        # Primary route page components
│       │   ├── login.tsx                 # User authentication page (`/login`)
│       │   ├── register.tsx              # User registration page (`/register`)
│       │   ├── registration.tsx          # (Unused stub) Redundant registration component
│       │   ├── dashboard.tsx             # Document dashboard with category filters & downloads (`/dashboard`)
│       │   ├── upload.tsx                # Drag-and-drop PDF upload & real-time classification (`/upload`)
│       │   ├── auth.css                  # Shared authentication styling for login & registration
│       │   ├── dashboard.css             # Dashboard grid, document cards & empty state styling
│       │   └── upload.css                # Upload dropzone & classification pill badge styling
│       │
│       └── utils/                        # Frontend utility helpers
│           └── category.ts               # Category emoji icon resolver & theme class mapper
│
└── docs/                                 # Full technical documentation suite
```

---

## 🏛️ Directory Responsibilities Summary

| Directory | Primary Responsibility | Key Files |
| :--- | :--- | :--- |
| `backend/src/api/` | Exposes REST HTTP endpoints, validates request payloads via DTOs, and manages user auth. | `api.py`, `document.py`, `users.py`, `categories.py` |
| `backend/src/constants/` | Ingests environment variables and exposes typed application constants. | `constant.py` |
| `backend/src/data/` | Manages PostgreSQL connection lifecycle, provisions database tables, and defines SQLModel entities. | `database.py` |
| `backend/src/model/` | Executes file validation, dual-pass PDF text extraction, OCR inference, and ML classification. | `contents.py`, `categorizer.py` |
| `frontend/src/components/`| Provides reusable UI components for layout, navigation, and category cards. | `header.tsx`, `footer.tsx`, `categorycard.tsx` |
| `frontend/src/pages/` | Implements user-facing application screens and handles REST API fetch integrations. | `dashboard.tsx`, `upload.tsx`, `login.tsx`, `register.tsx` |
| `frontend/src/utils/` | Shared helper functions for mapping category names to CSS themes and emoji icons. | `category.ts` |
| `docs/` | Comprehensive technical architecture and operations documentation. | `README.md`, `DOCUMENTATION_AUDIT.md` |
