import { test, expect } from '@playwright/test';

test.describe('Platform Admin', () => {
  test.beforeEach(async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
  });

  test('dashboard admin loads', async ({ page }) => {
    await page.goto('/admin');
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('admin tenants page loads', async ({ page }) => {
    await page.goto('/admin/tenants');
    await expect(page).toHaveURL(/\/admin\/tenants/);
  });

  test('admin users page loads', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page).toHaveURL(/\/admin\/users/);
  });

  test('admin subscriptions page loads', async ({ page }) => {
    await page.goto('/admin/subscriptions');
    await expect(page).toHaveURL(/\/admin\/subscriptions/);
  });

  test('admin notifications page loads', async ({ page }) => {
    await page.goto('/admin/notifications');
    await expect(page).toHaveURL(/\/admin\/notifications/);
  });

  test('admin security page loads', async ({ page }) => {
    await page.goto('/admin/security');
    await expect(page).toHaveURL(/\/admin\/security/);
  });

  test('admin incidents page loads', async ({ page }) => {
    await page.goto('/admin/incidents');
    await expect(page).toHaveURL(/\/admin\/incidents/);
  });

  test('admin audit page loads', async ({ page }) => {
    await page.goto('/admin/audit');
    await expect(page).toHaveURL(/\/admin\/audit/);
  });
});
