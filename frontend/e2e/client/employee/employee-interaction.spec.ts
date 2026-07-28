import { test, expect } from '@playwright/test';
import { DEMO_EMPLOYEE } from '../../helpers/ids';

const TENANT = DEMO_EMPLOYEE.tenant;

test.describe('Employee UI Interaction', () => {
  test('products page loads without errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('notifications page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/notifications`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });
});
