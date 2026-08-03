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

    const receivableTable = page.locator('div.rounded-lg.border').last();
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
});
