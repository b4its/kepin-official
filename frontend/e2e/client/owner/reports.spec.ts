import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER } from '../../helpers/ids';

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
});
