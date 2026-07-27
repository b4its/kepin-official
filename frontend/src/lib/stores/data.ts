import { writable, get } from 'svelte/store';
import type {
  Transaction, Account, JournalEntry, Invoice, Customer,
  Supplier, Product, StockMovement, Branch, Membership,
  AuditEvent, Notification, Tenant, User,
} from '$lib/api/types';
import * as tenantApi from '$lib/api/tenants';
import * as adminApi from '$lib/api/admin';
import { api } from '$lib/api/client';

let _slug = '';
export function setSlug(slug: string) { _slug = slug; }

// ── Transactions ──
export const transactions = writable<Transaction[]>([]);
export async function loadTransactions(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getTransactions(s);
  transactions.set(res.items?.map((t: any) => ({
    id: t.id, date: t.transactionDate || t.date, description: t.description,
    type: t.type, amount: parseFloat(t.amount || '0'), accountId: t.accountId,
    branchId: t.branchId, status: t.status, reference: t.reference,
    createdAt: t.createdAt, updatedAt: t.updatedAt,
  })) || []);
}
export async function createTransaction(data: any) { const s = _slug; if (!s) return; await tenantApi.createTransaction(s, data); await loadTransactions(s); }
export async function updateTransaction(id: string, data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/transactions/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); await loadTransactions(s); }
export async function deleteTransaction(id: string) { const s = _slug; if (!s) return; await api(`/tenants/${s}/transactions/${id}`, { method: 'DELETE' }); await loadTransactions(s); }

// ── Accounts ──
export const accounts = writable<Account[]>([]);
export async function loadAccounts(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getAccounts(s);
  accounts.set(res.items?.map((a: any) => ({
    id: a.id, code: a.code, name: a.name, type: a.type,
    balance: parseFloat(a.balance || '0'), isSystem: a.isSystem || false, status: a.status,
  })) || []);
}
export async function createAccount(data: any) { const s = _slug; if (!s) return; await tenantApi.createAccount(s, data); await loadAccounts(s); }
export async function updateAccount(id: string, data: any) { const s = _slug; if (!s) return; await tenantApi.updateAccount(s, id, data); await loadAccounts(s); }
export async function deleteAccount(id: string) { const s = _slug; if (!s) return; await tenantApi.deleteAccount(s, id); await loadAccounts(s); }

// ── Journal Entries ──
export const journalEntries = writable<JournalEntry[]>([]);
export async function loadJournals(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getJournals(s);
  journalEntries.set(res.items?.map((j: any) => ({
    id: j.id, date: j.date, description: j.description, reference: j.reference || '',
    status: j.status,
    lines: (j.lines || []).map((l: any) => ({
      id: l.id, accountId: l.accountId, accountCode: l.accountCode || '', accountName: l.accountName || '',
      description: l.description || '', debit: parseFloat(l.debit || '0'), credit: parseFloat(l.credit || '0'),
    })),
    createdBy: j.createdBy || '', createdAt: j.createdAt, approvedBy: j.approvedBy, approvedAt: j.approvedAt,
  })) || []);
}

// ── Invoices ──
export const invoices = writable<Invoice[]>([]);
export async function loadInvoices(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getInvoices(s);
  invoices.set(res.items?.map((i: any) => ({
    id: i.id, number: i.number || i.invoiceNumber || '', customerId: i.customerId,
    customerName: i.customerName || '', date: i.date, dueDate: i.dueDate, status: i.status,
    subtotal: parseFloat(i.subtotal || '0'), tax: parseFloat(i.tax || '0'), total: parseFloat(i.total || '0'),
    paidAmount: parseFloat(i.paidAmount || '0'),
    lines: (i.lines || []).map((l: any) => ({
      id: l.id, item: l.item || l.description || '', quantity: l.quantity || 0,
      unit: l.unit || 'pcs', price: parseFloat(l.price || '0'),
      tax: parseFloat(l.tax || '0'), discount: parseFloat(l.discount || '0'), total: parseFloat(l.total || '0'),
    })),
    createdAt: i.createdAt,
  })) || []);
}
export async function createInvoice(data: any) { const s = _slug; if (!s) return; await tenantApi.createInvoice(s, data); await loadInvoices(s); }
export async function updateInvoice(id: string, data: any) { const s = _slug; if (!s) return; await tenantApi.updateInvoice(s, id, data); await loadInvoices(s); }
export async function deleteInvoice(id: string) { const s = _slug; if (!s) return; await api(`/tenants/${s}/invoices/${id}`, { method: 'DELETE' }); await loadInvoices(s); }

