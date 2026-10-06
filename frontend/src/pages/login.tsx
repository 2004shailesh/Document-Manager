/**
 * ==============================================================================
 * User Authentication (Login) Page Component
 * ==============================================================================
 * Purpose:
 *   Authenticates registered users via `POST /users/login`.
 *   Upon receiving a valid `UserPublic` payload, persists user identity into
 *   browser `localStorage` and redirects to the `/dashboard`.
 *
 * Resiliency:
 *   - Auto-warms the backend on page load (`warmupServer`).
 *   - Uses `resilientFetch` to gracefully wait and retry through cloud cold starts.
 * ==============================================================================
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  API_BASE_URL,
  extractApiErrorMessage,
  resilientFetch,
  warmupServer,
} from '../utils/api';
import './auth.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Proactively ping backend on mount to start spin-up if asleep
  useEffect(() => {
    warmupServer();
  }, []);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setStatusMessage(null);
    setIsLoading(true);

    try {
      const response = await resilientFetch(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
        retries: 2,
        retryDelayMs: 3000,
        timeoutMs: 35000,
        onStatusUpdate: (msg) => setStatusMessage(msg),
      });

      if (!response.ok) {
        const errorMsg = await extractApiErrorMessage(
          response,
          'Invalid email or password. Please check your credentials.'
        );
        setError(errorMsg);
        return;
      }

      const data = await response.json();

      // Save user profile into localStorage and navigate to dashboard
      localStorage.setItem('user', JSON.stringify(data));
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      setError(
        `Unable to reach the server at ${API_BASE_URL}. If the backend was asleep, please click 'Retry Connection' below.`
      );
    } finally {
      setIsLoading(false);
      setStatusMessage(null);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Log in to access your document dashboard</p>
        </div>

        {statusMessage && (
          <div className="auth-status-banner" role="status">
            <span className="auth-spinner"></span>
            <span>{statusMessage}</span>
          </div>
        )}

        {error && (
          <div className="auth-error-banner" role="alert">
            <div className="auth-error-content">
              <span>⚠️ {error}</span>
              <button
                type="button"
                className="auth-retry-button"
                onClick={() => handleLogin()}
                disabled={isLoading}
              >
                🔄 Retry Connection
              </button>
            </div>
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
            {isLoading ? (
              <span className="button-loading-content">
                <span className="auth-spinner-small"></span>
                <span>Connecting...</span>
              </span>
            ) : (
              'Login'
            )}
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

