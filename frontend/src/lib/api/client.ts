const PUBLIC_API_URL = (typeof process !== 'undefined'
  ? (typeof process.env !== 'undefined'
      ? process.env['PUBLIC_API_URL']
      : undefined)
  : undefined) ?? 'http://localhost:8000/api/v1';

export type ApiError = {
  code: string;
  message: string;
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

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${PUBLIC_API_URL}${path}`, {
    ...init,
    headers: {
      'content-type': 'application/json',
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ code: 'UNKNOWN', message: 'Unknown error' }));
    throw error as ApiError;
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
