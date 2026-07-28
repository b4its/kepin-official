import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Reporting', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/reports/profit-loss returns data', async () => {
    const res = await api.get(`tenants/${TENANT}/reports/profit-loss`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('summary');
    expect(body).toHaveProperty('rows');
  });

  test('GET /tenants/:slug/reports/balance-sheet returns data', async () => {
    const res = await api.get(`tenants/${TENANT}/reports/balance-sheet`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('rows');
  });

  test('GET /tenants/:slug/reports/cash-flow returns data', async () => {
    const res = await api.get(`tenants/${TENANT}/reports/cash-flow`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('rows');
  });

  test('GET /tenants/:slug/reports/general-ledger returns data', async () => {
    const res = await api.get(`tenants/${TENANT}/reports/general-ledger`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/:slug/reports/receivable-aging returns data', async () => {
    const res = await api.get(`tenants/${TENANT}/reports/receivable-aging`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('buckets');
  });
});
