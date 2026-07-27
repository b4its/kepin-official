import { api } from './client';

export async function login(email: string, password: string) { return api('/dev-auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }); }
export async function register(data: { name: string; email: string; password: string }) { return api('/dev-auth/register', { method: 'POST', body: JSON.stringify(data) }); }
export async function logout() { return api('/dev-auth/logout', { method: 'POST' }); }
export async function forgotPassword(email: string) { return api('/dev-auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }); }
export async function resetPassword(token: string, password: string) { return api('/dev-auth/reset-password', { method: 'POST', body: JSON.stringify({ token, password }) }); }
export async function getProfile() { return api('/dev-auth/profile'); }
export async function updateProfile(data: { name?: string; phone?: string }) { return api('/dev-auth/profile', { method: 'PATCH', body: JSON.stringify(data) }); }
