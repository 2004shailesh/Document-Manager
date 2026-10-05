# Frontend Components Reference

This document details the reusable UI components located in `frontend/src/components/`.

---

## 🧩 Component Inventory

### 1. Header (`header.tsx`)
- **File**: `frontend/src/components/header.tsx`
- **Stylesheet**: `frontend/src/components/header.css`
- **Props**: None (inspects `localStorage` and `useLocation()`).
- **Functionality**:
  - Top navigation bar rendered on every page.
  - When User is Logged In: Displays Brand logo, `Dashboard` link, `Upload` link, user display name badge (`👤 {user.name}`), and a **Logout** button.
  - When User is Logged Out: Displays Brand logo, `Login` link, and `Register` link.
  - `handleLogout()` clears `localStorage.removeItem('user')` and redirects to `/login`.

---

### 2. CategoryCard (`categorycard.tsx`)
- **File**: `frontend/src/components/categorycard.tsx`
- **Stylesheet**: `frontend/src/components/categorycard.css`
- **Props Interface**:
  ```typescript
  interface CategoryCardProps {
    name: string;
    count: number;
    icon?: string;
    onClick?: () => void;
    isSelected?: boolean;
  }
  ```
- **Functionality**:
  - Renders a themed card widget for a category with document count.
  - Dynamically assigns emoji icons using `getCategoryIcon(name)`.
  - Dynamically assigns theme class (e.g., `theme-invoice`, `theme-medical`) using `getCategoryTheme(name)`.
  - Supports keyboard accessibility (`Enter` and `Space` key handlers) and ARIA attributes (`role="button"`, `aria-label`).
  - Highlights visually when `isSelected` is true.

---

### 3. Footer (`footer.tsx`)
- **File**: `frontend/src/components/footer.tsx`
- **Stylesheet**: `frontend/src/components/footer.css`
- **Props**: None.
- **Functionality**:
  - Renders at the bottom of every page.
  - Dynamically computes current year via `new Date().getFullYear()`.
  - Displays copyright notice and placeholder footer links (Privacy Policy, Terms of Service, Contact).

---

### 4. Sidebar (`sidebar.tsx`) — *(Unused Component)*
- **File**: `frontend/src/components/sidebar.tsx`
- **Status**: Defined in source code but currently unused in `App.tsx` (cataloged in [`docs/DOCUMENTATION_ISSUES.md`](file:///c:/Users/shail/OneDrive/Desktop/project/docs/DOCUMENTATION_ISSUES.md)).
