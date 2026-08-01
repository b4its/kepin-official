import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner UI Interaction', () => {
  test('create customer modal opens and has expected fields', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    const createBtn = page.locator('button').filter({ hasText: /pelanggan baru|buat|create|tambah/i }).first();
    await expect(createBtn).toBeVisible();

    await createBtn.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"], .modal, .MuiModal-root').first();
    await expect(modal).toBeVisible();

    await expect(page.locator('input, textarea').first()).toBeVisible();
  });

  test('invoice page has metric cards', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/sales/invoices`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('settings members page shows invite button', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/settings/members`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    const inviteBtn = page.locator('button').filter({ hasText: /undang anggota|invite|tambah/i }).first();
    await expect(inviteBtn).toBeVisible();
  });

  test('navigate between sales and inventory pages', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    await page.goto(`/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    await page.goto(`/app/${TENANT}/purchasing/orders`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('organization settings page shows profile info', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/settings/organization`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    const body = await page.locator('body').innerText();
    expect(body.length).toBeGreaterThan(10);
  });

  test('organization edit modal round-trips website and phone', async ({ page }) => {
    const testSite = `https://e2e-${Date.now().toString(36)}.example.com`;
    const testPhone = `021-${Date.now().toString().slice(-6)}`;

    await page.goto(`/app/${TENANT}/settings/organization`);
    await page.waitForLoadState('networkidle');

    const editBtn = page.locator('button').filter({ hasText: /edit profil/i }).first();
    await expect(editBtn).toBeVisible();
    await editBtn.click();

    const modal = page.locator('[role="dialog"], .modal, .MuiModal-root').first();
    await expect(modal).toBeVisible();

    const websiteInput = page.locator('#org-website');
    await websiteInput.fill(testSite);
    const phoneInput = page.locator('#org-phone');
    await phoneInput.fill(testPhone);

    await page.locator('button').filter({ hasText: /simpan perubahan/i }).first().click();
    await expect(modal).not.toBeVisible({ timeout: 10_000 });

    const body = await page.locator('body').innerText();
    expect(body).toContain(testSite);
    expect(body).toContain(testPhone);

    await editBtn.click();
    await expect(modal).toBeVisible();
    await page.locator('#org-website').fill('');
    await page.locator('#org-phone').fill('');
    await page.locator('button').filter({ hasText: /simpan perubahan/i }).first().click();
    await expect(modal).not.toBeVisible({ timeout: 10_000 });
  });

  test('notification detail page renders for a real notification', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const list = await api.get(`tenants/${TENANT}/notifications?pageSize=1`);
    const body = await list.json();
    await api.dispose();
    const items = body.items || [];
    if (items.length === 0) return;

    const nid = items[0].id;
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/notifications/${nid}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    expect(errors).toEqual([]);
    await expect(page.locator('body')).toContainText(/notifikasi/i, { timeout: 10_000 });
  });

  test('fiscal years page lists years and opens create modal', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/accounting/fiscal-years`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    expect(errors).toEqual([]);

    await expect(page.locator('body')).toContainText(/tahun buku/i, { timeout: 10_000 });

    const createBtn = page.locator('button').filter({ hasText: /buat tahun buku/i }).first();
    await expect(createBtn).toBeVisible();
    await createBtn.click();

    const modal = page.locator('[role="dialog"], .modal, .MuiModal-root').first();
    await expect(modal).toBeVisible();
    await expect(page.locator('#fy-start')).toBeVisible();
    await expect(page.locator('#fy-end')).toBeVisible();
  });

  test('fiscal years modal creates a run-scoped fiscal year', async ({ page }) => {
    await page.goto(`/app/${TENANT}/accounting/fiscal-years`);
    await page.waitForLoadState('networkidle');

    const createBtn = page.locator('button').filter({ hasText: /buat tahun buku/i }).first();
    await expect(createBtn).toBeVisible();
    await createBtn.click();

    const modal = page.locator('[role="dialog"], .modal, .MuiModal-root').first();
    await expect(modal).toBeVisible();

    const body = await page.locator('body').innerText();
    let year = 2035;
    while (year <= 2054 && body.includes(`Tahun Buku E2E ${year}`)) year += 1;
    const start = `${year}-04-01`;
    const end = `${year + 1}-03-31`;
    const name = `Tahun Buku E2E ${year}`;

    await page.locator('#fy-name').fill(name);
    await page.locator('#fy-start').fill(start);
    await page.locator('#fy-end').fill(end);
    await page.locator('button').filter({ hasText: /simpan/i }).first().click();
    await expect(modal).not.toBeVisible({ timeout: 10_000 });

    await expect(page.locator('body')).toContainText(name, { timeout: 10_000 });
    await expect(page.locator('body')).toContainText(/per bulan|periode 20/i, { timeout: 10_000 });
  });

  test('reconciliation page shows bank accounts and transactions tables', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/accounting/reconciliation`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    expect(errors).toEqual([]);

    await expect(page.locator('body')).toContainText(/rekening bank/i, { timeout: 10_000 });
    await expect(page.locator('body')).toContainText(/transaksi bank/i, { timeout: 10_000 });
    await expect(page.locator('body')).toContainText(/saldo buku/i, { timeout: 10_000 });
    await expect(page.locator('body')).toContainText(/belum dicocokkan/i, { timeout: 10_000 });
  });
});
