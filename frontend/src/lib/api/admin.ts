import { api } from './client';

export async function getAdminDashboard() { return api('/platform/dashboard'); }
export async function getAdminTenants(params?: string) { return api(`/platform/tenants${params || ''}`); }
export async function createAdminTenant(data: any) { return api('/platform/tenants', { method: 'POST', body: JSON.stringify(data) }); }
export async function suspendTenant(id: string) { return api(`/platform/tenants/${id}/suspend`, { method: 'POST' }); }
export async function reactivateTenant(id: string) { return api(`/platform/tenants/${id}/reactivate`, { method: 'POST' }); }
export async function getAdminUsers() { return api('/platform/users'); }
export async function getSubscriptionEvents() { return api('/platform/subscription-events'); }
export async function getIncidents() { return api('/platform/incidents'); }
export async function createIncident(data: any) { return api('/platform/incidents', { method: 'POST', body: JSON.stringify(data) }); }
export async function getPlatformAudit() { return api('/platform/audit-events'); }
export async function getHealthSummary() { return api('/platform/health-summary'); }
