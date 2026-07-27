import { api } from './client';

export async function getTenantContext(slug: string) { return api(`/tenants/${slug}/context`); }
export async function getTenantDashboard(slug: string, preset?: string) {
  const query = preset ? `?preset=${preset}` : '';
  return api(`/tenants/${slug}/dashboard${query}`);
}
export async function getOrganization(slug: string) { return api(`/tenants/${slug}/organization`); }
export async function updateOrganization(slug: string, data: any) { return api(`/tenants/${slug}/organization`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function getBranches(slug: string) { return api(`/tenants/${slug}/branches`); }
export async function createBranch(slug: string, data: any) { return api(`/tenants/${slug}/branches`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateBranch(slug: string, id: string, data: any) { return api(`/tenants/${slug}/branches/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteBranch(slug: string, id: string) { return api(`/tenants/${slug}/branches/${id}`, { method: 'DELETE' }); }
export async function getMembers(slug: string) { return api(`/tenants/${slug}/members`); }
export async function addMember(slug: string, data: any) { return api(`/tenants/${slug}/members`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateMember(slug: string, id: string, data: any) { return api(`/tenants/${slug}/members/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function removeMember(slug: string, id: string) { return api(`/tenants/${slug}/members/${id}`, { method: 'DELETE' }); }
export async function getRoles(slug: string) { return api(`/tenants/${slug}/roles`); }
export async function getIntegrations(slug: string) { return api(`/tenants/${slug}/integrations`); }
export async function getBilling(slug: string) { return api(`/tenants/${slug}/billing`); }
export async function getNotifications(slug: string) { return api(`/tenants/${slug}/notifications`); }
export async function markNotifRead(slug: string, id: string) { return api(`/tenants/${slug}/notifications/${id}/read`, { method: 'PATCH' }); }
export async function markAllNotifRead(slug: string) { return api(`/tenants/${slug}/notifications/read-all`, { method: 'POST' }); }
export async function deleteNotif(slug: string, id: string) { return api(`/tenants/${slug}/notifications/${id}`, { method: 'DELETE' }); }
export async function getAuditEvents(slug: string) { return api(`/tenants/${slug}/audit-events`); }
export async function getAccounts(slug: string) { return api(`/tenants/${slug}/accounts`); }
export async function getAccountBalance(slug: string, id: string) { return api(`/tenants/${slug}/accounts/${id}/balance`); }
export async function createAccount(slug: string, data: any) { return api(`/tenants/${slug}/accounts`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateAccount(slug: string, id: string, data: any) { return api(`/tenants/${slug}/accounts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteAccount(slug: string, id: string) { return api(`/tenants/${slug}/accounts/${id}`, { method: 'DELETE' }); }
export async function getTransactions(slug: string, params?: string) { return api(`/tenants/${slug}/transactions${params || ''}`); }
export async function createTransaction(slug: string, data: any) { return api(`/tenants/${slug}/transactions`, { method: 'POST', body: JSON.stringify(data) }); }
export async function postTransaction(slug: string, id: string) { return api(`/tenants/${slug}/transactions/${id}/post`, { method: 'POST' }); }
export async function voidTransaction(slug: string, id: string) { return api(`/tenants/${slug}/transactions/${id}/void`, { method: 'POST' }); }
export async function getJournals(slug: string, params?: string) { return api(`/tenants/${slug}/journals${params || ''}`); }
export async function getCustomers(slug: string) { return api(`/tenants/${slug}/customers`); }
export async function createCustomer(slug: string, data: any) { return api(`/tenants/${slug}/customers`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateCustomer(slug: string, id: string, data: any) { return api(`/tenants/${slug}/customers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteCustomer(slug: string, id: string) { return api(`/tenants/${slug}/customers/${id}`, { method: 'DELETE' }); }
export async function getInvoices(slug: string, params?: string) { return api(`/tenants/${slug}/invoices${params || ''}`); }
export async function createInvoice(slug: string, data: any) { return api(`/tenants/${slug}/invoices`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateInvoice(slug: string, id: string, data: any) { return api(`/tenants/${slug}/invoices/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteInvoice(slug: string, id: string) { return api(`/tenants/${slug}/invoices/${id}`, { method: 'DELETE' }); }
export async function getSuppliers(slug: string) { return api(`/tenants/${slug}/suppliers`); }
export async function getProducts(slug: string) { return api(`/tenants/${slug}/products`); }
export async function getStockBalances(slug: string) { return api(`/tenants/${slug}/stock-balances`); }
export async function getStockMovements(slug: string) { return api(`/tenants/${slug}/stock-movements`); }
export async function getReports(slug: string, type: string, params?: string) { return api(`/tenants/${slug}/reports/${type}${params || ''}`); }
export async function getSidebarSettings(slug: string) { return api(`/tenants/${slug}/sidebar-settings`); }
export async function updateSidebarSettings(slug: string, enabledItems: Record<string, boolean>) { return api(`/tenants/${slug}/sidebar-settings`, { method: 'PUT', body: JSON.stringify({ enabledItems }) }); }
