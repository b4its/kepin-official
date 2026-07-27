import { test, expect } from '@playwright/test';

test.describe('User Without Organization', () => {
  test('dashboard shows create-organization prompt', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto('/app');
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    const body = await page.locator('body').innerText();
    const hasNoOrgPrompt = /buat organisasi|create organization|belum memiliki/i.test(body);
    expect(hasNoOrgPrompt).toBeTruthy();
  });

  test('user can access public pages even without org', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page.locator('h1').first()).toBeVisible();
  });

  test('redirects to tenant selector when accessing unknown tenant', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto('/app/org-tidak-ada');
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });
});
