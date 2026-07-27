import { writable } from 'svelte/store';
import type {
  Transaction, Account, JournalEntry, Invoice, Customer,
  Supplier, Product, StockMovement, Branch, Membership,
  AuditEvent, Notification, Tenant, User,
} from '$lib/api/types';
import * as tenantApi from '$lib/api/tenants';
import * as adminApi from '$lib/api/admin';
import { api } from '$lib/api/client';

// ── Transactions ──
export const transactions = writable<Transaction[]>([]);
export async function loadTransactions(slug: string) {
  const res = await tenantApi.getTransactions(slug);
  transactions.set((res as any).items?.map((t: any) => ({
    id: t.id,
    date: t.transactionDate || t.date,
    description: t.description,
    type: t.type,
    amount: parseFloat(t.amount || '0'),
    accountId: t.accountId,
    branchId: t.branchId,
    status: t.status,
    reference: t.reference,
    createdAt: t.createdAt,
    updatedAt: t.updatedAt,
  })) || []);
}
export async function createTransaction(slug: string, data: any) {
  await tenantApi.createTransaction(slug, data);
  await loadTransactions(slug);
}
export async function updateTransaction(slug: string, id: string, data: any) {
  await api(`/tenants/${slug}/transactions/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  await loadTransactions(slug);
}
export async function deleteTransaction(slug: string, id: string) {
  await api(`/tenants/${slug}/transactions/${id}`, { method: 'DELETE' });
  await loadTransactions(slug);
}

// ── Accounts ──
export const accounts = writable<Account[]>([]);
export async function loadAccounts(slug: string) {
  const res = await tenantApi.getAccounts(slug);
  accounts.set((res as any).items?.map((a: any) => ({
    id: a.id,
    code: a.code,
    name: a.name,
    type: a.type,
    balance: parseFloat(a.balance || '0'),
    isSystem: a.isSystem || false,
    status: a.status,
  })) || []);
}
export async function createAccount(slug: string, data: any) {
  await tenantApi.createAccount(slug, data);
  await loadAccounts(slug);
}
export async function updateAccount(slug: string, id: string, data: any) {
  await tenantApi.updateAccount(slug, id, data);
  await loadAccounts(slug);
}
export async function deleteAccount(slug: string, id: string) {
  await tenantApi.deleteAccount(slug, id);
  await loadAccounts(slug);
}

// ── Journal Entries ──
export const journalEntries = writable<JournalEntry[]>([]);
export async function loadJournals(slug: string) {
  const res = await tenantApi.getJournals(slug);
  journalEntries.set((res as any).items?.map((j: any) => ({
    id: j.id,
    date: j.date,
    description: j.description,
    reference: j.reference || '',
    status: j.status,
    lines: (j.lines || []).map((l: any) => ({
      id: l.id,
      accountId: l.accountId,
      accountCode: l.accountCode || '',
      accountName: l.accountName || '',
      description: l.description || '',
      debit: parseFloat(l.debit || '0'),
      credit: parseFloat(l.credit || '0'),
    })),
    createdBy: j.createdBy || '',
    createdAt: j.createdAt,
    approvedBy: j.approvedBy,
    approvedAt: j.approvedAt,
  })) || []);
}

// ── Invoices ──
export const invoices = writable<Invoice[]>([]);
export async function loadInvoices(slug: string) {
  const res = await tenantApi.getInvoices(slug);
  invoices.set((res as any).items?.map((i: any) => ({
    id: i.id,
    number: i.number || i.invoiceNumber || '',
    customerId: i.customerId,
    customerName: i.customerName || '',
    date: i.date,
    dueDate: i.dueDate,
    status: i.status,
    subtotal: parseFloat(i.subtotal || '0'),
    tax: parseFloat(i.tax || '0'),
    total: parseFloat(i.total || '0'),
    paidAmount: parseFloat(i.paidAmount || '0'),
    lines: (i.lines || []).map((l: any) => ({
      id: l.id,
      item: l.item || l.description || '',
      quantity: l.quantity || 0,
      unit: l.unit || 'pcs',
      price: parseFloat(l.price || '0'),
      tax: parseFloat(l.tax || '0'),
      discount: parseFloat(l.discount || '0'),
      total: parseFloat(l.total || '0'),
    })),
    createdAt: i.createdAt,
  })) || []);
}
export async function createInvoice(slug: string, data: any) {
  await tenantApi.createInvoice(slug, data);
  await loadInvoices(slug);
}
export async function updateInvoice(slug: string, id: string, data: any) {
  await tenantApi.updateInvoice(slug, id, data);
  await loadInvoices(slug);
}
export async function deleteInvoice(slug: string, id: string) {
  await api(`/tenants/${slug}/invoices/${id}`, { method: 'DELETE' });
  await loadInvoices(slug);
}

// ── Customers ──
export const customers = writable<Customer[]>([]);
export async function loadCustomers(slug: string) {
  const res = await tenantApi.getCustomers(slug);
  customers.set((res as any).items?.map((c: any) => ({
    id: c.id,
    name: c.name,
    email: c.email || '',
    phone: c.phone || '',
    address: c.address || '',
    createdAt: c.createdAt,
  })) || []);
}
export async function createCustomer(slug: string, data: any) {
  await tenantApi.createCustomer(slug, data);
  await loadCustomers(slug);
}
export async function updateCustomer(slug: string, id: string, data: any) {
  await tenantApi.updateCustomer(slug, id, data);
  await loadCustomers(slug);
}
export async function deleteCustomer(slug: string, id: string) {
  await tenantApi.deleteCustomer(slug, id);
  await loadCustomers(slug);
}

// ── Suppliers ──
export const suppliers = writable<Supplier[]>([]);
export async function loadSuppliers(slug: string) {
  const res = await tenantApi.getSuppliers(slug);
  suppliers.set((res as any).items?.map((s: any) => ({
    id: s.id,
    name: s.name,
    email: s.email || '',
    phone: s.phone || '',
    address: s.address || '',
    createdAt: s.createdAt,
  })) || []);
}
export async function createSupplier(slug: string, data: any) {
  await api(`/tenants/${slug}/suppliers`, { method: 'POST', body: JSON.stringify(data) });
  await loadSuppliers(slug);
}
export async function updateSupplier(slug: string, id: string, data: any) {
  await api(`/tenants/${slug}/suppliers/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  await loadSuppliers(slug);
}
export async function deleteSupplier(slug: string, id: string) {
  await api(`/tenants/${slug}/suppliers/${id}`, { method: 'DELETE' });
  await loadSuppliers(slug);
}

// ── Products ──
export const products = writable<Product[]>([]);
export async function loadProducts(slug: string) {
  const res = await tenantApi.getProducts(slug);
  products.set((res as any).items?.map((p: any) => ({
    id: p.id,
    sku: p.sku || '',
    name: p.name,
    category: p.category || '',
    unit: p.unit || 'pcs',
    price: parseFloat(p.price || '0'),
    cost: parseFloat(p.cost || '0'),
    stock: parseInt(p.stock || '0', 10),
    minStock: parseInt(p.minStock || '0', 10),
    location: p.location || '',
    status: p.status,
  })) || []);
}
export async function createProduct(slug: string, data: any) {
  await api(`/tenants/${slug}/products`, { method: 'POST', body: JSON.stringify(data) });
  await loadProducts(slug);
}
export async function updateProduct(slug: string, id: string, data: any) {
  await api(`/tenants/${slug}/products/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  await loadProducts(slug);
}
export async function deleteProduct(slug: string, id: string) {
  await api(`/tenants/${slug}/products/${id}`, { method: 'DELETE' });
  await loadProducts(slug);
}

// ── Stock Movements ──
export const stockMovements = writable<StockMovement[]>([]);
export async function loadStockMovements(slug: string) {
  const res = await tenantApi.getStockMovements(slug);
  stockMovements.set((res as any).items?.map((m: any) => ({
    id: m.id,
    date: m.date,
    productId: m.productId,
    productName: m.productName || '',
    type: m.type,
    quantity: parseInt(m.quantity || '0', 10),
    beforeStock: parseInt(m.beforeStock || '0', 10),
    afterStock: parseInt(m.afterStock || '0', 10),
    reason: m.reason || '',
    reference: m.reference,
    createdBy: m.createdBy || '',
    createdAt: m.createdAt,
  })) || []);
}

// ── Branches ──
export const branches = writable<Branch[]>([]);
export async function loadBranches(slug: string) {
  const res = await tenantApi.getBranches(slug);
  branches.set((res as any).items?.map((b: any) => ({
    id: b.id,
    name: b.name,
    code: b.code,
    isMain: b.isMain || false,
  })) || []);
}
export async function createBranch(slug: string, data: any) {
  await tenantApi.createBranch(slug, data);
  await loadBranches(slug);
}
export async function updateBranch(slug: string, id: string, data: any) {
  await tenantApi.updateBranch(slug, id, data);
  await loadBranches(slug);
}
export async function deleteBranch(slug: string, id: string) {
  await tenantApi.deleteBranch(slug, id);
  await loadBranches(slug);
}

// ── Members ──
export const members = writable<(Membership & { status: string })[]>([]);
export async function loadMembers(slug: string) {
  const res = await tenantApi.getMembers(slug);
  members.set((res as any).items?.map((m: any) => ({
    tenant: {
      id: m.tenant?.id || m.tenantId || '',
      slug: m.tenant?.slug || '',
      name: m.tenant?.name || '',
      legalName: m.tenant?.legalName || '',
      sector: m.tenant?.sector || '',
      timezone: m.tenant?.timezone || '',
      plan: m.tenant?.plan || '',
      status: m.tenant?.status || 'active',
      createdAt: m.tenant?.createdAt || '',
    },
    user: {
      id: m.user?.id || m.userId || '',
      email: m.user?.email || '',
      name: m.user?.name || '',
      avatar: m.user?.avatar,
    },
    permissions: m.permissions || [],
    role: m.role || '',
    status: m.status || 'active',
  })) || []);
}
export async function addMember(slug: string, data: any) {
  await tenantApi.addMember(slug, data);
  await loadMembers(slug);
}
export async function updateMember(slug: string, id: string, data: any) {
  await tenantApi.updateMember(slug, id, data);
  await loadMembers(slug);
}
export async function removeMember(slug: string, id: string) {
  await tenantApi.removeMember(slug, id);
  await loadMembers(slug);
}

// ── Notifications ──
export const notifications = writable<Notification[]>([]);
export async function loadNotifications(slug: string) {
  const res = await tenantApi.getNotifications(slug);
  notifications.set((res as any).items?.map((n: any) => ({
    id: n.id,
    message: n.message,
    createdAt: n.createdAt,
    read: n.read || false,
    type: n.type || 'info',
    link: n.link,
  })) || []);
}
export async function markNotifRead(slug: string, id: string) {
  await tenantApi.markNotifRead(slug, id);
  await loadNotifications(slug);
}
export async function markAllNotifRead(slug: string) {
  await tenantApi.markAllNotifRead(slug);
  await loadNotifications(slug);
}
export async function deleteNotification(slug: string, id: string) {
  await tenantApi.deleteNotif(slug, id);
  await loadNotifications(slug);
}

// ── Audit Events ──
export const auditEvents = writable<AuditEvent[]>([]);
export async function loadAuditEvents(slug: string) {
  const res = await tenantApi.getAuditEvents(slug);
  auditEvents.set((res as any).items?.map((a: any) => ({
    id: a.id,
    timestamp: a.timestamp || a.createdAt,
    actor: a.actor || '',
    action: a.action,
    module: a.module,
    objectId: a.objectId || '',
    objectType: a.objectType || '',
    before: a.before,
    after: a.after,
    correlationId: a.correlationId,
    integrityVerified: a.integrityVerified,
  })) || []);
}

// ── Admin: Tenants ──
export const adminTenants = writable<Tenant[]>([]);
export async function loadAdminTenants() {
  const res = await adminApi.getAdminTenants();
  adminTenants.set((res as any).items?.map((t: any) => ({
    id: t.id,
    slug: t.slug,
    name: t.name,
    legalName: t.legalName || '',
    sector: t.sector || '',
    timezone: t.timezone || '',
    plan: t.plan || '',
    status: t.status,
    createdAt: t.createdAt,
  })) || []);
}

// ── Admin: Subscription Notifications ──
export type SubscriberNotif = {
  id: string;
  tenantName: string;
  tenantSlug: string;
  buyerName: string;
  buyerEmail: string;
  plan: string;
  amount: number;
  joinedAt: string;
  expiresAt: string;
  status: 'active' | 'expiring' | 'expired';
};
export const subscriberNotifs = writable<SubscriberNotif[]>([]);
export async function loadSubscriberNotifs() {
  const res = await adminApi.getSubscriptionEvents();
  subscriberNotifs.set((res as any).items?.map((s: any) => ({
    id: s.id,
    tenantName: s.tenantName || '',
    tenantSlug: s.tenantSlug || '',
    buyerName: s.buyerName || s.userName || '',
    buyerEmail: s.buyerEmail || s.userEmail || '',
    plan: s.plan || '',
    amount: parseFloat(s.amount || '0'),
    joinedAt: s.joinedAt || s.createdAt,
    expiresAt: s.expiresAt || '',
    status: s.status || 'active',
  })) || []);
}

// ── Admin: Users ──
export const adminUsers = writable<User[]>([]);
export async function loadAdminUsers() {
  const res = await adminApi.getAdminUsers();
  adminUsers.set((res as any).items?.map((u: any) => ({
    id: u.id,
    email: u.email,
    name: u.name,
    avatar: u.avatar,
  })) || []);
}

export { tenantApi, adminApi };
