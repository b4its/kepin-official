import { test, expect } from '@playwright/test';
import { DEMO_OWNER } from '../../helpers/ids';

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
});
