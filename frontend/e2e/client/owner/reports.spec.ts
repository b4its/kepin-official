import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Reports & Export', () => {
  test('reports page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('cash flow tab renders summary and rows', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Arus Kas' }).click();
    await expect(page.getByText('Arus Kas Operasi')).toBeVisible();
    await expect(page.getByText('Net Arus Kas')).toBeVisible();
    await expect(page.getByText('Arus Kas Pendanaan')).toBeVisible();
    await expect(page.getByText('Arus Kas per Bulan')).toBeVisible();
    await expect(page.getByText('Δ Net vs Bulan Lalu')).toBeVisible();
    expect(errors).toEqual([]);
  });

  test('profit-loss tab shows monthly breakdown', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Laba Rugi' }).click();
    await expect(page.getByText('Laba Rugi per Bulan')).toBeVisible();
    await expect(page.getByText('Pendapatan', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Δ Laba vs Bulan Lalu')).toBeVisible();
    expect(errors).toEqual([]);
  });

  test('balance-sheet tab shows monthly breakdown', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Neraca', exact: true }).click();
    await expect(page.getByText('Neraca per Bulan')).toBeVisible();
    await expect(page.getByText('Kewajiban + Ekuitas').first()).toBeVisible();
    await expect(page.getByText('Δ Aset vs Bulan Lalu')).toBeVisible();
    expect(errors).toEqual([]);
  });

  test('export modal shows selected report detail', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByLabel('Jenis laporan untuk ekspor').selectOption('trial');
    await page.getByRole('button', { name: /ekspor/i }).first().click();
    await expect(page.locator('h2', { hasText: 'Neraca Saldo' })).toBeVisible();
    await expect(page.getByText('Debit Periode', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Kredit Akhir', { exact: true }).first()).toBeVisible();
    expect(errors).toEqual([]);
  });

  test('export modal aging detail shows per-entity bucket columns', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByLabel('Jenis laporan untuk ekspor').selectOption('aging-detail');
    await page.getByRole('button', { name: /ekspor/i }).first().click();
    await expect(page.locator('h2', { hasText: 'Aging Detail' })).toBeVisible();
    await expect(page.getByText('Bucket Tertua', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Lancar', { exact: true }).first()).toBeVisible();
    expect(errors).toEqual([]);
  });

  test('export aging excel downloads multi-sheet workbook', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
    page.on('pageerror', (err) => errors.push(String(err)));
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByLabel('Jenis laporan untuk ekspor').selectOption('aging');
    await page.getByRole('button', { name: /ekspor/i }).first().click();
    await expect(page.locator('h2', { hasText: 'Aging' })).toBeVisible();
    const xlsxDownload = page.waitForEvent('download', { timeout: 20000 });
    await page.getByRole('button', { name: 'Excel (.xlsx)' }).click();
    expect((await xlsxDownload).suggestedFilename()).toMatch(/\.xlsx$/);
    expect(errors).toEqual([]);
  });

  test('period comparison toggles and shows delta on metric cards', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('checkbox', { name: /bandingkan dengan periode sebelumnya/i }).check();
    await expect(page.getByLabel('Tanggal mulai pembanding')).toHaveValue(/\d{4}-\d{2}-\d{2}/);
    await expect(page.getByLabel('Tanggal akhir pembanding')).toHaveValue(/\d{4}-\d{2}-\d{2}/);
    await page.getByRole('button', { name: /periode sebelumnya/i }).click();
    await expect(page.getByLabel('Tanggal akhir pembanding')).toHaveValue(/\d{4}-\d{2}-\d{2}/);
    await page.waitForLoadState('networkidle');
    await page.getByRole('checkbox', { name: /bandingkan dengan periode sebelumnya/i }).uncheck();
    expect(errors).toEqual([]);
  });

  test('investor report page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/reports/investor`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('insights page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/insights`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('insights period comparison fills compare range', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/insights`);
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('Pendapatan dan Beban Harian')).toBeVisible();

    await page.getByRole('checkbox', { name: /bandingkan dengan periode sebelumnya/i }).check();
    await expect(page.getByLabel('Tanggal mulai pembanding')).toHaveValue(/\d{4}-\d{2}-\d{2}/);
    await expect(page.getByLabel('Tanggal akhir pembanding')).toHaveValue(/\d{4}-\d{2}-\d{2}/);
    await page.getByRole('button', { name: /periode sebelumnya/i }).click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('checkbox', { name: /bandingkan dengan periode sebelumnya/i }).uncheck();
    expect(errors).toEqual([]);
  });

  test('aging per-customer drill-down opens kartu piutang', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const name = `0E2E Aging ${runId}`;

    const c = await api.post(`tenants/${TENANT}/customers`, {
      data: { code: `C-${runId.slice(-12)}`, name, email: `${runId}@test.com`, phone: '0812', address: 'Test' },
    });
    expect(c.status()).toBe(201);
    const customerId = (await c.json()).id;

    const inv = await api.post(`tenants/${TENANT}/invoices`, {
      data: {
        customer_id: customerId,
        invoice_date: '2026-07-10',
        due_date: '2026-08-10',
        lines: [{ item_name: 'Jasa Konsultasi', quantity: '1', unit_price: '500000' }],
      },
    });
    expect(inv.status()).toBe(201);
    const invoiceId = (await inv.json()).id;
    expect((await api.post(`tenants/${TENANT}/invoices/${invoiceId}/post`)).status()).toBe(200);

    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Aging' }).click();

    const receivableTable = page.locator('div.rounded-lg.border').filter({ hasText: 'Pelanggan' });
    await receivableTable.locator('input[placeholder="Cari..."]').fill(name);
    await expect(receivableTable.locator('tbody tr', { hasText: name })).toHaveCount(1);
    await receivableTable
      .locator('tbody tr', { hasText: name })
      .getByRole('button', { name: 'Kartu piutang' })
      .click();

    const heading = page.getByRole('heading', { name: new RegExp(`Kartu Piutang · ${name}`) });
    await expect(heading).toBeVisible();
    await expect(page.locator('body')).toContainText('Saldo awal Rp 0');
    await expect(page.locator('body')).toContainText('Saldo akhir Rp 500.000');
    await expect(page.getByRole('cell', { name: /INV-/ })).toBeVisible();

    const pdfDownload = page.waitForEvent('download');
    await page.getByRole('button', { name: 'PDF' }).click();
    expect((await pdfDownload).suggestedFilename()).toMatch(/\.pdf$/);

    const pay = await api.post(`tenants/${TENANT}/customer-payments`, {
      data: {
        customer_id: customerId,
        payment_date: '2026-07-25',
        amount: '500000',
        method: 'transfer',
        allocations: [{ invoice_id: invoiceId, amount: '500000' }],
      },
    });
    const paymentId = (await pay.json()).id;
    await api.post(`tenants/${TENANT}/customer-payments/${paymentId}/void`).catch(() => {});
    await api.dispose();
  });

  test('aging asOf: periode berakhir di masa depan menggeser invoice ke bucket >90', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const name = `0E2E AgingAsOf ${runId}`;

    const c = await api.post(`tenants/${TENANT}/customers`, {
      data: { code: `C-${runId.slice(-12)}`, name, email: `${runId}@test.com`, phone: '0812', address: 'Test' },
    });
    expect(c.status()).toBe(201);
    const customerId = (await c.json()).id;

    const inv = await api.post(`tenants/${TENANT}/invoices`, {
      data: {
        customer_id: customerId,
        invoice_date: '2026-07-10',
        due_date: '2026-08-10',
        lines: [{ item_name: 'Jasa Konsultasi', quantity: '1', unit_price: '500000' }],
      },
    });
    expect(inv.status()).toBe(201);
    const invoiceId = (await inv.json()).id;
    expect((await api.post(`tenants/${TENANT}/invoices/${invoiceId}/post`)).status()).toBe(200);

    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Aging' }).click();

    const receivableTable = page.locator('div.rounded-lg.border').filter({ hasText: 'Pelanggan' });
    await receivableTable.locator('input[placeholder="Cari..."]').fill(name);
    const row = receivableTable.locator('tbody tr', { hasText: name });
    await expect(row).toHaveCount(1);
    await expect(row.getByRole('cell').nth(1)).toHaveText(/Rp\s*500\.000/);
    await expect(row.getByRole('cell').nth(5)).toHaveText(/Rp\s*0/);

    await page.getByRole('button', { name: 'Kustom', exact: true }).click();
    await page.locator('input[type="date"]').nth(0).fill('2026-01-01');
    await page.locator('input[type="date"]').nth(1).fill('2026-12-31');
    await page.getByRole('button', { name: 'Terapkan' }).click();

    await expect(row.getByRole('cell').nth(1)).toHaveText(/Rp\s*0/);
    await expect(row.getByRole('cell').nth(5)).toHaveText(/Rp\s*500\.000/);

    await api.post(`tenants/${TENANT}/invoices/${invoiceId}/void`).catch(() => {});
    await api.dispose();
  });

  test('aging per-supplier drill-down opens kartu hutang', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const name = `0E2E AgingSup ${runId}`;

    const prod = await api.post(`tenants/${TENANT}/products`, {
      data: { sku: `SKU-${runId.slice(-12)}`, name: `E2E Aging Barang ${runId}`, unit: 'pcs', cost_price: '400000', sale_price: '500000' },
    });
    expect(prod.status()).toBe(201);
    const productId = (await prod.json()).id;

    const locRes = await api.get(`tenants/${TENANT}/inventory-locations`);
    expect(locRes.status()).toBe(200);
    const locations = await locRes.json();
    expect(locations.length).toBeGreaterThan(0);
    const locationId = locations[0].id;

    const sup = await api.post(`tenants/${TENANT}/suppliers`, {
      data: { code: `SUP-${runId.slice(-12)}`, name, email: `${runId}@test.com`, phone: '0812', address: 'Test' },
    });
    expect(sup.status()).toBe(201);
    const supplierId = (await sup.json()).id;

    const po = await api.post(`tenants/${TENANT}/purchase-orders`, {
      data: {
        supplier_id: supplierId,
        order_date: '2026-07-10',
        lines: [{ product_id: productId, item_name: 'Bahan Baku', quantity: '1', unit_price: '400000' }],
      },
    });
    expect(po.status()).toBe(201);
    const poBody = await po.json();
    const poLineId = poBody.lines[0].id;
    expect((await api.post(`tenants/${TENANT}/purchase-orders/${poBody.id}/send`)).status()).toBe(200);
    expect((await api.post(`tenants/${TENANT}/purchase-orders/${poBody.id}/receive`, {
      data: { location_id: locationId, lines: [{ line_id: poLineId, quantity_received: '1' }] },
    })).status()).toBe(200);

    await page.goto(`/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Aging' }).click();

    const payableTable = page.locator('div.rounded-lg.border').filter({ hasText: 'Pemasok' });
    await payableTable.locator('input[placeholder="Cari..."]').fill(name);
    await expect(payableTable.locator('tbody tr', { hasText: name })).toHaveCount(1);
    await payableTable
      .locator('tbody tr', { hasText: name })
      .getByRole('button', { name: 'Kartu hutang' })
      .click();

    const heading = page.getByRole('heading', { name: new RegExp(`Kartu Hutang · ${name}`) });
    await expect(heading).toBeVisible();
    await expect(page.locator('body')).toContainText('Saldo awal Rp 0');
    await expect(page.locator('body')).toContainText('Saldo akhir Rp 400.000');
    await expect(page.getByRole('cell', { name: /GR-/ })).toBeVisible();

    await api.dispose();
  });
});
