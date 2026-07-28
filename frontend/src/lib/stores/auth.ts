import { writable } from 'svelte/store';
import { PUBLIC_API_URL } from '$env/static/public';

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar?: string;
};

const SESSION_KEY = 'kepin_session';
const TOKEN_KEY = 'kepin_token';

function getSession(): AuthUser | null {
  if (typeof localStorage === 'undefined') return null;
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function saveSession(user: AuthUser) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

function clearSession() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem(TOKEN_KEY);
}

export const currentUser = writable<AuthUser | null>(getSession());

export async function login(email: string, password: string): Promise<{ success: boolean; error?: string; tenantSlug?: string }> {
  try {
    const response = await fetch(`${PUBLIC_API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Email atau password salah' }));
      return { success: false, error: body.detail || 'Email atau password salah' };
    }
    const body = await response.json();
    localStorage.setItem(TOKEN_KEY, body.access_token);

    const user: AuthUser = {
      id: body.user.id,
      name: body.user.name,
      email: body.user.email,
      phone: body.user.phone || '',
      avatar: body.user.avatarUrl,
    };
    saveSession(user);
    currentUser.set(user);

    const tenants: { slug: string; role: string }[] = (body.tenants || []).map((t: any) => ({
      slug: t.slug, role: t.role,
    }));
    localStorage.setItem('kepin_tenants', JSON.stringify(tenants));

    const firstSlug = tenants[0]?.slug || '';
    return { success: true, tenantSlug: firstSlug };
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

export async function register(name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${PUBLIC_API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Registrasi gagal' }));
      return { success: false, error: body.detail || 'Registrasi gagal' };
    }
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

export function logout() {
  clearSession();
  currentUser.set(null);
}

export function updateProfile(data: { name?: string; email?: string; phone?: string }): AuthUser | null {
  const user = getSession();
  if (!user) return null;
  const updated = { ...user, ...data };
  saveSession(updated);
  currentUser.set(updated);
  return updated;
}
