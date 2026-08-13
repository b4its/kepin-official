import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Dashboard Aging Summary', () => {
  test('shows piutang & hutang aging summary from seeded data', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();

    const c = await api.post(`tenants/${TENANT}/customers`, {
      data: { code: `C-${runId.slice(-12)}`, name: `0E2E DashCust ${runId}`, email: `${runId}@test.com`, phone: '0812', address: 'Test' },
    });
    expect(c.status()).toBe(201);
    const customerId = (await c.json()).id;

    const inv = await api.post(`tenants/${TENANT}/invoices`, {
      data: {
        customer_id: customerId,
        invoice_date: '2026-07-10',
        due_date: '2026-08-10',
        lines: [{ item_name: 'Jasa Konsultasi', quantity: '1', unit_price: '500000' }],
      },
    });
    expect(inv.status()).toBe(201);
    const invoiceId = (await inv.json()).id;
    expect((await api.post(`tenants/${TENANT}/invoices/${invoiceId}/post`)).status()).toBe(200);

    const prod = await api.post(`tenants/${TENANT}/products`, {
      data: { sku: `SKU-${runId.slice(-12)}`, name: `E2E Dash Barang ${runId}`, unit: 'pcs', cost_price: '400000', sale_price: '500000' },
    });
    expect(prod.status()).toBe(201);
    const productId = (await prod.json()).id;

    const locRes = await api.get(`tenants/${TENANT}/inventory-locations`);
    expect(locRes.status()).toBe(200);
    const locations = await locRes.json();
    expect(locations.length).toBeGreaterThan(0);
    const locationId = locations[0].id;

    const sup = await api.post(`tenants/${TENANT}/suppliers`, {
      data: { code: `SUP-${runId.slice(-12)}`, name: `0E2E DashSup ${runId}`, email: `${runId}@test.com`, phone: '0812', address: 'Test' },
    });
    expect(sup.status()).toBe(201);
    const supplierId = (await sup.json()).id;

    const po = await api.post(`tenants/${TENANT}/purchase-orders`, {
      data: {
        supplier_id: supplierId,
        order_date: '2026-07-10',
        lines: [{ product_id: productId, item_name: 'Bahan Baku', quantity: '1', unit_price: '400000' }],
      },
    });
    expect(po.status()).toBe(201);
    const poBody = await po.json();
    expect((await api.post(`tenants/${TENANT}/purchase-orders/${poBody.id}/send`)).status()).toBe(200);
    expect((await api.post(`tenants/${TENANT}/purchase-orders/${poBody.id}/receive`, {
      data: { location_id: locationId, lines: [{ line_id: poBody.lines[0].id, quantity_received: '1' }] },
    })).status()).toBe(200);

    await page.goto(`/app/${TENANT}`);
    await page.waitForLoadState('networkidle');

    const arCard = page.locator('div.card').filter({ hasText: 'Piutang Usaha' });
    await expect(arCard).toBeVisible();
    await expect(arCard).toContainText('Lancar');
    const arTotal = Number((await arCard.locator('p.text-2xl').textContent())?.replace(/[^\d]/g, '') ?? '0');
    expect(arTotal).toBeGreaterThanOrEqual(500000);

    const apCard = page.locator('div.card').filter({ hasText: 'Hutang Usaha' });
    await expect(apCard).toBeVisible();
    await expect(apCard).toContainText('1-30');
    const apTotal = Number((await apCard.locator('p.text-2xl').textContent())?.replace(/[^\d]/g, '') ?? '0');
    expect(apTotal).toBeGreaterThanOrEqual(400000);

    await arCard.getByRole('link', { name: /Lihat laporan/ }).click();
    await expect(page.getByRole('heading', { name: 'Piutang per Bucket' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Hutang per Bucket' })).toBeVisible();

    await api.dispose();
  });
});
