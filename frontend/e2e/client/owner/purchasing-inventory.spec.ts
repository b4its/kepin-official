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

  test('supplier statement shows receipt and payment with running balance', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    let supplierId: string | undefined;

    const prod = await api.post(`tenants/${TENANT}/products`, {
      data: { sku: `SKU-${runId.slice(-12)}`, name: `E2E Barang ${runId}`, unit: 'pcs', cost_price: '400000', sale_price: '500000' },
    });
    expect(prod.status()).toBe(201);
    const productId = (await prod.json()).id;

    const locRes = await api.get(`tenants/${TENANT}/inventory-locations`);
    expect(locRes.status()).toBe(200);
    const locations = await locRes.json();
    expect(locations.length).toBeGreaterThan(0);
    const locationId = locations[0].id;

    const sup = await api.post(`tenants/${TENANT}/suppliers`, {
      data: { code: `SUP-${runId.slice(-12)}`, name: `0E2E Supplier ${runId}`, email: `supplier.${runId}@test.com`, phone: '08123456789', address: 'Test addr' },
    });
    expect(sup.status()).toBe(201);
    supplierId = (await sup.json()).id;

    const po = await api.post(`tenants/${TENANT}/purchase-orders`, {
      data: {
        supplier_id: supplierId,
        order_date: '2026-08-01',
        lines: [{ product_id: productId, item_name: 'Bahan Baku', quantity: '1', unit_price: '400000' }],
      },
    });
    expect(po.status()).toBe(201);
    const poBody = await po.json();
    const poId = poBody.id;
    const poLineId = poBody.lines[0].id;
    expect((await api.post(`tenants/${TENANT}/purchase-orders/${poId}/send`)).status()).toBe(200);
    expect((await api.post(`tenants/${TENANT}/purchase-orders/${poId}/receive`, {
      data: { location_id: locationId, lines: [{ line_id: poLineId, quantity_received: '1' }] },
    })).status()).toBe(200);

    const st = await api.get(`tenants/${TENANT}/supplier-statements?supplierId=${supplierId}`);
    expect(st.status()).toBe(200);
    let body = await st.json();
    expect(body.items).toHaveLength(1);
    expect(body.items[0].reference).toMatch(/^GR-/);
    expect(body.items[0].credit).toBe('400000.00');
    expect(body.closing).toBe('400000.00');

    const pay = await api.post(`tenants/${TENANT}/supplier-payments`, {
      data: { supplier_id: supplierId, payment_date: new Date().toISOString().slice(0, 10), amount: '400000', method: 'transfer' },
    });
    expect(pay.status()).toBe(201);
    const paymentId = (await pay.json()).id;
    expect((await api.post(`tenants/${TENANT}/supplier-payments/${paymentId}/post`)).status()).toBe(200);

    const st2 = await api.get(`tenants/${TENANT}/supplier-statements?supplierId=${supplierId}`);
    expect(st2.status()).toBe(200);
    body = await st2.json();
    expect(body.items).toHaveLength(2);
    expect(body.items[1].reference).toMatch(/^SPAY-/);
    expect(body.closing).toBe('0.00');

    await page.goto(`/app/${TENANT}/purchasing/suppliers`);
    await page.getByPlaceholder('Cari...').fill(`0E2E Supplier ${runId}`);
    const row = page.locator('tbody tr', { hasText: `0E2E Supplier ${runId}` }).first();
    await row.getByRole('button', { name: 'Statement' }).click();
    await expect(page.getByRole('heading', { name: /Kartu Hutang/ })).toBeVisible();
    await expect(page.locator('body')).toContainText('Saldo awal Rp 0 · Saldo akhir Rp 0');
    await expect(page.getByRole('cell', { name: /^GR-/ })).toBeVisible();
    await expect(page.getByRole('cell', { name: /SPAY-/ })).toBeVisible();

    await api.post(`tenants/${TENANT}/supplier-payments/${paymentId}/void`).catch(() => {});
    await api.dispose();
  });
});
