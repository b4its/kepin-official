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
  label: string;
  href: string;
  icon: typeof Icon;
  permission?: Permission;
  badge?: string;
};

export type NavigationGroup = {
  label: string;
  items: NavigationItem[];
};

export const clientNavigation: NavigationGroup[] = [
  {
    label: 'Ringkasan',
    items: [
      { label: 'Dashboard', href: '', icon: Home },
    ],
  },
  {
    label: 'Penjualan',
    items: [
      { label: 'Invoice', href: '/sales/invoices', icon: Receipt },
      { label: 'Pelanggan', href: '/sales/customers', icon: Users },
    ],
  },
  {
    label: 'Pembelian',
    items: [
      { label: 'Pesanan', href: '/purchasing/orders', icon: ShoppingCart },
      { label: 'Pemasok', href: '/purchasing/suppliers', icon: Building2 },
    ],
  },
  {
    label: 'Inventaris',
    items: [
      { label: 'Produk', href: '/inventory/products', icon: Package },
      { label: 'Pergerakan Stok', href: '/inventory/movements', icon: Warehouse },
    ],
  },
  {
    label: 'Akuntansi',
    items: [
      { label: 'Transaksi', href: '/transactions', icon: DollarSign },
      { label: 'Jurnal', href: '/accounting/journals', icon: BookOpen },
      { label: 'Chart of Accounts', href: '/accounting/chart-of-accounts', icon: FileText },
      { label: 'Rekonsiliasi', href: '/accounting/reconciliation', icon: CreditCard },
    ],
  },
  {
    label: 'Laporan & Insight',
    items: [
      { label: 'Laporan', href: '/reports', icon: BarChart3 },
      { label: 'Investor Report', href: '/reports/investor', icon: TrendingUp },
      { label: 'AI Insight', href: '/insights', icon: Activity },
    ],
  },
  {
    label: 'Kontrol',
    items: [
      { label: 'Audit Trail', href: '/audit', icon: Shield },
      { label: 'Pengaturan', href: '/settings/organization', icon: Settings },
    ],
  },
];

export const adminNavigation: NavigationGroup[] = [
  {
    label: 'Platform',
    items: [
      { label: 'Dashboard', href: '/admin', icon: Home },
      { label: 'Tenant', href: '/admin/tenants', icon: Building2 },
      { label: 'Pengguna', href: '/admin/users', icon: Users },
      { label: 'Langganan', href: '/admin/subscriptions', icon: CreditCard },
    ],
  },
  {
    label: 'Keamanan',
    items: [
      { label: 'Keamanan', href: '/admin/security', icon: Shield },
      { label: 'Insiden', href: '/admin/incidents', icon: AlertTriangle },
      { label: 'Audit Platform', href: '/admin/audit', icon: Activity },
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
