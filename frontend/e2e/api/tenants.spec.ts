import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Tenant Endpoints', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/context returns tenant context', async () => {
    const res = await api.get(`tenants/${TENANT}/context`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.tenant).toHaveProperty('id');
    expect(body.tenant).toHaveProperty('slug');
    expect(body.tenant.slug).toBe(TENANT);
  });

  test('GET /tenants/:slug/dashboard returns dashboard data', async () => {
    const res = await api.get(`tenants/${TENANT}/dashboard`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('metrics');
  });
});
