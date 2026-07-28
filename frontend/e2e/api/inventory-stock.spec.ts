import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Inventory & Stock', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/products/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/products?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/products/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('sku');
    }
  });

  test('PATCH /tenants/:slug/products/:id updates product', async () => {
    const runId = uniqueId();
    const sku = `SKU-PATCH-${runId.slice(-8)}`;
    const create = await api.post(`tenants/${TENANT}/products`, {
      data: { sku, name: `E2E Patch ${runId}`, category: 'Test', unit: 'pcs', salePrice: '15000', costPrice: '7000', minimumStock: '2', status: 'active' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const patchRes = await api.patch(`tenants/${TENANT}/products/${id}`, {
      data: { name: `${created.name}-patched`, salePrice: '20000' },
    });
    expect(patchRes.status()).toBe(200);
    const patched = await patchRes.json();
    expect(patched.name).toBe(`${created.name}-patched`);
  });

  test('DELETE /tenants/:slug/products/:id removes product', async () => {
    const runId = uniqueId();
    const sku = `SKU-DEL-${runId.slice(-8)}`;
    const create = await api.post(`tenants/${TENANT}/products`, {
      data: { sku, name: `E2E Delete ${runId}`, category: 'Test', unit: 'pcs', salePrice: '10000', costPrice: '5000', minimumStock: '1', status: 'active' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const delRes = await api.delete(`tenants/${TENANT}/products/${id}`);
    expect(delRes.status()).toBe(204);

    const getRes = await api.get(`tenants/${TENANT}/products/${id}`);
    expect([404, 403]).toContain(getRes.status());
  });

  test('GET /tenants/:slug/stock-balances returns list', async () => {
    const res = await api.get(`tenants/${TENANT}/stock-balances`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
  });
});
