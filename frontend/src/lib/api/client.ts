import { PUBLIC_API_URL } from '$env/static/public';

export type ApiError = {
  code: string;
  message: string;
  status?: number;
  detail?: string;
  fieldErrors?: Record<string, string[]>;
  requestId?: string;
};

export type PaginatedResponse<T> = {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
};

const TOKEN_KEY = 'kepin_token';

function getToken(): string | null {
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'content-type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(`${PUBLIC_API_URL}${path}`, {
    ...init,
    headers: {
      ...headers,
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ code: 'UNKNOWN', message: 'Unknown error' }));
    throw {
      ...error,
      status: response.status,
      message: error.message || error.detail || `HTTP ${response.status}`,
    } as ApiError;
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
