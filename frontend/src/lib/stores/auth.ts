import { writable } from 'svelte/store';

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar?: string;
};

type StoredUser = {
  id: string;
  name: string;
  email: string;
  phone: string;
  password: string;
};

const USERS_KEY = 'kepin_users';
const SESSION_KEY = 'kepin_session';

function getStoredUsers(): StoredUser[] {
  if (typeof localStorage === 'undefined') return [];
  return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
}

function saveUsers(users: StoredUser[]) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function getSession(): AuthUser | null {
  if (typeof localStorage === 'undefined') return null;
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function saveSession(user: AuthUser) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export const currentUser = writable<AuthUser | null>(getSession());

export function login(email: string, password: string): { success: boolean; error?: string } {
  const users = getStoredUsers();
  const found = users.find(u => u.email === email);
  if (!found) return { success: false, error: 'Email tidak terdaftar' };
  if (found.password !== password) return { success: false, error: 'Password salah' };
  const user: AuthUser = { id: found.id, name: found.name, email: found.email, phone: found.phone };
  saveSession(user);
  currentUser.set(user);
  return { success: true };
}

export function register(name: string, email: string, password: string): { success: boolean; error?: string } {
  const users = getStoredUsers();
  if (users.find(u => u.email === email)) return { success: false, error: 'Email sudah terdaftar' };
  const newUser: StoredUser = {
    id: crypto.randomUUID?.() || Date.now().toString(),
    name,
    email,
    phone: '',
    password,
  };
  saveUsers([...users, newUser]);
  const user: AuthUser = { id: newUser.id, name: newUser.name, email: newUser.email, phone: newUser.phone };
  saveSession(user);
  currentUser.set(user);
  return { success: true };
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

  const users = getStoredUsers();
  const idx = users.findIndex(u => u.id === user.id);
  if (idx !== -1) {
    users[idx] = { ...users[idx], ...data };
    saveUsers(users);
  }
  return updated;
}
