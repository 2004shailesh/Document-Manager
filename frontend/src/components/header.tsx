/**
 * ==============================================================================
 * Application Header Navigation Component
 * ==============================================================================
 * Purpose:
 *   Universal top navigation bar. Dynamically displays authenticated links
 *   (Dashboard, Upload, User Badge, Logout) when a user session exists in `localStorage`,
 *   or public links (Login, Register) when unauthenticated.
 * ==============================================================================
 */

import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
import './header.css';

interface StoredUser {
  id: number;
  name: string;
  email: string;
}

function getStoredUser(): StoredUser | null {
  const stored = localStorage.getItem('user');
  if (!stored) return null;
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

function Header() {
  const navigate = useNavigate();
  useLocation(); // Triggers header update on route navigation
  const user = getStoredUser();

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <header className="app-header">
      <Link to={user ? '/dashboard' : '/login'} className="header-brand">
        <span className="brand-icon" aria-hidden="true">
          📄
        </span>
        <span className="brand-title">Document Manager</span>
      </Link>

      <nav className="header-nav">
        {user ? (
          <>
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Dashboard
            </NavLink>

            <NavLink
              to="/upload"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Upload
            </NavLink>

            <div className="nav-user">
              <span className="user-badge" title={user.email}>
                👤 {user.name}
              </span>
              <button type="button" className="header-logout-button" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <NavLink
              to="/login"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Login
            </NavLink>

            <NavLink
              to="/register"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Register
            </NavLink>
          </>
        )}
      </nav>
    </header>
  );
}

export default Header;
