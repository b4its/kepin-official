import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Accounting Workflow', () => {
  test('chart of accounts renders and has data', async ({ page, request }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });

    await page.goto(`/app/${TENANT}/accounting/chart-of-accounts`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);

    const res = await request.get(`/tenants/${TENANT}/accounts`);
    expect(res.status()).toBe(200);
  });

  test('journals endpoint returns data', async ({ request }) => {
    const res = await request.get(`/tenants/${TENANT}/journals`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('transactions endpoint returns data', async ({ request }) => {
    const res = await request.get(`/tenants/${TENANT}/transactions`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('create account non-system via API', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const code = `9-${Date.now().toString().slice(-4)}`;
    const name = `E2E Account ${uniqueId()}`;

    const create = await api.post(`/tenants/${TENANT}/accounts`, {
      data: { code, name, type: 'expense', balance: 0, status: 'active' },
    });
    expect(create.status()).toBe(201);

    await api.dispose();
  });
});
