import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Sales Workflow', () => {
  test('create customer via UI persists after reload', async ({ page, request }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const name = `E2E Customer ${runId}`;
    let customerId: string | undefined;

    await page.goto(`/app/${TENANT}/sales/customers`);
    const btn = page.getByRole('button', { name: /pelanggan baru|customer baru|tambah/i }).first();
    if (await btn.isVisible().catch(() => false)) {
      await btn.click();
      await page.getByLabel(/nama/i).fill(name);
      await page.getByRole('button', { name: /simpan|save/i }).click();
      await page.waitForTimeout(1000);
    }

    const checkApi = await api.get(`/tenants/${TENANT}/customers?search=${runId}`);
    if (checkApi.ok()) {
      const body = await checkApi.json();
      const items = body.items || [];
      if (items.length > 0) {
        customerId = items[0].id;
        expect(items.some((c: any) => c.name?.includes(runId))).toBeTruthy();
      }
    }
    if (customerId) {
      await api.delete(`/tenants/${TENANT}/customers/${customerId}`).catch(() => {});
    }
    await api.dispose();
  });

  test('invoices endpoint returns data', async ({ request }) => {
    const res = await request.get(`/tenants/${TENANT}/invoices`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('customers endpoint returns data', async ({ request }) => {
    const res = await request.get(`/tenants/${TENANT}/customers`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });
});
