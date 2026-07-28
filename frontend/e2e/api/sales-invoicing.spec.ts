import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Sales & Invoicing', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('POST /tenants/:slug/customer-payments returns list', async () => {
    const res = await api.get(`tenants/${TENANT}/customer-payments`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/:slug/invoices/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/invoices?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/invoices/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('status');
    }
  });

  test('POST /tenants/:slug/invoices creates draft invoice', async () => {
    const custList = await api.get(`tenants/${TENANT}/customers?pageSize=1`);
    const custBody = await custList.json();
    if (custBody.items.length === 0) {
      const runId = uniqueId();
      const cust = await api.post(`tenants/${TENANT}/customers`, {
        data: { code: `INV-${runId.slice(-12)}`, name: `E2E Inv Cust ${runId}`, email: '', phone: '', address: '' },
      });
      expect(cust.status()).toBe(201);
      custBody.items = [await cust.json()];
    }
    const customerId = custBody.items[0].id;

    const prodList = await api.get(`tenants/${TENANT}/products?pageSize=1`);
    const prodBody = await prodList.json();
    let productId: string | undefined;
    if (prodBody.items.length > 0) {
      productId = prodBody.items[0].id;
    }

    const lines: any[] = productId
      ? [{ product_id: productId, item_name: 'E2E test item', quantity: '1', unit_price: '50000' }]
      : [{ item_name: 'E2E test item (no product)', quantity: '1', unit_price: '50000' }];

    const runId = uniqueId();
    const res = await api.post(`tenants/${TENANT}/invoices`, {
      data: {
        customer_id: customerId,
        invoice_date: new Date().toISOString().slice(0, 10),
        due_date: new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
        notes: `E2E test invoice ${runId}`,
        lines,
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty('id');
    expect(body.status).toBe('draft');
  });

  test('GET /tenants/:slug/customers/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/customers?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/customers/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('code');
    }
  });
});
