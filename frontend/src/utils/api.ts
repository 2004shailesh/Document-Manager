/**
 * ==============================================================================
 * Centralized API Configuration & Resilient Network Utilities
 * ==============================================================================
 * Author: Senior Software Engineer & Cloud Deployment Architect
 * Purpose:
 *   Provides centralized backend endpoint configuration and resilient network
 *   fetch operations designed to smoothly handle cloud free-tier cold starts
 *   (Render / Koyeb / Fly) with automated exponential retries and warmup pings.
 * ==============================================================================
 */

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

let isWarmupTriggered = false;

/**
 * Sends a non-blocking background ping to wake up a sleeping backend container.
 * Safe to call multiple times; will only execute once per browser session.
 */
export function warmupServer(): void {
  if (isWarmupTriggered) return;
  isWarmupTriggered = true;

  // Background ping without awaiting or blocking UI
  fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    mode: 'cors',
  })
    .then((res) => {
      if (res.ok) {
        console.info('[API Warmup] Backend service is awake and healthy.');
      }
    })
    .catch(() => {
      // Quietly ignore warmup errors (actual requests will retry if needed)
      console.debug('[API Warmup] Warmup ping sent to backend.');
    });
}

export interface FetchRetryOptions extends RequestInit {
  retries?: number;
  retryDelayMs?: number;
  timeoutMs?: number;
  onStatusUpdate?: (statusText: string) => void;
}

/**
 * Resilient fetch wrapper with automatic timeout and retry capabilities.
 * Specially tuned to absorb 30-50s cold-start delays on free cloud hosting.
 */
export async function resilientFetch(
  url: string,
  options: FetchRetryOptions = {}
): Promise<Response> {
  const {
    retries = 2,
    retryDelayMs = 2500,
    timeoutMs = 35000,
    onStatusUpdate,
    ...fetchOptions
  } = options;

  let lastError: unknown;

  for (let attempt = 1; attempt <= retries + 1; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      if (attempt > 1 && onStatusUpdate) {
        onStatusUpdate(
          `Waking up server from sleep mode (Attempt ${attempt}/${retries + 1})...`
        );
      }

      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (err: unknown) {
      clearTimeout(timeoutId);
      lastError = err;

      const isAbort = (err as Error)?.name === 'AbortError';
      const isNetworkError = err instanceof TypeError || isAbort;

      if (attempt <= retries && isNetworkError) {
        if (onStatusUpdate) {
          onStatusUpdate(
            `Server is starting up (Attempt ${attempt}/${retries + 1}), waiting a few seconds...`
          );
        }
        await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
        continue;
      }

      break;
    }
  }

  throw lastError;
}

/**
 * Extracts a human-friendly error string from a failed API response payload.
 */
export async function extractApiErrorMessage(
  response: Response,
  fallbackMessage: string
): Promise<string> {
  try {
    const data = await response.json().catch(() => null);
    if (!data) return fallbackMessage;

    if (data.detail) {
      if (typeof data.detail === 'string') return data.detail;
      if (Array.isArray(data.detail)) {
        return data.detail
          .map((err: { msg?: string }) => err.msg || '')
          .filter(Boolean)
          .join(', ');
      }
      return JSON.stringify(data.detail);
    }

    if (data.message && typeof data.message === 'string') {
      return data.message;
    }
  } catch {
    // Fall back to provided default
  }
  return fallbackMessage;
}

