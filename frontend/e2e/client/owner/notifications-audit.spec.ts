import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Notifications & Audit', () => {
  test('notifications page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/notifications`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('audit page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/audit`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('notifications API returns list', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`/tenants/${TENANT}/notifications`);
    expect(res.status()).toBe(200);
    await api.dispose();
  });

  test('audit events API returns list', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`/tenants/${TENANT}/audit-events`);
    expect(res.status()).toBe(200);
    await api.dispose();
  });
});
