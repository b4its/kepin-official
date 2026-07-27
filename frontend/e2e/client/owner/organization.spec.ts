import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Organization, Members & Sidebar', () => {
  test('organization settings page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/settings/organization`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('members page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/settings/members`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('sidebar settings page loads for owner', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/settings/sidebar`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('branches page loads', async ({ page }) => {
    await page.goto(`/app/${TENANT}/settings/branches`);
    await expect(page).toHaveURL(/\/settings\/branches/);
  });

  test('roles page loads', async ({ page }) => {
    await page.goto(`/app/${TENANT}/settings/roles`);
    await expect(page).toHaveURL(/\/settings\/roles/);
  });

  test('billing page loads', async ({ page }) => {
    await page.goto(`/app/${TENANT}/settings/billing`);
    await expect(page).toHaveURL(/\/settings\/billing/);
  });

  test('integrations page loads', async ({ page }) => {
    await page.goto(`/app/${TENANT}/settings/integrations`);
    await expect(page).toHaveURL(/\/settings\/integrations/);
  });

  test('members API returns list', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`/tenants/${TENANT}/org/members`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    await api.dispose();
  });

  test('sidebar settings can be fetched and updated', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const get = await api.get(`/tenants/${TENANT}/sidebar-settings`);
    expect(get.status()).toBe(200);

    const put = await api.put(`/tenants/${TENANT}/sidebar-settings`, {
      data: { enabledItems: { sales_invoices: true, inventory_products: false } },
    });
    expect(put.status()).toBe(200);
    await api.dispose();
  });
});
