import { writable, get } from 'svelte/store';
import type {
  Transaction, Account, JournalEntry, Invoice, Customer,
  Supplier, Product, StockMovement, Branch, Membership,
  AuditEvent, Notification, Tenant, User,
} from '$lib/api/types';

type JSON = Record<string, unknown>;

// ── Transactions ──
export const transactions = writable<Transaction[]>([
  { id: 'TXN-001', date: '2026-07-25', description: 'Penjualan Tunai', type: 'income', amount: 2500000, accountId: 'ACC-001', branchId: 'BR-001', status: 'posted', createdAt: '2026-07-25T10:00:00Z', updatedAt: '2026-07-25T10:00:00Z' },
  { id: 'TXN-002', date: '2026-07-24', description: 'Pembelian Stok', type: 'expense', amount: 1800000, accountId: 'ACC-002', branchId: 'BR-001', status: 'posted', createdAt: '2026-07-24T14:00:00Z', updatedAt: '2026-07-24T14:00:00Z' },
  { id: 'TXN-003', date: '2026-07-24', description: 'Pembayaran Listrik', type: 'expense', amount: 450000, accountId: 'ACC-003', branchId: 'BR-001', status: 'posted', createdAt: '2026-07-24T09:00:00Z', updatedAt: '2026-07-24T09:00:00Z' },
  { id: 'TXN-004', date: '2026-07-23', description: 'Penjualan Online', type: 'income', amount: 3200000, accountId: 'ACC-001', branchId: 'BR-002', status: 'posted', createdAt: '2026-07-23T16:00:00Z', updatedAt: '2026-07-23T16:00:00Z' },
  { id: 'TXN-005', date: '2026-07-26', description: 'Biaya Marketing', type: 'expense', amount: 750000, accountId: 'ACC-004', branchId: 'BR-001', status: 'draft', createdAt: '2026-07-26T08:00:00Z', updatedAt: '2026-07-26T08:00:00Z' },
]);
export function createTransaction(data: JSON) {
  const id = `TXN-${String(Date.now()).slice(-6)}`;
  const now = new Date().toISOString();
  transactions.update(list => [...list, { id, date: now.slice(0,10), description: '', type: 'income', amount: 0, accountId: '', branchId: 'BR-001', status: 'draft', createdAt: now, updatedAt: now, ...data }]);
}
export function updateTransaction(id: string, data: JSON) {
  transactions.update(list => list.map(t => t.id === id ? { ...t, ...data, updatedAt: new Date().toISOString() } : t));
}
export function deleteTransaction(id: string) {
  transactions.update(list => list.filter(t => t.id !== id));
}

// ── Accounts ──
export const accounts = writable<Account[]>([
  { id: 'ACC-001', code: '101', name: 'Kas', type: 'asset', balance: 45300000, isSystem: false, status: 'active' },
  { id: 'ACC-002', code: '102', name: 'Bank BCA', type: 'asset', balance: 125000000, isSystem: false, status: 'active' },
  { id: 'ACC-003', code: '201', name: 'Hutang Usaha', type: 'liability', balance: 8500000, isSystem: false, status: 'active' },
  { id: 'ACC-004', code: '301', name: 'Modal', type: 'equity', balance: 150000000, isSystem: true, status: 'active' },
  { id: 'ACC-005', code: '401', name: 'Pendapatan', type: 'income', balance: 45200000, isSystem: false, status: 'active' },
  { id: 'ACC-006', code: '501', name: 'Beban Operasional', type: 'expense', balance: 28100000, isSystem: false, status: 'active' },
  { id: 'ACC-007', code: '103', name: 'Piutang', type: 'asset', balance: 12000000, isSystem: false, status: 'active' },
  { id: 'ACC-008', code: '104', name: 'Persediaan', type: 'asset', balance: 45000000, isSystem: false, status: 'active' },
]);

