# Frontend Structure & Styling Architecture

This document describes the directory organization, CSS styling system, asset structure, and build configuration of the React 19 Single Page Application.

---

## 🗂️ Frontend File Organization

```text
frontend/
├── index.html                    # Root HTML5 template mounting <div id="root"></div>
├── package.json                  # Dependencies: react 19, react-router-dom 7, vite 8
├── tsconfig.json                 # TypeScript project configuration
├── vite.config.ts                # Vite React plugin setup
├── eslint.config.js              # ESLint 10 flat configuration
├── .prettierrc                   # Prettier formatting rules
│
├── public/
│   └── favicon.svg               # Application SVG favicon
│
└── src/
    ├── main.tsx                  # Mounts App component using ReactDOM.createRoot
    ├── App.tsx                   # Defines <BrowserRouter>, Header, Routes, and Footer
    ├── index.css                 # Global CSS variables, reset, font stacks, and layout shells
    │
    ├── components/               # Reusable UI component modules & styles
    │   ├── categorycard.tsx      # Themed category card with count & click handler
    │   ├── categorycard.css      # Gradients, hover scale animations & category themes
    │   ├── footer.tsx            # Application footer component
    │   ├── footer.css            # Footer styling & link layout
    │   ├── header.tsx            # Sticky navigation bar with dynamic session controls
    │   ├── header.css            # Brand typography, active link highlights & logout button
    │   └── sidebar.tsx           # (Unused) Sidebar navigation component
    │
    ├── pages/                    # Route page views & styles
    │   ├── login.tsx             # User login form
    │   ├── register.tsx          # User signup form
    │   ├── registration.tsx      # (Unused stub) Redundant registration component
    │   ├── dashboard.tsx         # Document dashboard with category filters & downloads
    │   ├── upload.tsx            # PDF upload dropzone with 3MB guard & result cards
    │   ├── auth.css              # Authentication form cards, error banners & inputs
    │   ├── dashboard.css         # Grid layouts, document cards, spinners & empty states
    │   └── upload.css            # Upload dropzone, file input, and classification pill styles
    │
    └── utils/
        └── category.ts           # Category icon emoji resolver and theme class mapper
```

---

## 🎨 Global Styling & Theme System

The frontend utilizes Vanilla CSS with modular component stylesheets and scoped theme classes defined in `frontend/src/utils/category.ts` and `frontend/src/components/categorycard.css`:

| Category Name | Theme CSS Class | Background Gradient | Accent Border |
| :--- | :--- | :--- | :--- |
| **Invoice** | `.theme-invoice` | `linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)` | `#bfdbfe` |
| **Contracts** | `.theme-contracts` | `linear-gradient(135deg, #fefce8 0%, #fef9c3 100%)` | `#fef08a` |
| **Reports** | `.theme-reports` | `linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)` | `#bbf7d0` |
| **Notes** | `.theme-notes` | `linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%)` | `#f5d0fe` |
| **Medical** | `.theme-medical` | `linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%)` | `#fecdd3` |
| **Others** | `.theme-others` | `linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)` | `#e2e8f0` |

---

## ⚡ Typography & Layout

- **Font Family**: Modern system UI font stack (`system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif`).
- **Layout Model**: Flexbox-driven full-height layout (`min-height: 100vh`, `display: flex`, `flex-direction: column`) with sticky header, expanding `<main>` content, and fixed footer.
