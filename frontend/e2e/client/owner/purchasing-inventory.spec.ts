import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Purchasing & Inventory Workflow', () => {
  test('create product via API and verify in list', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const sku = `SKU-${uniqueId()}`;
    const name = `E2E Product ${uniqueId()}`;

    const create = await api.post(`tenants/${TENANT}/products`, {
      data: { sku, name, category: 'Test', unit: 'pcs', salePrice: '10000', costPrice: '5000', minimumStock: '1', status: 'active' },
    });
    expect(create.status()).toBe(201);

    const list = await api.get(`tenants/${TENANT}/products?search=${sku}`);
    expect(list.ok()).toBeTruthy();
    const body = await list.json();
    const items = body.items || [];
    expect(items.some((p: any) => p.sku === sku)).toBeTruthy();

    await api.dispose();
  });

  test('create supplier via API', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const code = `SUP-${runId.slice(-12)}`;
    const name = `E2E Supplier ${runId}`;

    const create = await api.post(`tenants/${TENANT}/suppliers`, {
      data: { code, name, email: `supplier.${runId}@test.com`, phone: '08123456789', address: 'Test addr' },
    });
    expect(create.status()).toBe(201);

    await api.dispose();
  });

  test('stock movements endpoint returns data', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`tenants/${TENANT}/stock-movements`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    await api.dispose();
  });

  test('purchase orders endpoint returns data', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get(`tenants/${TENANT}/purchase-orders`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    await api.dispose();
  });
});
