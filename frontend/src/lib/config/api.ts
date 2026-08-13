import { PUBLIC_API_URL } from '$env/static/public';
import { dev } from '$app/environment';

const LOOPBACK = /^(localhost|127\.0\.0\.1|::1)$/;

export function getApiUrl(): string {
  if (typeof window === 'undefined') return PUBLIC_API_URL;

  let url: URL;
  try {
    url = new URL(PUBLIC_API_URL);
  } catch {
    url = new URL('http://localhost:8000/api/v1');
  }

  const isLocal = dev || LOOPBACK.test(url.hostname);
  if (isLocal) {
    url.hostname = window.location.hostname;
  }

  return url.toString().replace(/\/$/, '');
}