// ── Journal Entries ──
export const journalEntries = writable<JournalEntry[]>([
  { id: 'JNL-001', date: '2026-07-25', description: 'Penjualan Tunai', reference: 'INV-001', status: 'posted', lines: [{ id: '1', accountId: 'ACC-001', accountCode: '101', accountName: 'Kas', description: 'Debit Kas', debit: 2500000, credit: 0 }, { id: '2', accountId: 'ACC-005', accountCode: '401', accountName: 'Pendapatan', description: 'Kredit Pendapatan', debit: 0, credit: 2500000 }], createdBy: 'Budi Santoso', createdAt: '2026-07-25T10:00:00Z' },
  { id: 'JNL-002', date: '2026-07-24', description: 'Pembelian Stok', reference: 'PO-001', status: 'posted', lines: [{ id: '3', accountId: 'ACC-008', accountCode: '104', accountName: 'Persediaan', description: 'Debit Persediaan', debit: 1800000, credit: 0 }, { id: '4', accountId: 'ACC-001', accountCode: '101', accountName: 'Kas', description: 'Kredit Kas', debit: 0, credit: 1800000 }], createdBy: 'Budi Santoso', createdAt: '2026-07-24T14:00:00Z' },
  { id: 'JNL-003', date: '2026-07-26', description: 'Adjustment Stok', reference: 'ADJ-001', status: 'draft', lines: [{ id: '5', accountId: 'ACC-008', accountCode: '104', accountName: 'Persediaan', description: 'Adjustment', debit: 500000, credit: 0 }], createdBy: 'Ani Lestari', createdAt: '2026-07-26T09:00:00Z' },
]);

// ── Invoices ──
export const invoices = writable<Invoice[]>([
  { id: 'INV-001', number: 'INV/2026/001', customerId: 'CUST-001', customerName: 'PT Maju Jaya', date: '2026-07-20', dueDate: '2026-08-20', status: 'paid', subtotal: 5000000, tax: 500000, total: 5500000, paidAmount: 5500000, lines: [], createdAt: '2026-07-20T10:00:00Z' },
  { id: 'INV-002', number: 'INV/2026/002', customerId: 'CUST-002', customerName: 'CV Sejahtera', date: '2026-07-22', dueDate: '2026-08-22', status: 'sent', subtotal: 3250000, tax: 325000, total: 3575000, paidAmount: 0, lines: [], createdAt: '2026-07-22T14:00:00Z' },
  { id: 'INV-003', number: 'INV/2026/003', customerId: 'CUST-003', customerName: 'UD Makmur', date: '2026-07-10', dueDate: '2026-07-25', status: 'overdue', subtotal: 7800000, tax: 780000, total: 8580000, paidAmount: 3000000, lines: [], createdAt: '2026-07-10T09:00:00Z' },
  { id: 'INV-004', number: 'INV/2026/004', customerId: 'CUST-001', customerName: 'PT Maju Jaya', date: '2026-07-25', dueDate: '2026-08-25', status: 'draft', subtotal: 2100000, tax: 210000, total: 2310000, paidAmount: 0, lines: [], createdAt: '2026-07-25T11:00:00Z' },
]);
export function createInvoice(data: JSON) {
  const id = `INV-${String(Date.now()).slice(-6)}`;
  const year = new Date().getFullYear();
  const num = get(invoices).length + 1;
  invoices.update(list => [...list, { id, number: `INV/${year}/${String(num).padStart(3,'0')}`, customerId: '', customerName: '', date: '', dueDate: '', status: 'draft' as const, subtotal: 0, tax: 0, total: 0, paidAmount: 0, lines: [], createdAt: new Date().toISOString(), ...data }]);
}
export function updateInvoice(id: string, data: JSON) {
  invoices.update(list => list.map(inv => inv.id === id ? { ...inv, ...data } : inv));
}
export function deleteInvoice(id: string) {
  invoices.update(list => list.filter(inv => inv.id !== id));
}

