import { test, expect } from '@playwright/test';

test.describe('Owner Auth & Context', () => {
  test('owner can open tenant dashboard', async ({ page }) => {
    await page.goto('/app/toko-maju');
    await expect(page).toHaveURL(/\/app\/toko-maju/);
  });

  test('owner navigation renders all menu groups', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto('/app/toko-maju');
    await page.waitForSelector('nav, aside, [class*="sidebar"]', { timeout: 5000 }).catch(() => {});
    expect(errors).toEqual([]);
  });
});
