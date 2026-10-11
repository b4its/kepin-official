import { test, expect, request } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';

/**
 * Regresi untuk provisioning tenant baru:
 * organisasi baru harus otomatis memiliki cabang, lokasi inventaris default,
 * dan akun GL default agar alur inventori (POS, penerimaan stok) langsung jalan.
 * Tanpa provisioning ini, penambahan stok gagal dengan
 * "Tidak ada lokasi inventaris aktif" / "Akun default tidak ditemukan".
 */
async function loginAsNewUser() {
  const email = `e2e.prov.${uniqueId()}@test.example`;
  const password = 'rahasia123';
  const anonymous = await request.newContext({ baseURL: apiURL });
  const reg = await anonymous.post('auth/register', {
    data: { name: 'E2E Provision', email, password },
  });
  expect(reg.status()).toBe(201);
  await anonymous.dispose();
  return loginApi(apiURL, email, password);
}

test.describe('Tenant inventory provisioning', () => {
  test('organisasi baru langsung punya lokasi inventaris & akun GL default', async () => {
    const { api } = await loginAsNewUser();
    const slug = `e2e-prov-${uniqueId().replace(/[^a-z0-9]/gi, '')}`.slice(0, 40);

    const create = await api.post('auth/create-organization', {
      data: { name: `E2E Provision ${slug}`, slug, plan: 'free' },
    });
    expect(create.status()).toBe(200);

    // 1) Lokasi inventaris default tersedia
    const locationsRes = await api.get(`tenants/${slug}/inventory-locations`);
    expect(locationsRes.status()).toBe(200);
    const locations = await locationsRes.json();
    expect(Array.isArray(locations)).toBeTruthy();
    expect(locations.length).toBeGreaterThan(0);
    expect(locations[0].status).toBe('active');

    // 2) Cabang default tersedia
    const branches = await (await api.get(`tenants/${slug}/branches`)).json();
    expect(branches.length).toBeGreaterThan(0);

    // 3) Akun GL default tersedia (kode yang dibutuhkan modul inventori)
    const accountsBody = await (await api.get(`tenants/${slug}/accounts?pageSize=100`)).json();
    const codes = new Set(accountsBody.items.map((a: any) => a.code));
    for (const code of ['1-3001', '6-1001', '3-4001']) {
      expect(codes.has(code), `akun default ${code} harus tersedia`).toBeTruthy();
    }

    await api.dispose();
  });

  test('penerimaan stok pada tenant baru berhasil & memperbarui saldo', async () => {
    const { api } = await loginAsNewUser();
    const slug = `e2e-stk-${uniqueId().replace(/[^a-z0-9]/gi, '')}`.slice(0, 40);

    const create = await api.post('auth/create-organization', {
      data: { name: `E2E Stok ${slug}`, slug, plan: 'free' },
    });
    expect(create.status()).toBe(200);

    const locations = await (await api.get(`tenants/${slug}/inventory-locations`)).json();
    const locationId = locations[0].id;

    // Produk baru menyimpan minimum stock dengan benar.
    const productRes = await api.post(`tenants/${slug}/products`, {
      data: {
        sku: 'E2E-STK-1',
        name: 'Produk Stok E2E',
        category: 'Test',
        unit: 'pcs',
        salePrice: '15000',
        costPrice: '8000',
        minimumStock: '50',
      },
    });
    expect(productRes.status()).toBe(201);
    const product = await productRes.json();
    expect(Number(product.minimumStock)).toBe(50);

    // Penerimaan stok awal.
    const receipt = await api.post(`tenants/${slug}/stock-movements/receipts`, {
      data: {
        product_id: product.id,
        location_id: locationId,
        quantity: '75',
        unit_cost: '8000',
        reason: 'Stok awal e2e',
      },
    });
    expect(receipt.status()).toBe(201);

    const balances = await (await api.get(`tenants/${slug}/stock-balances`)).json();
    const balance = balances.find((b: any) => b.productId === product.id);
    expect(balance).toBeTruthy();
    expect(Number(balance.quantity)).toBe(75);

    await api.dispose();
  });
});