// ── Customers ──
export const customers = writable<Customer[]>([
  { id: 'CUST-001', name: 'PT Maju Jaya', email: 'info@majujaya.co.id', phone: '021-5551212', address: 'Jl. Merdeka No. 123, Jakarta', createdAt: '2026-01-15T10:00:00Z' },
  { id: 'CUST-002', name: 'CV Sejahtera', email: 'admin@sejahtera.com', phone: '022-5553434', address: 'Jl. Braga No. 45, Bandung', createdAt: '2026-02-20T10:00:00Z' },
  { id: 'CUST-003', name: 'UD Makmur', email: 'makmur@ud.com', phone: '031-5555656', address: 'Jl. Tunjungan No. 78, Surabaya', createdAt: '2026-03-10T10:00:00Z' },
  { id: 'CUST-004', name: 'PT Nusantara Abadi', email: 'contact@nusantara.co.id', phone: '061-5557878', address: 'Jl. Sudirman No. 90, Medan', createdAt: '2026-04-05T10:00:00Z' },
]);
export function createCustomer(data: JSON) {
  const id = `CUST-${String(Date.now()).slice(-6)}`;
  customers.update(list => [...list, { id, name: '', email: '', phone: '', address: '', createdAt: new Date().toISOString(), ...data }]);
}
export function updateCustomer(id: string, data: JSON) {
  customers.update(list => list.map(c => c.id === id ? { ...c, ...data } : c));
}
export function deleteCustomer(id: string) {
  customers.update(list => list.filter(c => c.id !== id));
}

// ── Suppliers ──
export const suppliers = writable<Supplier[]>([
  { id: 'SUPP-001', name: 'PT Sumber Makmur', email: 'sales@sumbermakmur.co.id', phone: '021-5559999', address: 'Jl. Industri No. 56, Jakarta', createdAt: '2026-01-10T10:00:00Z' },
  { id: 'SUPP-002', name: 'CV Bahan Baku', email: 'order@bahanbaku.com', phone: '022-5551111', address: 'Jl. Kopo No. 12, Bandung', createdAt: '2026-01-15T10:00:00Z' },
  { id: 'SUPP-003', name: 'UD Logistik', email: 'info@udlogistik.com', phone: '031-5553333', address: 'Jl. Raya Industri No. 34, Surabaya', createdAt: '2026-02-01T10:00:00Z' },
]);
export function createSupplier(data: JSON) {
  const id = `SUPP-${String(Date.now()).slice(-6)}`;
  suppliers.update(list => [...list, { id, name: '', email: '', phone: '', address: '', createdAt: new Date().toISOString(), ...data }]);
}
export function updateSupplier(id: string, data: JSON) {
  suppliers.update(list => list.map(s => s.id === id ? { ...s, ...data } : s));
}
export function deleteSupplier(id: string) {
  suppliers.update(list => list.filter(s => s.id !== id));
}

// ── Products ──
export const products = writable<Product[]>([
  { id: 'PROD-001', sku: 'SKU-001', name: 'Produk A', category: 'Elektronik', unit: 'pcs', price: 500000, cost: 350000, stock: 3, minStock: 10, location: 'Rak A1', status: 'active' },
  { id: 'PROD-002', sku: 'SKU-002', name: 'Produk B', category: 'Fashion', unit: 'pcs', price: 650000, cost: 400000, stock: 25, minStock: 5, location: 'Rak B2', status: 'active' },
  { id: 'PROD-003', sku: 'SKU-003', name: 'Produk C', category: 'Makanan', unit: 'box', price: 390000, cost: 250000, stock: 15, minStock: 10, location: 'Rak C3', status: 'active' },
  { id: 'PROD-004', sku: 'SKU-004', name: 'Produk D', category: 'Elektronik', unit: 'pcs', price: 1500000, cost: 1100000, stock: 8, minStock: 3, location: 'Rak A2', status: 'active' },
  { id: 'PROD-005', sku: 'SKU-005', name: 'Produk E', category: 'Fashion', unit: 'pcs', price: 250000, cost: 150000, stock: 50, minStock: 20, location: 'Rak B1', status: 'inactive' },
]);
export function createProduct(data: JSON) {
  const id = `PROD-${String(Date.now()).slice(-6)}`;
  products.update(list => [...list, { id, sku: '', name: '', category: '', unit: 'pcs', price: 0, cost: 0, stock: 0, minStock: 0, location: '', status: 'active', ...data }]);
}
export function updateProduct(id: string, data: JSON) {
  products.update(list => list.map(p => p.id === id ? { ...p, ...data } : p));
}
export function deleteProduct(id: string) {
  products.update(list => list.filter(p => p.id !== id));
}

