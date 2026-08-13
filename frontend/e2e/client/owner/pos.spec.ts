import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner POS Workflow', () => {
  test('POS page: katalog produk, action stok tambah/kurang, checkout, pergerakan stok', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const sku = `POS-${runId.slice(-10)}`;
    const name = `E2E POS ${runId.slice(-6)}`;

    const prod = await api.post(`tenants/${TENANT}/products`, {
      data: { sku, name, category: 'POS', unit: 'pcs', salePrice: '25000', costPrice: '15000', minimumStock: '2' },
    });
    expect(prod.status()).toBe(201);
    const productId = (await prod.json()).id;

    const locRes = await api.get(`tenants/${TENANT}/inventory-locations`);
    expect(locRes.status()).toBe(200);
    const locations = await locRes.json();
    expect(locations.length).toBeGreaterThan(0);
    const locationId = locations[0].id;

    const receipt = await api.post(`tenants/${TENANT}/stock-movements/receipts`, {
      data: { product_id: productId, location_id: locationId, quantity: '10', unit_cost: '15000' },
    });
    expect(receipt.status()).toBe(201);

    // ── Halaman POS menampilkan katalog produk + stok ──
    await page.goto(`/app/${TENANT}/pos`);
    await expect(page.getByRole('heading', { name: 'Point of Sales' })).toBeVisible();
    await page.getByPlaceholder('Cari produk, SKU, kategori...').fill(sku);
    const card = page.locator('div.card', { hasText: name }).first();
    await expect(card).toBeVisible();
    await expect(card).toContainText('Stok 10');

    // ── Action Stok → tambah 5 (10 → 15) ──
    await card.getByRole('button', { name: 'Stok' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('button', { name: '+ Tambah stok' }).click();
    await page.getByLabel('Jumlah stok').fill('5');
    await page.getByRole('button', { name: 'Tambah Stok', exact: true }).click();
    await expect(page.getByRole('dialog')).toBeHidden();
    await expect(card).toContainText('Stok 15');

    // ── Action Stok → kurangi 3 (15 → 12) ──
    await card.getByRole('button', { name: 'Stok' }).click();
    await page.getByRole('button', { name: '− Kurangi stok' }).click();
    await page.getByLabel('Jumlah stok').fill('3');
    await page.getByRole('button', { name: 'Kurangi Stok', exact: true }).click();
    await expect(page.getByRole('dialog')).toBeHidden();
    await expect(card).toContainText('Stok 12');

    // ── Keranjang + checkout (2 pcs → stok 10) ──
    await card.getByRole('button', { name: 'Keranjang' }).click();
    await card.getByRole('button', { name: 'Keranjang' }).click();
    await expect(page.getByText('Keranjang (2)')).toBeVisible();
    await page.getByRole('button', { name: 'Bayar & Kurangi Stok' }).click();
    await expect(page.locator('body')).toContainText('berhasil', { timeout: 10_000 });
    await expect(card).toContainText('Stok 10');

    // ── Pergerakan Stok mencatat otomatis ──
    await page.goto(`/app/${TENANT}/inventory/movements`);
    await expect(page.getByRole('heading', { name: 'Pergerakan Stok' })).toBeVisible();
    await page.getByPlaceholder('Cari...').fill(name);
    const row = page.locator('tbody tr', { hasText: name }).first();
    await expect(row).toContainText('Penjualan POS');
    await expect(row).toContainText('10');

    await api.dispose();
  });

  test('POS checkout via API: saldo & pergerakan terkalkulasi benar', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const sku = `POS-API-${runId.slice(-10)}`;
    const name = `E2E POS API ${runId.slice(-6)}`;

    const prod = await api.post(`tenants/${TENANT}/products`, {
      data: { sku, name, category: 'POS', unit: 'pcs', salePrice: '25000', costPrice: '15000' },
    });
    expect(prod.status()).toBe(201);
    const productId = (await prod.json()).id;

    const locations = await (await api.get(`tenants/${TENANT}/inventory-locations`)).json();
    const locationId = locations[0].id;

    await api.post(`tenants/${TENANT}/stock-movements/receipts`, {
      data: { product_id: productId, location_id: locationId, quantity: '10', unit_cost: '15000' },
    });

    const checkout = await api.post(`tenants/${TENANT}/pos/checkout`, {
      data: { items: [{ product_id: productId, quantity: '4' }] },
    });
    expect(checkout.status()).toBe(201);
    const body = await checkout.json();
    expect(body.checkoutNumber).toMatch(/^POS-/);
    expect(body.totalQuantity).toBe('4.00');
    expect(body.movements[0].beforeStock).toBe('10.00');
    expect(body.movements[0].afterStock).toBe('6.00');

    const balances = await (await api.get(`tenants/${TENANT}/stock-balances`)).json();
    const row = balances.find((r: any) => r.productId === productId);
    expect(row.quantity).toBe('6.00');

    const mvs = await (await api.get(`tenants/${TENANT}/stock-movements?pageSize=100`)).json();
    const posMvs = mvs.items.filter((m: any) => m.productId === productId);
    expect(posMvs).toHaveLength(2);
    expect(posMvs[0].type).toBe('out');
    expect(posMvs[0].referenceType).toBe('pos');
    await api.dispose();
  });

  test('POS page: jumlah dibayarkan menghitung kembalian secara real-time', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const sku = `CHK-${runId.slice(-10)}`;
    const name = `E2E Change ${runId.slice(-6)}`;

    const prod = await api.post(`tenants/${TENANT}/products`, {
      data: { sku, name, category: 'POS', unit: 'pcs', salePrice: '25000', costPrice: '15000', minimumStock: '2' },
    });
    expect(prod.status()).toBe(201);
    const productId = (await prod.json()).id;

    const locs = await (await api.get(`tenants/${TENANT}/inventory-locations`)).json();
    const loc = locs[0].id;
    await api.post(`tenants/${TENANT}/stock-movements/receipts`, {
      data: { product_id: productId, location_id: loc, quantity: '10', unit_cost: '15000' },
    });

    await page.goto(`/app/${TENANT}/pos`);
    await expect(page.getByRole('heading', { name: 'Point of Sales' })).toBeVisible();
    await page.getByPlaceholder('Cari produk, SKU, kategori...').fill(sku);
    const card = page.locator('div.card', { hasText: name }).first();
    await expect(card).toBeVisible();
    await card.getByRole('button', { name: 'Keranjang' }).click();
    await card.getByRole('button', { name: 'Keranjang' }).click();
    await expect(page.getByText('Keranjang (2)')).toBeVisible();

    // total = 2 x 25000 = 50000
    const changeRow = page.getByText('Kembalian').locator('..');
    const paidInput = page.locator('input[inputmode="numeric"]').first();
    await expect(paidInput).toBeVisible();

    // dibayar 100000 → kembalian 50000 (real-time)
    await paidInput.fill('100000');
    await expect(changeRow).toContainText('Rp 50.000');

    // dibayar 30000 → uang kurang, checkout terkunci
    await paidInput.fill('30000');
    await expect(page.getByText('Uang dibayarkan kurang Rp 20.000')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Bayar & Kurangi Stok' })).toBeDisabled();

    // tombol Uang Pas → set ke total, kembalian 0, checkout aktif
    await page.getByRole('button', { name: 'Uang Pas' }).click();
    await expect(changeRow).toContainText('Rp 0');
    await expect(page.getByRole('button', { name: 'Bayar & Kurangi Stok' })).toBeEnabled();

    await api.dispose();
  });
});