// ── Customers ──
export const customers = writable<Customer[]>([]);
export async function loadCustomers(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getCustomers(s);
  customers.set(res.items?.map((c: any) => ({
    id: c.id, name: c.name, email: c.email || '', phone: c.phone || '', address: c.address || '', createdAt: c.createdAt,
  })) || []);
}
export async function createCustomer(data: any) { const s = _slug; if (!s) return; await tenantApi.createCustomer(s, data); await loadCustomers(s); }
export async function updateCustomer(id: string, data: any) { const s = _slug; if (!s) return; await tenantApi.updateCustomer(s, id, data); await loadCustomers(s); }
export async function deleteCustomer(id: string) { const s = _slug; if (!s) return; await tenantApi.deleteCustomer(s, id); await loadCustomers(s); }

// ── Suppliers ──
export const suppliers = writable<Supplier[]>([]);
export async function loadSuppliers(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getSuppliers(s);
  suppliers.set(res.items?.map((s: any) => ({
    id: s.id, name: s.name, email: s.email || '', phone: s.phone || '', address: s.address || '', createdAt: s.createdAt,
  })) || []);
}
export async function createSupplier(data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/suppliers`, { method: 'POST', body: JSON.stringify(data) }); await loadSuppliers(s); }
export async function updateSupplier(id: string, data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/suppliers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); await loadSuppliers(s); }
export async function deleteSupplier(id: string) { const s = _slug; if (!s) return; await api(`/tenants/${s}/suppliers/${id}`, { method: 'DELETE' }); await loadSuppliers(s); }

// ── Products ──
export const products = writable<Product[]>([]);
export async function loadProducts(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getProducts(s);
  products.set(res.items?.map((p: any) => ({
    id: p.id, sku: p.sku || '', name: p.name, category: p.category || '',
    unit: p.unit || 'pcs', price: parseFloat(p.price || '0'), cost: parseFloat(p.cost || '0'),
    stock: parseInt(p.stock || '0', 10), minStock: parseInt(p.minStock || '0', 10),
    location: p.location || '', status: p.status,
  })) || []);
}
export async function createProduct(data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/products`, { method: 'POST', body: JSON.stringify(data) }); await loadProducts(s); }
export async function updateProduct(id: string, data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/products/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); await loadProducts(s); }
export async function deleteProduct(id: string) { const s = _slug; if (!s) return; await api(`/tenants/${s}/products/${id}`, { method: 'DELETE' }); await loadProducts(s); }

// ── Stock Movements ──
export const stockMovements = writable<StockMovement[]>([]);
export async function loadStockMovements(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getStockMovements(s);
  stockMovements.set(res.items?.map((m: any) => ({
    id: m.id, date: m.date, productId: m.productId, productName: m.productName || '',
    type: m.type, quantity: parseInt(m.quantity || '0', 10),
    beforeStock: parseInt(m.beforeStock || '0', 10), afterStock: parseInt(m.afterStock || '0', 10),
    reason: m.reason || '', reference: m.reference, createdBy: m.createdBy || '', createdAt: m.createdAt,
  })) || []);
}

// ── Branches ──
export const branches = writable<Branch[]>([]);
export async function loadBranches(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getBranches(s);
  branches.set(res.items?.map((b: any) => ({
    id: b.id, name: b.name, code: b.code, isMain: b.isMain || false,
  })) || []);
}
export async function createBranch(data: any) { const s = _slug; if (!s) return; await tenantApi.createBranch(s, data); await loadBranches(s); }
export async function updateBranch(id: string, data: any) { const s = _slug; if (!s) return; await tenantApi.updateBranch(s, id, data); await loadBranches(s); }
export async function deleteBranch(id: string) { const s = _slug; if (!s) return; await tenantApi.deleteBranch(s, id); await loadBranches(s); }

// ── Members ──
export const members = writable<any[]>([]);
export async function loadMembers(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getMembers(s);
  members.set(res.items?.map((m: any) => ({
    id: m.id,
    tenant: { id: m.tenant?.id || m.tenantId || '', slug: m.tenant?.slug || '', name: m.tenant?.name || '', legalName: m.tenant?.legalName || '', sector: m.tenant?.sector || '', timezone: m.tenant?.timezone || '', plan: m.tenant?.plan || '', status: m.tenant?.status || 'active', createdAt: m.tenant?.createdAt || '' },
    user: { id: m.user?.id || m.userId || '', email: m.user?.email || '', name: m.user?.name || '', avatar: m.user?.avatar },
    permissions: m.permissions || [], role: m.role || '', status: m.status || 'active',
  })) || []);
}
export async function addMember(data: any) { const s = _slug; if (!s) return; await tenantApi.addMember(s, data); await loadMembers(s); }
export async function updateMember(idx: number, data: any) {
  const s = _slug; if (!s) return;
  const list = get(members);
  const id = list[idx]?.id; if (!id) return;
  await tenantApi.updateMember(s, id, data); await loadMembers(s);
}
export async function removeMember(idx: number) {
  const s = _slug; if (!s) return;
  const list = get(members);
  const id = list[idx]?.id; if (!id) return;
  await tenantApi.removeMember(s, id); await loadMembers(s);
}
// alias for pages that use deleteMember
export { addMember as createMember };
export { removeMember as deleteMember };

