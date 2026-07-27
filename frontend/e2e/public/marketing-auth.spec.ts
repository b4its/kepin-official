import { test, expect } from '@playwright/test';

test.describe('Marketing & Public Pages', () => {
  test('landing page loads and shows hero heading', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto('/');
    await expect(page.locator('h1, h2').first()).toBeVisible();
    expect(errors).toEqual([]);
  });

  test('login page can be opened', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page.getByRole('heading', { name: /masuk/i })).toBeVisible();
  });

  test('register page can be opened', async ({ page }) => {
    await page.goto('/auth/register');
    await expect(page.getByRole('heading', { name: /daftar/i })).toBeVisible();
  });

  test('privacy page loads', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('terms page loads', async ({ page }) => {
    await page.goto('/terms');
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('security page loads', async ({ page }) => {
    await page.goto('/security');
    await expect(page.locator('h1').first()).toBeVisible();
  });
});
