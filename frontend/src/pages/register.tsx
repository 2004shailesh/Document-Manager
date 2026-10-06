/**
 * ==============================================================================
 * User Registration Page Component
 * ==============================================================================
 * Purpose:
 *   Handles new user account registration via `POST /users/`.
 *   Upon successful registration, displays feedback and redirects the user
 *   to `/login` to establish their authenticated session.
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

function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  // Proactively ping backend on mount
  useEffect(() => {
    warmupServer();
  }, []);

  const handleRegister = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setStatusMessage(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      const response = await resilientFetch(`${API_BASE_URL}/users/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
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
          'Registration failed. Please check your information.'
        );
        setError(errorMsg);
        return;
      }

      setSuccessMessage('Account created successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 1200);
    } catch (err) {
      console.error('Registration error:', err);
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
          <h1>Create an Account</h1>
          <p>Register to manage and classify your documents</p>
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
                onClick={() => handleRegister()}
                disabled={isLoading}
              >
                🔄 Retry Connection
              </button>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="auth-success-banner" role="status">
            <span>✓</span>
            <span>{successMessage}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleRegister}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              placeholder="e.g. John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

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
                <span>Creating Account...</span>
              </span>
            ) : (
              'Register'
            )}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in here</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;