// ── Notifications ──
export const notifications = writable<Notification[]>([]);
export async function loadNotifications(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getNotifications(s);
  notifications.set(res.items?.map((n: any) => ({
    id: n.id, message: n.message, createdAt: n.createdAt,
    read: n.read || false, type: n.type || 'info', link: n.link,
  })) || []);
}
export async function markNotifRead(id: string) { const s = _slug; if (!s) return; await tenantApi.markNotifRead(s, id); await loadNotifications(s); }
export async function markAllNotifRead() { const s = _slug; if (!s) return; await tenantApi.markAllNotifRead(s); await loadNotifications(s); }
export async function deleteNotification(id: string) { const s = _slug; if (!s) return; await tenantApi.deleteNotif(s, id); await loadNotifications(s); }

// ── Audit Events ──
export const auditEvents = writable<AuditEvent[]>([]);
export async function loadAuditEvents(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getAuditEvents(s);
  auditEvents.set(res.items?.map((a: any) => ({
    id: a.id, timestamp: a.timestamp || a.createdAt, actor: a.actor || '',
    action: a.action, module: a.module, objectId: a.objectId || '',
    objectType: a.objectType || '', before: a.before, after: a.after,
    correlationId: a.correlationId, integrityVerified: a.integrityVerified,
  })) || []);
}

// ── Admin: Tenants ──
export const adminTenants = writable<Tenant[]>([]);
export async function loadAdminTenants() {
  const res: any = await adminApi.getAdminTenants();
  adminTenants.set(res.items?.map((t: any) => ({
    id: t.id, slug: t.slug, name: t.name, legalName: t.legalName || '',
    sector: t.sector || '', timezone: t.timezone || '',
    plan: t.plan || '', status: t.status, createdAt: t.createdAt,
  })) || []);
}

// ── Admin: Subscription Notifications ──
export type SubscriberNotif = { id: string; tenantName: string; tenantSlug: string; buyerName: string; buyerEmail: string; plan: string; amount: number; joinedAt: string; expiresAt: string; status: 'active' | 'expiring' | 'expired'; };
export const subscriberNotifs = writable<SubscriberNotif[]>([]);
export async function loadSubscriberNotifs() {
  const res: any = await adminApi.getSubscriptionEvents();
  subscriberNotifs.set(res.items?.map((s: any) => ({
    id: s.id, tenantName: s.tenantName || '', tenantSlug: s.tenantSlug || '',
    buyerName: s.buyerName || s.userName || '', buyerEmail: s.buyerEmail || s.userEmail || '',
    plan: s.plan || '', amount: parseFloat(s.amount || '0'),
    joinedAt: s.joinedAt || s.createdAt, expiresAt: s.expiresAt || '',
    status: s.status || 'active',
  })) || []);
}

// ── Admin: Users ──
export const adminUsers = writable<User[]>([]);
export async function loadAdminUsers() {
  const res: any = await adminApi.getAdminUsers();
  adminUsers.set(res.items?.map((u: any) => ({
    id: u.id, email: u.email, name: u.name, avatar: u.avatar,
  })) || []);
}

// ── Also export tenantApi helper for pages that need direct API access ──
// (already available as import { tenantApi } from '$lib/stores/data')
export { tenantApi, adminApi, api };

// ── Current role in the active tenant ──
export const currentRole = writable<'tenant_owner' | 'employee' | null>(null);
export function setCurrentRole(role: 'tenant_owner' | 'employee' | null) {
  currentRole.set(role);
}

// ── Sidebar settings (key → enabled bool; absent = true) ──
export const sidebarSettings = writable<Record<string, boolean>>({});

export async function loadSidebarSettings(slug?: string) {
  const s = slug || _slug;
  if (!s) return;
  try {
    const res: any = await tenantApi.getSidebarSettings(s);
    sidebarSettings.set(res.enabledItems || {});
  } catch {
    sidebarSettings.set({});
  }
}

export async function saveSidebarSettings(items: Record<string, boolean>, slug?: string) {
  const s = slug || _slug;
  if (!s) return;
  await tenantApi.updateSidebarSettings(s, items);
  sidebarSettings.set(items);
}

/** Returns true if the nav item key is enabled (default true when not configured). */
export function isNavEnabled(settings: Record<string, boolean>, key: string): boolean {
  return settings[key] !== false;
}