// ── Stock Movements ──
export const stockMovements = writable<StockMovement[]>([
  { id: 'MOV-001', date: '2026-07-25', productId: 'PROD-001', productName: 'Produk A', type: 'out', quantity: 5, beforeStock: 8, afterStock: 3, reason: 'Penjualan', createdAt: '2026-07-25T10:00:00Z', createdBy: 'Budi Santoso' },
  { id: 'MOV-002', date: '2026-07-24', productId: 'PROD-002', productName: 'Produk B', type: 'in', quantity: 20, beforeStock: 5, afterStock: 25, reason: 'Restock', createdAt: '2026-07-24T14:00:00Z', createdBy: 'Ani Lestari' },
  { id: 'MOV-003', date: '2026-07-23', productId: 'PROD-004', productName: 'Produk D', type: 'adjustment', quantity: 2, beforeStock: 6, afterStock: 8, reason: 'Opname', createdAt: '2026-07-23T09:00:00Z', createdBy: 'Budi Santoso' },
]);

// ── Branches ──
export const branches = writable<Branch[]>([
  { id: 'BR-001', name: 'Toko Pusat', code: 'PST', isMain: true },
  { id: 'BR-002', name: 'Cabang Bandung', code: 'BDG', isMain: false },
  { id: 'BR-003', name: 'Cabang Surabaya', code: 'SBY', isMain: false },
]);
export function createBranch(data: JSON) {
  const id = `BR-${String(Date.now()).slice(-6)}`;
  branches.update(list => [...list, { id, name: '', code: '', isMain: false, ...data }]);
}
export function updateBranch(id: string, data: JSON) {
  branches.update(list => list.map(b => b.id === id ? { ...b, ...data } : b));
}
export function deleteBranch(id: string) {
  branches.update(list => list.filter(b => b.id !== id));
}

