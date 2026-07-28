import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Sales Workflow', () => {
  test('create customer via API and verify in list', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const code = `C-${runId.slice(-12)}`;
    const name = `E2E Customer ${runId}`;
    let customerId: string | undefined;

    const createRes = await api.post(`tenants/${TENANT}/customers`, {
      data: { code, name, email: `${runId}@test.com`, phone: '08123456789', address: 'Test address' },
    });
    expect(createRes.status()).toBe(201);
    const created = await createRes.json();
    customerId = created.id;

    const checkApi = await api.get(`tenants/${TENANT}/customers?search=${runId}`);
    if (checkApi.ok()) {
      const body = await checkApi.json();
      const items = body.items || [];
      expect(items.some((c: any) => c.name?.includes(runId))).toBeTruthy();
    }
    if (customerId) {
      await api.delete(`tenants/${TENANT}/customers/${customerId}`).catch(() => {});
    }
    await api.dispose();
  });

  test('invoices endpoint returns data', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`tenants/${TENANT}/invoices`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    await api.dispose();
  });

  test('customers endpoint returns data', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`tenants/${TENANT}/customers`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    await api.dispose();
  });
});
