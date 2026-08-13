import { api } from './client';
import { createId } from '$lib/utils/id';

export async function getTenantContext(slug: string) { return api(`/tenants/${slug}/context`); }
export async function getTenantDashboard(slug: string, params?: { preset?: string; startDate?: string; endDate?: string }) {
  const search = new URLSearchParams();
  if (params?.preset) search.set('preset', params.preset);
  if (params?.startDate) search.set('startDate', params.startDate);
  if (params?.endDate) search.set('endDate', params.endDate);
  const query = search.size ? `?${search}` : '';
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
export async function createIntegration(slug: string, data: { provider: string; displayName: string }) { return api(`/tenants/${slug}/integrations`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateIntegration(slug: string, id: string, data: { displayName?: string; status?: string }) { return api(`/tenants/${slug}/integrations/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function syncIntegration(slug: string, id: string, data: { bankAccountId: string; transactions: Array<{ externalId: string; transactionDate: string; description?: string; amount: string }> }) { return api(`/tenants/${slug}/integrations/${id}/sync`, { method: 'POST', body: JSON.stringify(data) }); }
export async function getBilling(slug: string) { return api(`/tenants/${slug}/billing`); }
export async function getBillingHistory(slug: string) { return api(`/tenants/${slug}/billing-history`); }
export async function getNotifications(slug: string) { return api(`/tenants/${slug}/notifications?pageSize=100`); }
export async function getNotification(slug: string, id: string) { return api(`/tenants/${slug}/notifications/${id}`); }
export async function markNotifRead(slug: string, id: string) { return api(`/tenants/${slug}/notifications/${id}/read`, { method: 'PATCH' }); }
export async function markAllNotifRead(slug: string) { return api(`/tenants/${slug}/notifications/read-all`, { method: 'POST' }); }
export async function deleteNotif(slug: string, id: string) { return api(`/tenants/${slug}/notifications/${id}`, { method: 'DELETE' }); }
export async function getAuditEvents(slug: string, params?: { objectType?: string; action?: string; pageSize?: number }) {
  const q = new URLSearchParams();
  if (params?.objectType) q.set('objectType', params.objectType);
  if (params?.action) q.set('action', params.action);
  if (params?.pageSize) q.set('pageSize', String(params.pageSize));
  const qs = q.toString();
  return api(`/tenants/${slug}/audit-events${qs ? `?${qs}` : ''}`);
}
export async function getAuditEventTypes(slug: string) { return api(`/tenants/${slug}/audit-events/types`); }
export async function getAccounts(slug: string) { return api(`/tenants/${slug}/accounts`); }
export async function getAccountBalance(slug: string, id: string) { return api(`/tenants/${slug}/accounts/${id}/balance`); }
export async function createAccount(slug: string, data: any) { return api(`/tenants/${slug}/accounts`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateAccount(slug: string, id: string, data: any) { return api(`/tenants/${slug}/accounts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteAccount(slug: string, id: string) { return api(`/tenants/${slug}/accounts/${id}`, { method: 'DELETE' }); }
export async function getTransactions(slug: string, params?: string) { return api(`/tenants/${slug}/transactions${params || ''}${params?.includes('pageSize') ? '' : (params ? '&' : '?')}pageSize=100`); }
export async function createTransaction(slug: string, data: any) { return api(`/tenants/${slug}/transactions`, { method: 'POST', body: JSON.stringify(data) }); }
export async function postTransaction(slug: string, id: string) { return api(`/tenants/${slug}/transactions/${id}/post`, { method: 'POST' }); }
export async function voidTransaction(slug: string, id: string) { return api(`/tenants/${slug}/transactions/${id}/void`, { method: 'POST' }); }
export async function getJournals(slug: string, params?: string) { return api(`/tenants/${slug}/journals${params || ''}${params?.includes('pageSize') ? '' : (params ? '&' : '?')}pageSize=100`); }
export async function getLedger(slug: string, params?: string) { return api(`/tenants/${slug}/journals/ledger${params || ''}`); }
export async function createJournal(slug: string, data: { journalDate: string; reference?: string; description?: string; lines: { accountId: string; description?: string; debit: string; credit: string }[] }) { return api(`/tenants/${slug}/journals`, { method: 'POST', body: JSON.stringify(data) }); }
export async function postJournal(slug: string, id: string) { return api(`/tenants/${slug}/journals/${id}/post`, { method: 'POST', headers: { 'X-Idempotency-Key': createId() } }); }
export async function reverseJournal(slug: string, id: string) { return api(`/tenants/${slug}/journals/${id}/reverse`, { method: 'POST' }); }
export async function getBankAccounts(slug: string) { return api(`/tenants/${slug}/bank-accounts`); }
export async function createBankAccount(slug: string, data: { accountId: string; bankName: string; maskedNumber?: string }) { return api(`/tenants/${slug}/bank-accounts`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateBankAccount(slug: string, id: string, data: { bankName?: string; maskedNumber?: string; status?: string }) { return api(`/tenants/${slug}/bank-accounts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteBankAccount(slug: string, id: string) { return api(`/tenants/${slug}/bank-accounts/${id}`, { method: 'DELETE' }); }
export async function getBankTransactions(slug: string, params?: string) { return api(`/tenants/${slug}/bank-transactions${params || ''}`); }
export async function getCustomerStatement(slug: string, customerId: string, params?: string) { return api(`/tenants/${slug}/customer-statements?customerId=${customerId}${params || ''}`); }
export async function getSupplierStatement(slug: string, supplierId: string, params?: string) { return api(`/tenants/${slug}/supplier-statements?supplierId=${supplierId}${params || ''}`); }
export async function createBankTransaction(slug: string, data: { bankAccountId: string; externalId: string; transactionDate: string; description?: string; amount: string }) { return api(`/tenants/${slug}/bank-transactions`, { method: 'POST', body: JSON.stringify(data) }); }
export async function importBankTransactionsCsv(slug: string, data: { bankAccountId: string; csv: string }) { return api(`/tenants/${slug}/bank-transactions/import`, { method: 'POST', body: JSON.stringify(data) }); }
export async function deleteBankTransaction(slug: string, id: string) { return api(`/tenants/${slug}/bank-transactions/${id}`, { method: 'DELETE' }); }
export async function getFiscalYears(slug: string) { return api(`/tenants/${slug}/fiscal-years`); }
export async function createFiscalYear(slug: string, data: { name?: string; startDate: string; endDate: string }) { return api(`/tenants/${slug}/fiscal-years`, { method: 'POST', body: JSON.stringify(data) }); }
export async function closeFiscalYear(slug: string, id: string) { return api(`/tenants/${slug}/fiscal-years/${id}/close`, { method: 'POST' }); }
export async function reopenFiscalYear(slug: string, id: string) { return api(`/tenants/${slug}/fiscal-years/${id}/reopen`, { method: 'POST' }); }
export async function closePeriod(slug: string, id: string) { return api(`/tenants/${slug}/periods/${id}/close`, { method: 'POST' }); }
export async function reopenPeriod(slug: string, id: string) { return api(`/tenants/${slug}/periods/${id}/reopen`, { method: 'POST' }); }
export async function createReconciliationMatch(slug: string, data: { bankTransactionId: string; transactionId: string; confidence?: string; note?: string }) { return api(`/tenants/${slug}/reconciliation/matches`, { method: 'POST', body: JSON.stringify(data) }); }
export async function confirmReconciliationMatch(slug: string, id: string) { return api(`/tenants/${slug}/reconciliation/matches/${id}/confirm`, { method: 'POST' }); }
export async function getReconciliationSuggestions(slug: string, params?: string) { return api(`/tenants/${slug}/reconciliation/suggestions${params || ''}`); }
export async function bulkAutoMatch(slug: string, data: { bankAccountId?: string; minScore?: number; maxStatements?: number }) { return api(`/tenants/${slug}/reconciliation/matches/bulk`, { method: 'POST', body: JSON.stringify(data) }); }
export async function getCustomers(slug: string, search?: string) { return api(`/tenants/${slug}/customers?pageSize=100${search ? `&search=${encodeURIComponent(search)}` : ''}`); }
export async function createCustomer(slug: string, data: any) { return api(`/tenants/${slug}/customers`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateCustomer(slug: string, id: string, data: any) { return api(`/tenants/${slug}/customers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteCustomer(slug: string, id: string) { return api(`/tenants/${slug}/customers/${id}`, { method: 'DELETE' }); }
export async function getInvoices(slug: string, params?: string) { return api(`/tenants/${slug}/invoices${params || ''}${params?.includes('pageSize') ? '' : (params ? '&' : '?')}pageSize=100`); }
export async function createInvoice(slug: string, data: any) { return api(`/tenants/${slug}/invoices`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateInvoice(slug: string, id: string, data: any) { return api(`/tenants/${slug}/invoices/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteInvoice(slug: string, id: string) { return api(`/tenants/${slug}/invoices/${id}`, { method: 'DELETE' }); }
export async function postInvoice(slug: string, id: string) { return api(`/tenants/${slug}/invoices/${id}/post`, { method: 'POST', headers: { 'X-Idempotency-Key': createId() } }); }
export async function reverseInvoice(slug: string, id: string) { return api(`/tenants/${slug}/invoices/${id}/reverse`, { method: 'POST' }); }
export async function getSuppliers(slug: string) { return api(`/tenants/${slug}/suppliers?pageSize=100`); }
export async function createSupplier(slug: string, data: any) { return api(`/tenants/${slug}/suppliers`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updateSupplier(slug: string, id: string, data: any) { return api(`/tenants/${slug}/suppliers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deleteSupplier(slug: string, id: string) { return api(`/tenants/${slug}/suppliers/${id}`, { method: 'DELETE' }); }
export async function getPurchaseOrders(slug: string) { return api(`/tenants/${slug}/purchase-orders?pageSize=100`); }
export async function createPurchaseOrder(slug: string, data: any) { return api(`/tenants/${slug}/purchase-orders`, { method: 'POST', body: JSON.stringify(data) }); }
export async function updatePurchaseOrder(slug: string, id: string, data: any) { return api(`/tenants/${slug}/purchase-orders/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); }
export async function deletePurchaseOrder(slug: string, id: string) { return api(`/tenants/${slug}/purchase-orders/${id}`, { method: 'DELETE' }); }
export async function sendPurchaseOrder(slug: string, id: string) { return api(`/tenants/${slug}/purchase-orders/${id}/send`, { method: 'POST' }); }
export async function receivePurchaseOrder(slug: string, id: string, data: { locationId: string; lines: { line_id: string; quantity_received: string }[]; notes?: string }) { return api(`/tenants/${slug}/purchase-orders/${id}/receive`, { method: 'POST', body: JSON.stringify(data) }); }
export async function cancelPurchaseOrder(slug: string, id: string) { return api(`/tenants/${slug}/purchase-orders/${id}/cancel`, { method: 'POST' }); }
export async function getInventoryLocations(slug: string) { return api(`/tenants/${slug}/inventory-locations`); }
export async function getSupplierPayments(slug: string) { return api(`/tenants/${slug}/supplier-payments?pageSize=100`); }
export async function createSupplierPayment(slug: string, data: { supplierId: string; paymentDate: string; amount: string; method?: string; reference?: string }) { return api(`/tenants/${slug}/supplier-payments`, { method: 'POST', body: JSON.stringify(data) }); }
export async function postSupplierPayment(slug: string, id: string) { return api(`/tenants/${slug}/supplier-payments/${id}/post`, { method: 'POST' }); }
export async function voidSupplierPayment(slug: string, id: string) { return api(`/tenants/${slug}/supplier-payments/${id}/void`, { method: 'POST' }); }
export async function getProducts(slug: string, search?: string, pageSize?: number, page?: number) { return api(`/tenants/${slug}/products?${search ? `search=${encodeURIComponent(search)}&` : ''}${pageSize ? `pageSize=${pageSize}&` : ''}${page ? `page=${page}` : ''}`); }
export async function getStockBalances(slug: string) { return api(`/tenants/${slug}/stock-balances`); }
export async function getStockMovements(slug: string) { return api(`/tenants/${slug}/stock-movements?pageSize=100`); }
export async function createStockReceipt(slug: string, data: { productId: string; locationId: string; quantity: string; unitCost?: string; reason?: string }) { return api(`/tenants/${slug}/stock-movements/receipts`, { method: 'POST', body: JSON.stringify({ product_id: data.productId, location_id: data.locationId, quantity: data.quantity, unit_cost: data.unitCost || '0', reason: data.reason || '' }) }); }
export async function createStockIssue(slug: string, data: { productId: string; locationId: string; quantity: string; reason?: string }) { return api(`/tenants/${slug}/stock-movements/issues`, { method: 'POST', body: JSON.stringify({ product_id: data.productId, location_id: data.locationId, quantity: data.quantity, reason: data.reason || '' }) }); }
export async function createPosCheckout(slug: string, data: { items: { product_id: string; quantity: string }[]; reason?: string }) { return api(`/tenants/${slug}/pos/checkout`, { method: 'POST', body: JSON.stringify(data) }); }
export async function getReports(slug: string, type: string, params?: string) { return api(`/tenants/${slug}/reports/${type}${params || ''}`); }
export async function getSidebarSettings(slug: string) { return api(`/tenants/${slug}/sidebar-settings`); }
export async function updateSidebarSettings(slug: string, enabledItems: Record<string, boolean>) { return api(`/tenants/${slug}/sidebar-settings`, { method: 'PUT', body: JSON.stringify({ enabledItems }) }); }
