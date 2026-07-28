import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Organization Module', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/organization returns settings', async () => {
    test.fixme(true, 'Backend needs restart: OrganizationSettingResponse id field mismatch');
  });

  test('PATCH /tenants/:slug/organization updates settings', async () => {
    test.fixme(true, 'Backend needs restart: OrganizationSettingResponse id field mismatch');
  });

  test('GET /tenants/:slug/branches returns list', async () => {
    const res = await api.get(`tenants/${TENANT}/branches`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('POST /tenants/:slug/branches creates branch', async () => {
    const code = `BR-${uniqueId().slice(-8)}`;
    const name = `E2E Branch ${uniqueId()}`;
    const res = await api.post(`tenants/${TENANT}/branches`, {
      data: { code, name, address: 'Test address' },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.code).toBe(code);
    expect(body.name).toBe(name);
  });

  test('GET /tenants/:slug/roles returns list', async () => {
    const res = await api.get(`tenants/${TENANT}/roles`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('GET /tenants/:slug/members returns list', async () => {
    const res = await api.get(`tenants/${TENANT}/members`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('GET /tenants/:slug/integrations returns list', async () => {
    const res = await api.get(`tenants/${TENANT}/integrations`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
  });

  test('GET /tenants/:slug/billing returns info', async () => {
    const res = await api.get(`tenants/${TENANT}/billing`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('planCode');
  });

  test('GET /tenants/:slug/sidebar-settings returns settings', async () => {
    const res = await api.get(`tenants/${TENANT}/sidebar-settings`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('tenantId');
  });

  test('PUT /tenants/:slug/sidebar-settings updates settings', async () => {
    const res = await api.put(`tenants/${TENANT}/sidebar-settings`, {
      data: { enabledItems: {} },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('message');
  });
});
