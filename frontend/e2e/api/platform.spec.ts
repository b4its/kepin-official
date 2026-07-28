import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_ADMIN, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';

test.describe('Platform Admin', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];
  let adminToken: string;

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_ADMIN.email, DEMO_ADMIN.password);
    api = ctx.api;
    adminToken = ctx.token;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /platform/dashboard returns metrics', async () => {
    const res = await api.get('platform/dashboard');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.metrics).toHaveProperty('activeTenants');
    expect(body.metrics).toHaveProperty('mrr');
  });

  test('GET /platform/tenants returns paginated list', async () => {
    const res = await api.get('platform/tenants');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body.items.length).toBeGreaterThanOrEqual(1);
  });

  test('GET /platform/users returns paginated list', async () => {
    const res = await api.get('platform/users');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body.items.length).toBeGreaterThanOrEqual(1);
  });

  test('GET /platform/subscriptions returns paginated list', async () => {
    const res = await api.get('platform/subscriptions');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /platform/subscription-events returns paginated list', async () => {
    const res = await api.get('platform/subscription-events');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /platform/incidents returns paginated list', async () => {
    const res = await api.get('platform/incidents');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /platform/audit-events returns paginated list', async () => {
    const res = await api.get('platform/audit-events');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /platform/health-summary returns summary', async () => {
    const res = await api.get('platform/health-summary');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('status');
  });
});
