# Coding Standards & Conventions

This document defines the coding standards, static typing guidelines, and style rules enforced across the Python backend and TypeScript frontend codebases.

---

## 🐍 Python Coding Standards

1. **Python Version**: Target Python `3.12+`. Use modern syntax:
   - Union types: `int | None`, `str | None` (avoid legacy `Optional[int]`).
   - Generic aliases: `list[str]`, `dict[str, float]` (avoid `typing.List`, `typing.Dict`).
   - `collections.abc.Generator`, `collections.abc.Sequence`.
2. **Line Length & Formatting**: Max line length is **100 characters** (configured in `pyproject.toml` for Black and isort).
3. **Type Annotations**:
   - Every function and method must declare type annotations for all parameters and return values.
   - FastAPI route dependencies must use `typing.Annotated` with `Depends()`, `Query()`, `Form()`, or `File()`.
4. **Module Header Comments**:
   - Major files should include clean header blocks describing the module's architectural purpose and framework bindings.
5. **No Blind Exception Silencing**:
   - Always catch specific exceptions (`InvalidFileTypeError`, `HTTPException`, `psycopg2.Error`). If catching `Exception`, log it with `logger.warning()` or `logger.error()`.

---

## ⚛️ TypeScript & React Coding Standards

1. **TypeScript Typing**:
   - Avoid `any`. Define explicit interfaces or types for all component props, state objects, and API response payloads.
2. **Component Conventions**:
   - Use standard React function declarations (`function Dashboard() { ... }`).
   - Ensure components have a single clear responsibility.
   - Separate reusable UI elements into `frontend/src/components/`.
3. **React Hooks Guidelines**:
   - Strictly follow React Hook rules (e.g. declare hooks at the top level of components).
   - Use `useCallback` for functions passed as dependencies to `useEffect`.
4. **Styling Rules**:
   - Keep styles modular with companion CSS files (e.g. `dashboard.tsx` with `dashboard.css`).
   - Use CSS classes over inline styles for maintainability and performance.
5. **Accessibility**:
   - Provide `aria-label`, `role="button"`, and keyboard event handlers (`onKeyDown`) on clickable interactive divs.
