/**
 * ==============================================================================
 * User Authentication (Login) Page Component
 * ==============================================================================
 * Purpose:
 *   Authenticates registered users via `POST /users/login`.
 *   Upon receiving a valid `UserPublic` payload, persists user identity into
 *   browser `localStorage` and redirects to the `/dashboard`.
 * ==============================================================================
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../utils/api';
import './auth.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        let errorMessage = 'Invalid email or password. Please check your credentials.';
        if (data && data.detail) {
          errorMessage =
            typeof data.detail === 'string'
              ? data.detail
              : Array.isArray(data.detail)
                ? data.detail
                    .map((err: { msg?: string }) => err.msg || '')
                    .filter(Boolean)
                    .join(', ')
                : JSON.stringify(data.detail);
        }
        setError(errorMessage);
        return;
      }

      // Save user profile into localStorage and navigate to dashboard
      localStorage.setItem('user', JSON.stringify(data));
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      setError(
        `Cannot connect to server. Please ensure the backend is running at ${API_BASE_URL}.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Log in to access your document dashboard</p>
        </div>

        {error && (
          <div className="auth-error-banner" role="alert">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <button type="submit" className="auth-submit-button" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register">Create one here</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
