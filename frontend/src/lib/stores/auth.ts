import { writable } from 'svelte/store';
import { getApiUrl } from '$lib/config/api';

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar?: string;
  isSuperadmin?: boolean;
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

export type LoginResult = {
  success: boolean;
  error?: string;
  tenantSlug?: string;
  isSuperadmin?: boolean;
  mfaRequired?: boolean;
  mfaToken?: string;
};

export async function login(email: string, password: string): Promise<LoginResult> {
  try {
    const response = await fetch(`${getApiUrl()}/auth/login`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Email atau password salah' }));
      return { success: false, error: body.detail || 'Email atau password salah' };
    }
    const body = await response.json();

    if (body.mfa_required) {
      localStorage.setItem('kepin_mfa_token', body.mfa_token || '');
      return { success: false, mfaRequired: true, mfaToken: body.mfa_token };
    }

    return finalizeLogin(body);
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

function finalizeLogin(body: any): LoginResult {
  localStorage.setItem(TOKEN_KEY, body.access_token);

  const isSuperadmin = body.user?.isSuperadmin || false;
  const user: AuthUser = {
    id: body.user?.id,
    name: body.user?.name,
    email: body.user?.email,
    phone: body.user?.phone || '',
    avatar: body.user?.avatarUrl,
    isSuperadmin,
  };
  saveSession(user);
  currentUser.set(user);

  const tenants: { slug: string; role: string; name?: string; joinCode?: string; id?: string }[] = (body.tenants || []).map((t: any) => ({
    slug: t.slug, role: t.role, name: t.name, joinCode: t.joinCode, id: t.id,
  }));
  localStorage.setItem('kepin_tenants', JSON.stringify(tenants));

  const firstSlug = tenants[0]?.slug || '';
  return { success: true, tenantSlug: firstSlug, isSuperadmin };
}

export async function verifyMfa(code: string): Promise<LoginResult> {
  try {
    const mfaToken = localStorage.getItem('kepin_mfa_token') || '';
    if (!mfaToken) return { success: false, error: 'Sesi verifikasi MFA tidak ditemukan. Silakan login ulang.' };
    const response = await fetch(`${getApiUrl()}/auth/mfa/verify`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ mfa_token: mfaToken, code }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Kode verifikasi salah' }));
      return { success: false, error: body.detail || 'Kode verifikasi salah' };
    }
    const body = await response.json();
    localStorage.removeItem('kepin_mfa_token');
    return finalizeLogin(body);
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

export async function register(name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${getApiUrl()}/auth/register`, {
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

export async function forgotPassword(email: string): Promise<{ success: boolean; error?: string; devToken?: string }> {
  try {
    const response = await fetch(`${getApiUrl()}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Gagal mengirim tautan reset' }));
      return { success: false, error: body.detail || 'Gagal mengirim tautan reset' };
    }
    const body = await response.json();
    return { success: true, devToken: body.dev_reset_token || undefined };
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

export async function resetPassword(token: string, newPassword: string): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${getApiUrl()}/auth/reset-password`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Gagal mereset password' }));
      return { success: false, error: body.detail || 'Gagal mereset password' };
    }
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<{ success: boolean; error?: string }> {
  try {
    const token = localStorage.getItem(TOKEN_KEY) || '';
    const response = await fetch(`${getApiUrl()}/auth/change-password`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: 'Gagal mengganti password' }));
      return { success: false, error: body.detail || 'Gagal mengganti password' };
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

export type TenantInfo = { slug: string; role: string; name?: string; joinCode?: string; id?: string };

/** Tenant milik user di sesi ini (dari localStorage kepin_tenants). */
export function getTenants(): TenantInfo[] {
  if (typeof localStorage === 'undefined') return [];
  try {
    return JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
  } catch {
    return [];
  }
}

/** Keluar dari sebuah perusahaan (khusus karyawan/non-pemilik). */
export async function leaveTenant(slug: string): Promise<{ success: boolean; error?: string }> {
  try {
    const token = localStorage.getItem(TOKEN_KEY) || '';
    const res = await fetch(`${getApiUrl()}/tenants/${slug}/membership/leave`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: 'Gagal keluar dari perusahaan' }));
      return { success: false, error: body.detail || 'Gagal keluar dari perusahaan' };
    }
    try {
      const tenants = getTenants().filter((t) => t.slug !== slug);
      localStorage.setItem('kepin_tenants', JSON.stringify(tenants));
    } catch { /* noop */ }
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err?.message || 'Gagal terhubung ke server' };
  }
}

export function updateProfile(data: { name?: string; email?: string; phone?: string }): AuthUser | null {
  const user = getSession();
  if (!user) return null;
  const updated = { ...user, ...data };
  saveSession(updated);
  currentUser.set(updated);
  return updated;
}