// ── Members ──
export const members = writable<(Membership & { status: string })[]>([
  { tenant: { id: 'TEN-001', slug: 'toko-maju', name: 'Toko Maju Jaya', legalName: 'PT Toko Maju Jaya', sector: 'Ritel', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active', createdAt: '2026-01-01' }, user: { id: 'USR-001', email: 'budi@tokomaju.com', name: 'Budi Santoso' }, permissions: ['all'], role: 'Owner', status: 'active' },
  { tenant: { id: 'TEN-001', slug: 'toko-maju', name: 'Toko Maju Jaya', legalName: 'PT Toko Maju Jaya', sector: 'Ritel', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active', createdAt: '2026-01-01' }, user: { id: 'USR-002', email: 'ani@tokomaju.com', name: 'Ani Lestari' }, permissions: ['accounting.read', 'reports.export'], role: 'Akuntan', status: 'active' },
  { tenant: { id: 'TEN-001', slug: 'toko-maju', name: 'Toko Maju Jaya', legalName: 'PT Toko Maju Jaya', sector: 'Ritel', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active', createdAt: '2026-01-01' }, user: { id: 'USR-003', email: 'dedi@tokomaju.com', name: 'Dedi Kurniawan' }, permissions: ['inventory.adjust'], role: 'Staff Gudang', status: 'active' },
]);
export function createMember(data: Partial<Membership & { status: string }>) {
  const user = { id: `USR-${Date.now()}`, email: `user${Date.now()}@email.com`, name: '' };
  members.update(list => [...list, { tenant: { id: 'TEN-001', slug: 'toko-maju', name: 'Toko Maju Jaya', legalName: '', sector: '', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active', createdAt: '2026-01-01' }, user, permissions: [], role: '', status: 'active', ...data }]);
}
export function updateMember(idx: number, data: Partial<Membership & { status: string }>) {
  members.update(list => list.map((m, i) => i === idx ? { ...m, ...data } : m));
}
export function deleteMember(idx: number) {
  members.update(list => list.filter((_, i) => i !== idx));
}

// ── Notifications ──
export const notifications = writable<Notification[]>([
  { id: 'NOTIF-001', message: 'Invoice INV-005 telah dibayar oleh Pelanggan', createdAt: new Date(Date.now() - 30000).toISOString(), read: false, type: 'success' },
  { id: 'NOTIF-002', message: 'Stok produk SKU-001 hampir habis (sisa 3 unit)', createdAt: new Date(Date.now() - 120000).toISOString(), read: false, type: 'warning' },
  { id: 'NOTIF-003', message: 'Jurnal JNL-001 telah diposting oleh Budi Santoso', createdAt: new Date(Date.now() - 3600000).toISOString(), read: false, type: 'info' },
  { id: 'NOTIF-004', message: 'Pembayaran langganan akan jatuh tempo dalam 7 hari', createdAt: new Date(Date.now() - 86400000).toISOString(), read: true, type: 'info' },
  { id: 'NOTIF-005', message: 'Cabang Baru berhasil ditambahkan', createdAt: new Date(Date.now() - 172800000).toISOString(), read: true, type: 'success' },
  { id: 'NOTIF-006', message: 'Ada 5 invoice yang sudah melewati jatuh tempo', createdAt: new Date(Date.now() - 259200000).toISOString(), read: true, type: 'error' },
  { id: 'NOTIF-007', message: 'Laporan bulanan siap diunduh', createdAt: new Date(Date.now() - 432000000).toISOString(), read: true, type: 'info' },
  { id: 'NOTIF-008', message: 'Pemasok PT Sumber Makmur mengirimkan penawaran baru', createdAt: new Date(Date.now() - 604800000).toISOString(), read: true, type: 'info' },
]);
export function markNotifRead(id: string) {
  notifications.update(list => list.map(n => n.id === id ? { ...n, read: true } : n));
}
export function markAllNotifRead() {
  notifications.update(list => list.map(n => ({ ...n, read: true })));
}
export function deleteNotification(id: string) {
  notifications.update(list => list.filter(n => n.id !== id));
}

// ── Audit Events ──
export const auditEvents = writable<AuditEvent[]>([
  { id: 'AUD-001', timestamp: '2026-07-25T14:30:00Z', actor: 'Budi Santoso', action: 'Post Jurnal', module: 'Accounting', objectId: 'JNL-001', objectType: 'JournalEntry', integrityVerified: true },
  { id: 'AUD-002', timestamp: '2026-07-25T11:20:00Z', actor: 'Ani Lestari', action: 'Buat Invoice', module: 'Sales', objectId: 'INV-005', objectType: 'Invoice', integrityVerified: true },
  { id: 'AUD-003', timestamp: '2026-07-24T16:45:00Z', actor: 'Budi Santoso', action: 'Adjust Stok', module: 'Inventory', objectId: 'ADJ-001', objectType: 'Adjustment', integrityVerified: true },
  { id: 'AUD-004', timestamp: '2026-07-24T09:15:00Z', actor: 'System', action: 'Backup Otomatis', module: 'System', objectId: 'Daily', objectType: 'Backup', integrityVerified: true },
  { id: 'AUD-005', timestamp: '2026-07-23T15:00:00Z', actor: 'Dedi Kurniawan', action: 'Login', module: 'Auth', objectId: 'Session', objectType: 'Session', integrityVerified: true },
]);

// ── Admin: Tenants ──
export const adminTenants = writable<Tenant[]>([
  { id: 'TEN-001', slug: 'toko-maju', name: 'Toko Maju Jaya', legalName: 'PT Toko Maju Jaya', sector: 'Ritel', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active', createdAt: '2026-01-01T00:00:00Z' },
  { id: 'TEN-002', slug: 'bengkel-maju', name: 'Bengkel Maju', legalName: 'CV Bengkel Maju', sector: 'Otomotif', timezone: 'Asia/Jakarta', plan: 'Basic', status: 'active', createdAt: '2026-02-15T00:00:00Z' },
  { id: 'TEN-003', slug: 'warung-segar', name: 'Warung Segar', legalName: 'UD Warung Segar', sector: 'F&B', timezone: 'Asia/Jakarta', plan: 'Trial', status: 'trial', createdAt: '2026-06-01T00:00:00Z' },
  { id: 'TEN-004', slug: 'fashion-baru', name: 'Fashion Baru', legalName: 'PT Fashion Baru Indonesia', sector: 'Fashion', timezone: 'Asia/Jakarta', plan: 'Enterprise', status: 'suspended', createdAt: '2025-11-01T00:00:00Z' },
]);

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

export const subscriberNotifs = writable<SubscriberNotif[]>([
  { id: 'SUB-001', tenantName: 'Toko Maju Jaya', tenantSlug: 'toko-maju', buyerName: 'Budi Santoso', buyerEmail: 'budi@tokomaju.com', plan: 'Pro', amount: 299000, joinedAt: '2026-01-15T10:00:00Z', expiresAt: '2027-01-15T10:00:00Z', status: 'active' },
  { id: 'SUB-002', tenantName: 'Bengkel Maju', tenantSlug: 'bengkel-maju', buyerName: 'Ahmad Rizki', buyerEmail: 'ahmad@bengkelmaju.com', plan: 'Basic', amount: 99000, joinedAt: '2026-02-20T14:30:00Z', expiresAt: '2027-02-20T14:30:00Z', status: 'active' },
  { id: 'SUB-003', tenantName: 'Warung Segar', tenantSlug: 'warung-segar', buyerName: 'Siti Nurhaliza', buyerEmail: 'siti@warungsegar.com', plan: 'Trial', amount: 0, joinedAt: '2026-06-01T08:00:00Z', expiresAt: '2026-06-15T08:00:00Z', status: 'expiring' },
  { id: 'SUB-004', tenantName: 'Fashion Baru', tenantSlug: 'fashion-baru', buyerName: 'Diana Putri', buyerEmail: 'diana@fashionbaru.co.id', plan: 'Enterprise', amount: 999000, joinedAt: '2025-11-10T09:00:00Z', expiresAt: '2026-11-10T09:00:00Z', status: 'active' },
  { id: 'SUB-005', tenantName: 'Tech Solutions', tenantSlug: 'tech-solusi', buyerName: 'Rudi Hartono', buyerEmail: 'rudi@techsolusi.com', plan: 'Pro', amount: 299000, joinedAt: '2025-08-05T11:00:00Z', expiresAt: '2026-08-05T11:00:00Z', status: 'expired' },
  { id: 'SUB-006', tenantName: 'CV Karya Mandiri', tenantSlug: 'karya-mandiri', buyerName: 'Indra Lesmana', buyerEmail: 'indra@karyamandiri.com', plan: 'Basic', amount: 99000, joinedAt: '2026-03-12T07:30:00Z', expiresAt: '2027-03-12T07:30:00Z', status: 'active' },
]);

// ── Admin: Users ──
export const adminUsers = writable<User[]>([
  { id: 'USR-001', email: 'budi@tokomaju.com', name: 'Budi Santoso' },
  { id: 'USR-002', email: 'ani@tokomaju.com', name: 'Ani Lestari' },
  { id: 'USR-003', email: 'dedi@tokomaju.com', name: 'Dedi Kurniawan' },
  { id: 'USR-004', email: 'admin@kepin.io', name: 'Admin KePin' },
  { id: 'USR-005', email: 'super@kepin.io', name: 'Super Admin' },
]);
