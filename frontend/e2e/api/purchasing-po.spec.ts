import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Purchasing & Purchase Orders', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/suppliers/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/suppliers?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/suppliers/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('code');
    }
  });

  test('PATCH /tenants/:slug/suppliers/:id updates supplier', async () => {
    const runId = uniqueId();
    const code = `SUP-PATCH-${runId.slice(-8)}`;
    const create = await api.post(`tenants/${TENANT}/suppliers`, {
      data: { code, name: `E2E Supp ${runId}`, email: `sup.${runId}@test.com`, phone: '123', address: 'Addr' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const patchRes = await api.patch(`tenants/${TENANT}/suppliers/${id}`, {
      data: { name: `${created.name}-patched` },
    });
    expect(patchRes.status()).toBe(200);
    const patched = await patchRes.json();
    expect(patched.name).toBe(`${created.name}-patched`);
  });

  test('DELETE /tenants/:slug/suppliers/:id removes supplier', async () => {
    const runId = uniqueId();
    const code = `SUP-DEL-${runId.slice(-8)}`;
    const create = await api.post(`tenants/${TENANT}/suppliers`, {
      data: { code, name: `E2E Supp Del ${runId}`, email: `sup.del.${runId}@test.com`, phone: '123', address: 'Addr' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const delRes = await api.delete(`tenants/${TENANT}/suppliers/${id}`);
    expect(delRes.status()).toBe(204);

    const getRes = await api.get(`tenants/${TENANT}/suppliers/${id}`);
    expect([404, 403]).toContain(getRes.status());
  });

  test('GET /tenants/:slug/purchase-orders/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/purchase-orders?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/purchase-orders/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('status');
    }
  });

  test('POST /tenants/:slug/purchase-orders creates draft', async () => {
    const suppList = await api.get(`tenants/${TENANT}/suppliers?pageSize=1`);
    const suppBody = await suppList.json();
    if (suppBody.items.length === 0) {
      const runId = uniqueId();
      const supp = await api.post(`tenants/${TENANT}/suppliers`, {
        data: { code: `PO-${runId.slice(-8)}`, name: `E2E PO Supp ${runId}`, email: `po.sup.${runId}@test.com`, phone: '123', address: 'Addr' },
      });
      expect(supp.status()).toBe(201);
      suppBody.items = [await supp.json()];
    }
    const supplierId = suppBody.items[0].id;

    const prodList = await api.get(`tenants/${TENANT}/products?pageSize=1`);
    const prodBody = await prodList.json();
    let productId: string | undefined;
    if (prodBody.items.length > 0) {
      productId = prodBody.items[0].id;
    }

    const lines: any[] = productId
      ? [{ product_id: productId, item_name: 'E2E PO item', quantity: '10', unit_price: '25000' }]
      : [{ item_name: 'E2E PO item (no product)', quantity: '10', unit_price: '25000' }];

    const runId = uniqueId();
    const res = await api.post(`tenants/${TENANT}/purchase-orders`, {
      data: {
        supplier_id: supplierId,
        order_date: new Date().toISOString().slice(0, 10),
        notes: `E2E PO test ${runId}`,
        lines,
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty('id');
    expect(body.status).toBe('draft');
  });
});
