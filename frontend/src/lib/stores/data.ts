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
export function setSlug(slug: string) {
  if (_slug !== slug) {
    _slug = slug;
    clearTenantStores();
  } else {
    _slug = slug;
  }
}

function isActiveTenant(slug: string): boolean {
  return Boolean(slug) && slug === _slug;
}

export function clearTenantStores() {
  transactions.set([]);
  accounts.set([]);
  journalEntries.set([]);
  invoices.set([]);
  customers.set([]);
  suppliers.set([]);
  products.set([]);
  purchaseOrders.set([]);
  stockMovements.set([]);
  branches.set([]);
  inventoryLocations.set([]);
  members.set([]);
  notifications.set([]);
  auditEvents.set([]);
  supplierPayments.set([]);
  sidebarSettings.set({});
  currentRole.set(null);
}

// ── Transactions ──
export const transactions = writable<Transaction[]>([]);
export async function loadTransactions(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getTransactions(s);
  if (!isActiveTenant(s)) return;
  transactions.set(res.items?.map((t: any) => ({
    id: t.id, date: t.transactionDate || t.date, description: t.description,
    type: t.type, amount: parseFloat(t.amount || '0'), accountId: t.accountId,
    counterAccountId: t.counterAccountId, branchId: t.branchId, status: t.status, reference: t.reference,
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
  if (!isActiveTenant(s)) return;
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
export async function loadJournals(slug?: string, params?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getJournals(s, params);
  if (!isActiveTenant(s)) return;
  journalEntries.set(res.items?.map((j: any) => ({
    id: j.id, date: j.date || j.journalDate || j.journal_date, description: j.description, reference: j.reference || j.journalNumber || j.journal_number || '',
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
  if (!isActiveTenant(s)) return;
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
  if (!isActiveTenant(s)) return;
  customers.set(res.items?.map((c: any) => ({
    id: c.id, code: c.code || '', name: c.name, email: c.email || '', phone: c.phone || '', address: c.address || '', createdAt: c.createdAt,
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
  if (!isActiveTenant(s)) return;
  suppliers.set(res.items?.map((s: any) => ({
    id: s.id, code: s.code || '', name: s.name, email: s.email || '', phone: s.phone || '', address: s.address || '', createdAt: s.createdAt,
  })) || []);
}
export async function createSupplier(data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/suppliers`, { method: 'POST', body: JSON.stringify(data) }); await loadSuppliers(s); }
export async function updateSupplier(id: string, data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/suppliers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); await loadSuppliers(s); }
export async function deleteSupplier(id: string) { const s = _slug; if (!s) return; await api(`/tenants/${s}/suppliers/${id}`, { method: 'DELETE' }); await loadSuppliers(s); }

// ── Products ──
export const products = writable<Product[]>([]);
export async function loadProducts(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getProducts(s, undefined, 100);
  if (!isActiveTenant(s)) return;
  products.set(res.items?.map((p: any) => ({
    id: p.id, sku: p.sku || '', name: p.name, category: p.category || '',
    unit: p.unit || 'pcs', price: parseFloat(p.salePrice || p.sale_price || '0'), cost: parseFloat(p.costPrice || p.cost_price || '0'),
    stock: parseFloat(p.stock || '0'), minStock: parseFloat(p.minimumStock || p.minimum_stock || '0'),
    location: p.location || '', status: p.status,
  })) || []);
}
export async function createProduct(data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/products`, { method: 'POST', body: JSON.stringify(data) }); await loadProducts(s); }
export async function updateProduct(id: string, data: any) { const s = _slug; if (!s) return; await api(`/tenants/${s}/products/${id}`, { method: 'PATCH', body: JSON.stringify(data) }); await loadProducts(s); }
export async function deleteProduct(id: string) { const s = _slug; if (!s) return; await api(`/tenants/${s}/products/${id}`, { method: 'DELETE' }); await loadProducts(s); }

// ── Purchase Orders ──
export const purchaseOrders = writable<any[]>([]);
export async function loadPurchaseOrders(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getPurchaseOrders(s);
  if (!isActiveTenant(s)) return;
  purchaseOrders.set(res.items?.map((p: any) => ({
    id: p.id, number: p.po_number || p.poNumber || '', supplierId: p.supplier_id || p.supplierId || '',
    supplierName: p.supplier_name || p.supplierName || '', date: p.order_date || p.orderDate || '',
    expectedDate: p.expected_date || p.expectedDate || '', notes: p.notes || '',
    subtotal: parseFloat(p.subtotal || '0'), total: parseFloat(p.total || '0'), status: p.status || 'draft',
    lines: (p.lines || []).map((l: any) => ({
      id: l.id, productId: l.product_id || l.productId || '', itemName: l.item_name || l.itemName || '',
      quantity: parseFloat(l.quantity || '0'), receivedQuantity: parseFloat(l.received_quantity || l.receivedQuantity || '0'),
      unitPrice: parseFloat(l.unit_price || l.unitPrice || '0'), lineTotal: parseFloat(l.line_total || l.lineTotal || '0'),
      lineNumber: l.line_number || l.lineNumber || 0,
    })),
  })) || []);
}
export async function createPurchaseOrder(data: any) { const s = _slug; if (!s) return; await tenantApi.createPurchaseOrder(s, data); await loadPurchaseOrders(s); }
export async function updatePurchaseOrder(id: string, data: any) { const s = _slug; if (!s) return; await tenantApi.updatePurchaseOrder(s, id, data); await loadPurchaseOrders(s); }
export async function deletePurchaseOrder(id: string) { const s = _slug; if (!s) return; await tenantApi.deletePurchaseOrder(s, id); await loadPurchaseOrders(s); }
export async function sendPurchaseOrder(id: string) { const s = _slug; if (!s) return; await tenantApi.sendPurchaseOrder(s, id); await loadPurchaseOrders(s); }
export async function receivePurchaseOrder(id: string, data: { locationId: string; lines: { line_id: string; quantity_received: string }[]; notes?: string }) { const s = _slug; if (!s) return; await tenantApi.receivePurchaseOrder(s, id, data); await loadPurchaseOrders(s); }
export async function cancelPurchaseOrder(id: string) { const s = _slug; if (!s) return; await tenantApi.cancelPurchaseOrder(s, id); await loadPurchaseOrders(s); }

// ── Inventory Locations ──
export const inventoryLocations = writable<any[]>([]);
export async function loadInventoryLocations(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getInventoryLocations(s);
  if (!isActiveTenant(s)) return;
  inventoryLocations.set((Array.isArray(res) ? res : []).map((l: any) => ({
    id: l.id, code: l.code || '', name: l.name, status: l.status || 'active', branchId: l.branch_id || l.branchId || '',
  })) || []);
}

// ── Supplier Payments ──
export const supplierPayments = writable<any[]>([]);
export async function loadSupplierPayments(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getSupplierPayments(s);
  if (!isActiveTenant(s)) return;
  supplierPayments.set(res.items?.map((p: any) => ({
    id: p.id, number: p.paymentNumber || p.payment_number || '', date: p.paymentDate || p.payment_date || '',
    amount: parseFloat(p.amount || '0'), method: p.method || 'cash', reference: p.reference || '',
    status: p.status || 'draft', supplierId: p.supplierId || p.supplier_id || '',
    branchId: p.branchId || '', journalEntryId: p.journalEntryId || '', createdAt: p.createdAt,
  })) || []);
}
export async function createSupplierPayment(data: any) { const s = _slug; if (!s) return; await tenantApi.createSupplierPayment(s, data); await loadSupplierPayments(s); }
export async function postSupplierPayment(id: string) { const s = _slug; if (!s) return; await tenantApi.postSupplierPayment(s, id); await loadSupplierPayments(s); }
export async function voidSupplierPayment(id: string) { const s = _slug; if (!s) return; await tenantApi.voidSupplierPayment(s, id); await loadSupplierPayments(s); }

// ── Stock Movements ──
export const stockMovements = writable<StockMovement[]>([]);
export async function loadStockMovements(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getStockMovements(s);
  if (!isActiveTenant(s)) return;
  stockMovements.set(res.items?.map((m: any) => ({
    id: m.id, date: m.movementDate || m.movement_date || m.date || '', productId: m.productId || m.product_id || '', productName: m.productName || m.product_name || '',
    type: m.type, quantity: parseFloat(m.quantity || '0'),
    beforeStock: parseFloat(m.beforeStock || m.before_stock || '0'), afterStock: parseFloat(m.afterStock || m.after_stock || '0'),
    reason: m.reason || '', reference: m.reference, createdBy: m.createdBy || '', createdAt: m.createdAt,
  })) || []);
}

// ── Branches ──
export const branches = writable<Branch[]>([]);
export async function loadBranches(slug?: string) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getBranches(s);
  if (!isActiveTenant(s)) return;
  branches.set((Array.isArray(res) ? res : res.items || []).map((b: any) => ({
    id: b.id, name: b.name, code: b.code, address: b.address || '', isMain: b.isMain || b.is_main || false,
    status: b.status || 'active',
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
  if (!isActiveTenant(s)) return;
  members.set((Array.isArray(res) ? res : res.items || []).map((m: any) => ({
    id: m.id,
    tenant: { id: m.tenant?.id || m.tenantId || '', slug: m.tenant?.slug || '', name: m.tenant?.name || '', legalName: m.tenant?.legalName || '', sector: m.tenant?.sector || '', timezone: m.tenant?.timezone || '', plan: m.tenant?.plan || '', status: m.tenant?.status || 'active', createdAt: m.tenant?.createdAt || '' },
    user: { id: m.user?.id || m.userId || '', email: m.user?.email || m.userEmail || m.user_email || '', name: m.user?.name || m.userName || m.user_name || '', avatar: m.user?.avatar },
    permissions: m.permissions || [], role: m.roleName || m.role_name || m.role || '', status: m.status || 'active',
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
  if (!isActiveTenant(s)) return;
  notifications.set(res.items?.map((n: any) => ({
    id: n.id, title: n.title || '', message: n.message || '', createdAt: n.createdAt || n.created_at || '',
    read: Boolean(n.readAt || n.read_at), type: n.type || 'info', link: n.link, metadata: n.metadata,
  })) || []);
}
export async function markNotifRead(id: string) { const s = _slug; if (!s) return; await tenantApi.markNotifRead(s, id); await loadNotifications(s); }
export async function markAllNotifRead() { const s = _slug; if (!s) return; await tenantApi.markAllNotifRead(s); await loadNotifications(s); }
export async function deleteNotification(id: string) { const s = _slug; if (!s) return; await tenantApi.deleteNotif(s, id); await loadNotifications(s); }

// ── Audit Events ──
export const auditEvents = writable<AuditEvent[]>([]);
export async function loadAuditEvents(slug?: string, filters?: { objectType?: string; action?: string }) {
  const s = slug || _slug; if (!s) return;
  const res: any = await tenantApi.getAuditEvents(s, { ...filters, pageSize: 100 });
  if (!isActiveTenant(s)) return;
  auditEvents.set(res.items?.map((a: any) => ({
    id: a.id, timestamp: a.timestamp || '', actor: a.actorName || a.actor_name || '',
    action: a.action, module: a.module || '', objectId: a.objectId || a.object_id || '',
    objectType: a.objectType || a.object_type || '', before: a.before, after: a.after,
    requestId: a.requestId || a.request_id || '', correlationId: a.correlationId || a.correlation_id || '',
    integrityHash: a.integrityHash || a.integrity_hash || '',
  })) || []);
}

// ── Admin: Platform Audit ──
export const platformAuditEvents = writable<AuditEvent[]>([]);
export async function loadPlatformAudit() {
  const res: any = await adminApi.getPlatformAudit();
  platformAuditEvents.set(res.items?.map((a: any) => ({
    id: a.id, timestamp: a.timestamp || '', actor: a.actorName || '',
    action: a.action, module: a.objectType || '',
    objectId: a.objectId || '', before: a.before, after: a.after,
    correlationId: a.correlationId || '',
  })) || []);
}

// ── Admin: Tenants ──
export const adminTenants = writable<Tenant[]>([]);
export async function loadAdminTenants() {
  const res: any = await adminApi.getAdminTenants();
  adminTenants.set(res.items?.map((t: any) => ({
    id: t.id, slug: t.slug, name: t.name, legalName: t.legalName || '',
    sector: t.sector || '', timezone: t.timezone || '',
    currency: t.currency || '', status: t.status, createdAt: t.createdAt,
  })) || []);
}

// ── Admin: Subscription Notifications ──
export type SubscriberNotif = { id: string; tenantName: string; tenantSlug: string; buyerName: string; buyerEmail: string; plan: string; amount: number; joinedAt: string; expiresAt: string; status: 'active' | 'expiring' | 'expired'; };
export const subscriberNotifs = writable<SubscriberNotif[]>([]);
export async function loadSubscriberNotifs() {
  const res: any = await adminApi.getSubscriptionEvents();
  subscriberNotifs.set(res.items?.map((s: any) => {
    const evt = s.eventType || '';
    const status = evt.includes('expired') ? 'expired' : evt.includes('expiring') ? 'expiring' : 'active';
    return {
      id: s.id, tenantName: s.tenantName || '', tenantSlug: s.tenantSlug || '',
      buyerName: s.buyerName || '', buyerEmail: s.buyerEmail || '',
      plan: s.planCode || '', amount: parseFloat(s.amount || '0'),
      joinedAt: s.occurredAt || s.createdAt, expiresAt: s.periodEnd || '',
      status,
    };
  }) || []);
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
    if (!isActiveTenant(s)) return;
    sidebarSettings.set(res.enabledItems || {});
  } catch {
    if (!isActiveTenant(s)) return;
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
