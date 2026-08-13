<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import Toast from '$lib/components/ui/Toast.svelte';
  import Tour from '$lib/components/tour/Tour.svelte';

  let { children } = $props();

  const pageTitles: Record<string, string> = {
    '/(marketing)': 'Beranda',
    '/(marketing)/privacy': 'Kebijakan Privasi',
    '/(marketing)/security': 'Keamanan',
    '/(marketing)/terms': 'Syarat & Ketentuan',
    '/(auth)/auth/login': 'Masuk',
    '/(auth)/auth/register': 'Daftar Gratis',
    '/(auth)/auth/forgot-password': 'Lupa Password',
    '/(auth)/auth/reset-password': 'Reset Password',
    '/(auth)/auth/mfa': 'Verifikasi Dua Langkah',
    '/(auth)/auth/onboarding': 'Onboarding',
    '/(auth)/auth/create-company': 'Buat Perusahaan Baru',
    '/(auth)/auth/join-company': 'Gabung Perusahaan',
    '/(platform)/admin': 'Dashboard Admin',
    '/(platform)/admin/audit': 'Audit Platform',
    '/(platform)/admin/incidents': 'Insiden Keamanan',
    '/(platform)/admin/notifications': 'Notifikasi',
    '/(platform)/admin/security': 'Keamanan Platform',
    '/(platform)/admin/subscriptions': 'Langganan',
    '/(platform)/admin/tenants': 'Manajemen Tenant',
    '/(platform)/admin/users': 'Manajemen Pengguna',
    '/(workspace)/app/[tenantSlug]': 'Dashboard',
    '/(workspace)/app/[tenantSlug]/pos': 'Point of Sales',
    '/(workspace)/app/[tenantSlug]/transactions': 'Transaksi',
    '/(workspace)/app/[tenantSlug]/audit': 'Audit Trail',
    '/(workspace)/app/[tenantSlug]/insights': 'Analitik Bisnis',
    '/(workspace)/app/[tenantSlug]/notifications': 'Notifikasi',
    '/(workspace)/app/[tenantSlug]/notifications/[id]': 'Detail Notifikasi',
    '/(workspace)/app/[tenantSlug]/tutorial': 'Tutorial',
    '/(workspace)/app/[tenantSlug]/accounting/chart-of-accounts': 'Chart of Accounts',
    '/(workspace)/app/[tenantSlug]/accounting/fiscal-years': 'Tahun Buku',
    '/(workspace)/app/[tenantSlug]/accounting/journals': 'Jurnal',
    '/(workspace)/app/[tenantSlug]/accounting/reconciliation': 'Rekonsiliasi Bank',
    '/(workspace)/app/[tenantSlug]/inventory/movements': 'Pergerakan Stok',
    '/(workspace)/app/[tenantSlug]/inventory/products': 'Produk',
    '/(workspace)/app/[tenantSlug]/inventory/transactions': 'Transaksi Produk',
    '/(workspace)/app/[tenantSlug]/purchasing/orders': 'Pesanan Pembelian',
    '/(workspace)/app/[tenantSlug]/purchasing/payments': 'Pembayaran Pemasok',
    '/(workspace)/app/[tenantSlug]/purchasing/suppliers': 'Pemasok',
    '/(workspace)/app/[tenantSlug]/reports': 'Laporan Keuangan',
    '/(workspace)/app/[tenantSlug]/reports/investor': 'Investor Report',
    '/(workspace)/app/[tenantSlug]/sales/customers': 'Pelanggan',
    '/(workspace)/app/[tenantSlug]/sales/invoices': 'Invoice',
    '/(workspace)/app/[tenantSlug]/settings/billing': 'Billing',
    '/(workspace)/app/[tenantSlug]/settings/branches': 'Cabang',
    '/(workspace)/app/[tenantSlug]/settings/integrations': 'Integrasi',
    '/(workspace)/app/[tenantSlug]/settings/members': 'Anggota Tim',
    '/(workspace)/app/[tenantSlug]/settings/organization': 'Organisasi',
    '/(workspace)/app/[tenantSlug]/settings/roles': 'Peran & Izin',
    '/(workspace)/app/[tenantSlug]/settings/security': 'Keamanan',
    '/(workspace)/app/[tenantSlug]/settings/sidebar': 'Kustomisasi Sidebar'
  };

  const documentTitle = $derived.by(() => {
    const id = $page.route.id;
    if (id && id in pageTitles) return `KePin - ${pageTitles[id]}`;
    return 'KePin - Keuangan Pintar untuk UMKM';
  });
</script>

<svelte:head>
  <title>{documentTitle}</title>
  <link rel="icon" href="/media/logo/kepin-light.png" />
  <link rel="apple-touch-icon" href="/media/logo/kepin-light.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet" />
</svelte:head>

{@render children()}

<Toast />

<!-- Tur interaktif tersedia di seluruh halaman: landing, auth, dan workspace -->
<Tour />