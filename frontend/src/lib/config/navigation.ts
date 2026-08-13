import {
  Home,
  ShoppingCart,
  Package,
  Warehouse,
  BookOpen,
  BarChart3,
  Shield,
  Settings,
  Users,
  FileText,
  TrendingUp,
  DollarSign,
  Receipt,
  CreditCard,
  Building2,
  UserCog,
  AlertTriangle,
  Activity,
  Bell,
  LayoutDashboard,
  KeyRound,
  CalendarDays,
  HelpCircle,
  type Icon,
} from '@lucide/svelte';

export type Permission =
  | 'accounting.read'
  | 'accounting.write'
  | 'journal.post'
  | 'inventory.adjust'
  | 'reports.export'
  | 'members.manage'
  | 'billing.manage';

export type NavigationItem = {
  /** Unique stable key used for sidebar customisation. */
  key: string;
  label: string;
  href: string;
  icon: typeof Icon;
  permission?: Permission;
  badge?: string;
  /** If true, this item is always shown (cannot be hidden by owner). */
  pinned?: boolean;
};

export type NavigationGroup = {
  label: string;
  /** Unique key for the group itself, used for collapse state persistence. */
  key: string;
  items: NavigationItem[];
};

export const clientNavigation: NavigationGroup[] = [
  {
    label: 'Ringkasan',
    key: 'group_ringkasan',
    items: [
      { key: 'dashboard', label: 'Dashboard', href: '', icon: Home, pinned: true },
    ],
  },
  {
    label: 'Penjualan',
    key: 'group_penjualan',
    items: [
      { key: 'sales_pos', label: 'Point of Sales', href: '/pos', icon: ShoppingCart },
      { key: 'sales_invoices', label: 'Invoice', href: '/sales/invoices', icon: Receipt },
      { key: 'sales_customers', label: 'Pelanggan', href: '/sales/customers', icon: Users },
    ],
  },
  {
    label: 'Pembelian',
    key: 'group_pembelian',
    items: [
      { key: 'purchasing_orders', label: 'Pesanan', href: '/purchasing/orders', icon: ShoppingCart },
      { key: 'purchasing_payments', label: 'Pembayaran', href: '/purchasing/payments', icon: CreditCard },
      { key: 'purchasing_suppliers', label: 'Pemasok', href: '/purchasing/suppliers', icon: Building2 },
    ],
  },
  {
    label: 'Inventaris',
    key: 'group_inventaris',
    items: [
      { key: 'inventory_products', label: 'Produk', href: '/inventory/products', icon: Package },
      { key: 'inventory_movements', label: 'Pergerakan Stok', href: '/inventory/movements', icon: Warehouse },
      { key: 'inventory_transactions', label: 'Transaksi Produk', href: '/inventory/transactions', icon: Receipt },
    ],
  },
  {
    label: 'Akuntansi',
    key: 'group_akuntansi',
    items: [
      { key: 'accounting_transactions', label: 'Transaksi', href: '/transactions', icon: DollarSign },
      { key: 'accounting_journals', label: 'Jurnal', href: '/accounting/journals', icon: BookOpen },
      { key: 'accounting_coa', label: 'Chart of Accounts', href: '/accounting/chart-of-accounts', icon: FileText },
      { key: 'accounting_fiscal', label: 'Tahun Buku', href: '/accounting/fiscal-years', icon: CalendarDays },
      { key: 'accounting_recon', label: 'Rekonsiliasi', href: '/accounting/reconciliation', icon: CreditCard },
    ],
  },
  {
    label: 'Laporan & Insight',
    key: 'group_laporan',
    items: [
      { key: 'reports_summary', label: 'Laporan', href: '/reports', icon: BarChart3 },
      { key: 'reports_investor', label: 'Investor Report', href: '/reports/investor', icon: TrendingUp },
      { key: 'reports_insights', label: 'AI Insight', href: '/insights', icon: Activity },
    ],
  },
  {
    label: 'Kontrol',
    key: 'group_kontrol',
    items: [
      { key: 'audit_trail', label: 'Audit Trail', href: '/audit', icon: Shield },
      { key: 'notifications', label: 'Notifikasi', href: '/notifications', icon: Bell },
      { key: 'settings_org', label: 'Pengaturan', href: '/settings/organization', icon: Settings, pinned: true },
      { key: 'settings_security', label: 'Keamanan Akun', href: '/settings/security', icon: KeyRound, pinned: true },
    ],
  },
  {
    label: 'Bantuan',
    key: 'group_bantuan',
    items: [
      { key: 'tutorial', label: 'Tutorial', href: '/tutorial', icon: HelpCircle, pinned: true },
    ],
  },
];

export const adminNavigation: NavigationGroup[] = [
  {
    label: 'Platform',
    key: 'group_platform',
    items: [
      { key: 'admin_dashboard', label: 'Dashboard', href: '/admin', icon: Home },
      { key: 'admin_tenants', label: 'Tenant', href: '/admin/tenants', icon: Building2 },
      { key: 'admin_users', label: 'Pengguna', href: '/admin/users', icon: Users },
      { key: 'admin_subscriptions', label: 'Langganan', href: '/admin/subscriptions', icon: CreditCard },
      { key: 'admin_notifications', label: 'Notifikasi', href: '/admin/notifications', icon: Bell },
    ],
  },
  {
    label: 'Keamanan',
    key: 'group_keamanan',
    items: [
      { key: 'admin_security', label: 'Keamanan', href: '/admin/security', icon: Shield },
      { key: 'admin_incidents', label: 'Insiden', href: '/admin/incidents', icon: AlertTriangle },
      { key: 'admin_audit', label: 'Audit Platform', href: '/admin/audit', icon: Activity },
    ],
  },
];

export const landingAnchors = [
  { label: 'Solusi', href: '#solusi' },
  { label: 'Fitur', href: '#fitur' },
  { label: 'Keamanan', href: '#keamanan' },
  { label: 'Cara Kerja', href: '#cara-kerja' },
  { label: 'Harga', href: '#harga' },
  { label: 'FAQ', href: '#faq' },
];
