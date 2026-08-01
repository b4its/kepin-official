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
