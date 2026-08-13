export type ApiErrorBody = {
  code: string;
  message: string;
  fieldErrors?: Record<string, string[]>;
  requestId?: string;
};

export type Paginated<T> = {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
};

export type BankTransaction = {
  id: string;
  bankAccountId: string;
  externalId: string;
  transactionDate: string;
  description: string;
  amount: string;
  matched?: boolean;
};

export type MatchCandidate = {
  id: string;
  transactionNumber: string;
  transactionDate: string;
  description: string;
  amount: string;
  score: number;
};

export type Suggestion = {
  bankTransaction: BankTransaction;
  candidates: MatchCandidate[];
};

export type ImportCsvResult = {
  created: number;
  skipped: number;
  errors: string[];
};

export type ReconciliationMatch = {
  id: string;
  bankTransactionId: string;
  transactionId: string;
  confidence: string;
  status: string;
  matchedAt?: string | null;
  note?: string;
};

export type Tenant = {
  id: string;
  slug: string;
  name: string;
  legalName: string;
  sector: string;
  timezone: string;
  currency?: string;
  status: 'active' | 'trial' | 'suspended';
  createdAt: string;
};

export type User = {
  id: string;
  email: string;
  name: string;
  avatar?: string;
};

export type Membership = {
  tenant: Tenant;
  user: User;
  permissions: string[];
  role: string;
};

export type Branch = {
  id: string;
  name: string;
  code: string;
  address: string;
  isMain: boolean;
  status: 'active' | 'inactive';
};

export type Account = {
  id: string;
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'income' | 'expense';
  balance: number;
  isSystem: boolean;
  status: 'active' | 'inactive';
};

export type Transaction = {
  id: string;
  date: string;
  description: string;
  type: 'income' | 'expense' | 'transfer';
  amount: number;
  accountId: string;
  counterAccountId?: string;
  branchId: string;
  status: 'posted' | 'draft' | 'voided';
  reference?: string;
  createdAt: string;
  updatedAt: string;
};

export type JournalEntry = {
  id: string;
  date: string;
  description: string;
  reference: string;
  status: 'draft' | 'posted' | 'reversed';
  lines: JournalLine[];
  createdBy: string;
  createdAt: string;
  approvedBy?: string;
  approvedAt?: string;
};

export type JournalLine = {
  id: string;
  accountId: string;
  accountCode: string;
  accountName: string;
  description: string;
  debit: number;
  credit: number;
};

export type Invoice = {
  id: string;
  number: string;
  customerId: string;
  customerName: string;
  date: string;
  dueDate: string;
  status: 'draft' | 'sent' | 'partial' | 'paid' | 'overdue' | 'cancelled';
  subtotal: number;
  tax: number;
  total: number;
  paidAmount: number;
  lines: InvoiceLine[];
  createdAt: string;
};

export type InvoiceLine = {
  id: string;
  item: string;
  quantity: number;
  unit: string;
  price: number;
  tax: number;
  discount: number;
  total: number;
};

export type Customer = {
  id: string;
  code: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  createdAt: string;
};

export type Supplier = {
  id: string;
  code: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  createdAt: string;
};

export type Product = {
  id: string;
  sku: string;
  name: string;
  category: string;
  unit: string;
  price: number;
  cost: number;
  stock: number;
  minStock: number;
  location: string;
  status: 'active' | 'inactive';
};

export type StockMovement = {
  id: string;
  date: string;
  productId: string;
  productName: string;
  type: 'in' | 'out' | 'transfer' | 'adjustment';
  quantity: number;
  beforeStock: number;
  afterStock: number;
  reason?: string;
  reference?: string;
  createdBy: string;
  createdAt: string;
};

export type Notification = {
  id: string;
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
  type: 'info' | 'warning' | 'success' | 'error';
  link?: string;
  metadata?: Record<string, unknown>;
};

export type AuditEvent = {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  module: string;
  objectId: string;
  objectType: string;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  requestId?: string;
  correlationId?: string;
  integrityHash?: string;
};
