# Document Manager — Frontend Web Application

A Single Page Application (SPA) for the Document Management & Classification Service.

Built with **React 19**, **TypeScript**, **Vite**, and **React Router v7**.

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
# Using pnpm (recommended)
pnpm install

# Or using npm
npm install
```

### 2. Start Development Server
```bash
pnpm run dev
```
The application will be available at `http://localhost:5173`.

---

## 🛠️ Available Scripts

| Script | Command | Purpose |
| :--- | :--- | :--- |
| `dev` | `pnpm run dev` | Starts Vite development server with Hot Module Replacement (HMR) |
| `build` | `pnpm run build` | Runs TypeScript type checking (`tsc -b`) and bundles for production into `dist/` |
| `preview` | `pnpm run preview` | Locally previews the production build from `dist/` |
| `lint` | `pnpm run lint` | Runs ESLint 10 across all `.ts` and `.tsx` source files |
| `lint:fix` | `pnpm run lint:fix` | Automatically fixes autofixable ESLint errors |
| `format` | `pnpm run format` | Formats all source files with Prettier |
| `format:check`| `pnpm run format:check` | Verifies code formatting without writing changes |

---

## 📁 Source Directory Structure

```text
frontend/src/
├── App.tsx                  # Root layout shell and React Router declarations
├── main.tsx                 # React 19 entrypoint mounting #root in StrictMode
├── index.css                # Global background gradients and base layout styles
├── components/              # Reusable UI components
│   ├── categorycard.tsx     # Interactive category card with dynamic theme classes
│   ├── categorycard.css     # Category card gradients and hover animations
│   ├── footer.tsx           # Global application footer
│   ├── footer.css           # Footer styling
│   ├── header.tsx           # Navigation bar with dynamic session and logout buttons
│   └── header.css           # Header navigation styling
├── pages/                   # Top-level route pages
│   ├── login.tsx            # User authentication page (/login)
│   ├── register.tsx         # User registration page (/register)
│   ├── dashboard.tsx        # Document dashboard, category filters, and downloads (/dashboard)
│   ├── upload.tsx           # PDF upload and instant classification page (/upload)
│   ├── auth.css             # Login & registration styling
│   ├── dashboard.css        # Dashboard grid and document card styling
│   └── upload.css           # Upload dropzone and classification result styling
└── utils/
    └── category.ts          # Category icon emoji resolver and theme class mapper
```

---

## 🔗 Backend API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:
- **Auth**: `POST http://localhost:8000/users/login`, `POST http://localhost:8000/users/`
- **Dashboard**: `GET http://localhost:8000/users/{user_id}/documents`, `GET http://localhost:8000/categories/`
- **Upload**: `POST http://localhost:8000/documents/` (multipart/form-data)
- **Download**: `GET http://localhost:8000/documents/{document_id}/download` (BLOB stream)

For detailed architectural and API documentation, refer to [`docs/07-frontend.md`](file:///c:/Users/shail/OneDrive/Desktop/project/docs/07-frontend.md) and [`docs/05-api-reference.md`](file:///c:/Users/shail/OneDrive/Desktop/project/docs/05-api-reference.md).
