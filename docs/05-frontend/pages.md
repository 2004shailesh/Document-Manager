# Frontend Pages Catalog

This document details the responsibilities, routes, UI components, API interactions, and user flows for each page in the application.

---

## 📱 Page Reference Matrix

| Page Name | Route Path | File Location | Key API Calls | Primary Functionality |
| :--- | :--- | :--- | :--- | :--- |
| **Login** | `/login` | `frontend/src/pages/login.tsx` | `POST /users/login` | Authenticates users; stores session in `localStorage` and redirects to `/dashboard`. |
| **Register** | `/register` | `frontend/src/pages/register.tsx` | `POST /users/` | Registers new accounts with Argon2 password hashing; redirects to `/login`. |
| **Dashboard** | `/dashboard` | `frontend/src/pages/dashboard.tsx` | `GET /users/{id}/documents`, `GET /categories/`, `GET /documents/{id}/download` | Displays user document categories, category filtering, document previews, and one-click PDF downloads. |
| **Upload** | `/upload` | `frontend/src/pages/upload.tsx` | `POST /documents/` | Drag-and-drop / file selector upload with 3MB client guard and real-time category badge feedback. |

---

## 🔍 Page Deep-Dives

### 1. Dashboard (`/dashboard`)
- **Route**: `/dashboard` (Also the default fallback route from `/`).
- **Session Check**: Verifies `localStorage.getItem('user')`. If not found, immediately redirects to `/login`.
- **Data Flow & Caching**:
  1. Calls `GET /users/{user_id}/documents` on mount to fetch all documents owned by the logged-in user.
  2. Calls `GET /categories/` to map category IDs to names.
  3. Computes active category document counts for the user and caches the document list in component state (`userDocuments`).
  4. If the user has 0 documents, renders the Empty State: *"OOPS ! upload a document"*.
  5. If the user has documents, renders interactive `CategoryCard` components in a responsive grid.
  6. Clicking a `CategoryCard` filters documents in memory (`useMemo`) without making additional API calls.
  7. **4-Way Sorting Dropdown**:
     - `Name A → Z` (`name_asc`): Alphabetical ascending order.
     - `Name Z → A` (`name_desc`): Alphabetical descending order.
     - `Old to New` (`time_asc`): Chronological ascending order using the database `uploaded_at` timestamp.
     - `New to Old` (`time_desc`): Chronological descending order using the database `uploaded_at` timestamp.
  8. Clicking the **Download** button invokes `GET /documents/{id}/download`, converts the response to a browser `Blob`, and triggers an automated file download.

---

### 2. Document Upload (`/upload`)
- **Route**: `/upload`.
- **File Validation**: Enforces `MAX_FILE_SIZE_MB = 3` (`3,145,728 bytes`). If a larger file is selected, the file input is reset and an error banner is displayed.
- **Data Flow**:
  1. User selects a PDF file.
  2. Clicks **Upload Document**.
  3. Form data is assembled: `formdata.append('file', file)` and `formdata.append('owner_user_id', user.id)`.
  4. Button state switches to *"Extracting & Classifying..."*.
  5. On success (`HTTP 201`), renders the Success Card with extracted category pill badges and a direct link to the Dashboard.

---

### 3. User Login (`/login`)
- **Route**: `/login`.
- **Form Fields**: Email address and password.
- **Data Flow**: Submits JSON to `POST /users/login`. On success, writes user profile to `localStorage.setItem('user', JSON.stringify(data))` and navigates to `/dashboard`.

---

### 4. User Registration (`/register`)
- **Route**: `/register`.
- **Form Fields**: Full Name, Email Address, Password.
- **Data Flow**: Submits JSON to `POST /users/`. Displays success banner and automatically navigates to `/login` after 1.2 seconds.
