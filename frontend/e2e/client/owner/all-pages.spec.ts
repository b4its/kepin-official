import { test, expect } from '@playwright/test';

const TENANT = 'toko-maju';
const PAGES = [
  { route: `/app/${TENANT}`, label: 'Dashboard' },
  { route: `/app/${TENANT}/sales/invoices`, label: 'Invoice' },
  { route: `/app/${TENANT}/sales/customers`, label: 'Pelanggan' },
  { route: `/app/${TENANT}/purchasing/orders`, label: 'Pesanan' },
  { route: `/app/${TENANT}/purchasing/payments`, label: 'Pembayaran' },
  { route: `/app/${TENANT}/purchasing/suppliers`, label: 'Pemasok' },
  { route: `/app/${TENANT}/inventory/products`, label: 'Produk' },
  { route: `/app/${TENANT}/inventory/movements`, label: 'Pergerakan Stok' },
  { route: `/app/${TENANT}/transactions`, label: 'Transaksi' },
  { route: `/app/${TENANT}/accounting/chart-of-accounts`, label: 'Chart of Accounts' },
  { route: `/app/${TENANT}/accounting/journals`, label: 'Jurnal' },
  { route: `/app/${TENANT}/accounting/reconciliation`, label: 'Rekonsiliasi' },
  { route: `/app/${TENANT}/reports`, label: 'Laporan' },
  { route: `/app/${TENANT}/reports/investor`, label: 'Investor Report' },
  { route: `/app/${TENANT}/insights`, label: 'AI Insight' },
  { route: `/app/${TENANT}/notifications`, label: 'Notifikasi' },
  { route: `/app/${TENANT}/audit`, label: 'Audit Trail' },
  { route: `/app/${TENANT}/settings/organization`, label: 'Pengaturan' },
  { route: `/app/${TENANT}/settings/security`, label: 'Keamanan' },
  { route: `/app/${TENANT}/settings/branches`, label: 'Cabang' },
  { route: `/app/${TENANT}/settings/members`, label: 'Anggota' },
  { route: `/app/${TENANT}/settings/roles`, label: 'Role' },
  { route: `/app/${TENANT}/settings/sidebar`, label: 'Sidebar' },
  { route: `/app/${TENANT}/settings/billing`, label: 'Tagihan' },
  { route: `/app/${TENANT}/settings/integrations`, label: 'Integrasi' },
];

test.describe('Workspace Page Render', () => {
  for (const { route, label } of PAGES) {
    test(`${route} renders without error`, async ({ page }) => {
      const errors: string[] = [];
      page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

      await page.goto(route);
      await page.waitForLoadState('networkidle');
      expect(errors).toEqual([]);
    });
  }
});
