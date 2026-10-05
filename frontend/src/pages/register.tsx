/**
 * ==============================================================================
 * User Registration Page Component
 * ==============================================================================
 * Purpose:
 *   Handles new user account registration via `POST /users/`.
 *   Upon successful registration, displays feedback and redirects the user
 *   to `/login` to establish their authenticated session.
 * ==============================================================================
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../utils/api';
import './auth.css';

function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/users/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          password,
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        let errorMessage = 'Registration failed. Please check your information.';
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

      setSuccessMessage('Account created successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 1200);
    } catch (err) {
      console.error('Registration error:', err);
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
          <h1>Create an Account</h1>
          <p>Register to manage and classify your documents</p>
        </div>

        {error && (
          <div className="auth-error-banner" role="alert">
            <span>⚠️</span>
            <span>{error}</span>
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
            {isLoading ? 'Creating Account...' : 'Register'}
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
