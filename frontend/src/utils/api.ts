/**
 * ==============================================================================
 * Centralized API Configuration Utility
 * ==============================================================================
 * Sourced from Vite environment variables (VITE_API_BASE_URL).
 * - In Development: Uses `http://localhost:8000` from `.env.development`.
 * - In Production: Uses the configured backend URL from `.env.production` or Vercel.
 * ==============================================================================
 */

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');
