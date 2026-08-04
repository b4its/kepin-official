import { test, expect } from '@playwright/test';
import type { APIRequestContext, Page } from '@playwright/test';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';
const API = (process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1/').replace(/\/+$/, '');
const TENANT = 'toko-maju';
const COUNT = 100;
const TS = Date.now();

const dayAgo = (n: number) => new Date(Date.now() - n * 86400000).toISOString().slice(0, 10);

let token: string;

async function apiPost(request: APIRequestContext, path: string, body: any) {
  const res = await request.post(`${API}/${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    data: body,
  });
  if (!res.ok()) {
    const err = await res.text().catch(() => '');
    throw new Error(`${res.status()}: ${err}`);
  }
  return res.json();
}

async function apiGetTotal(request: APIRequestContext, path: string): Promise<number> {
  const sep = path.includes('?') ? '&' : '?';
  const res = await request.get(`${API}/${path}${sep}pageSize=100&page=1`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) throw new Error(`${res.status()}: ${await res.text().catch(() => '')}`);
  const body = await res.json();
  return body.total ?? body.length ?? 0;
}

async function apiGetList(request: APIRequestContext, path: string): Promise<any[]> {
  const sep = path.includes('?') ? '&' : '?';
  const res = await request.get(`${API}/${path}${sep}pageSize=100`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) throw new Error(`${res.status()}: ${await res.text().catch(() => '')}`);
  const body = await res.json();
  return body.items || [];
}

async function login(page: Page) {
  await page.goto(WEB + '/auth/login');
  await page.waitForLoadState('networkidle');
  await page.locator('#email').fill('budi@tokomaju.com');
  await page.locator('#password').fill('budi123');
  await page.locator('button[type="submit"]').click();
  await page.waitForURL(/\/app\/toko-maju/, { timeout: 15000 });
  token = await page.evaluate(() => localStorage.getItem('kepin_token') || '');
}

test.describe('SEED DATA: 100 records per CRUD page', () => {
  test('Seed all CRUD pages with 100 records each', async ({ page }) => {
    test.setTimeout(600_000);

    console.log('▶️ LOGIN');
    await login(page);
    const { request } = page;
    console.log('   ✅ Logged in');

    // ── 1. CUSTOMERS ──
    console.log('\n═══ 1. CUSTOMERS ═══');
    for (let i = 0; i < COUNT; i++) {
      await apiPost(request, `tenants/${TENANT}/customers`, {
        code: `C-${TS}-${String(i + 1).padStart(4, '0')}`,
        name: `Pelanggan Seeded ${i + 1}`,
        email: `cust${TS}.${i + 1}@seed.test`,
        phone: `081${String(i + 1).padStart(8, '0')}`,
        address: `Jl. Seed No. ${i + 1}`,
      });
    }
    let total = await apiGetTotal(request, `tenants/${TENANT}/customers`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Customers: total=${total}`);

    // ── 2. SUPPLIERS ──
    console.log('\n═══ 2. SUPPLIERS ═══');
    for (let i = 0; i < COUNT; i++) {
      await apiPost(request, `tenants/${TENANT}/suppliers`, {
        code: `S-${TS}-${String(i + 1).padStart(4, '0')}`,
        name: `Pemasok Seeded ${i + 1}`,
        email: `sup${TS}.${i + 1}@seed.test`,
        phone: `082${String(i + 1).padStart(8, '0')}`,
        address: `Jl. Supplier No. ${i + 1}`,
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/suppliers`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Suppliers: total=${total}`);

    // ── 3. PRODUCTS ──
    console.log('\n═══ 3. PRODUCTS ═══');
    for (let i = 0; i < COUNT; i++) {
      await apiPost(request, `tenants/${TENANT}/products`, {
        sku: `SKU-${TS}-${String(i + 1).padStart(4, '0')}`,
        name: `Produk Seeded ${i + 1}`,
        category: i % 3 === 0 ? 'Elektronik' : i % 3 === 1 ? 'Fashion' : 'Makanan',
        unit: 'pcs',
        sale_price: String(10000 + i * 100),
        cost_price: String(7000 + i * 70),
        minimum_stock: String(5 + (i % 10)),
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/products`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Products: total=${total}`);

    // ── 4. ACCOUNTS ──
    console.log('\n═══ 4. CHART OF ACCOUNTS ═══');
    const types = ['asset', 'liability', 'equity', 'income', 'expense'];
    for (let i = 0; i < COUNT; i++) {
      await apiPost(request, `tenants/${TENANT}/accounts`, {
        code: `${TS}-${String(i + 100).padStart(3, '0')}`,
        name: `Akun Seeded ${i + 1}`,
        type: types[i % types.length],
        normal_balance: 'debit',
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/accounts`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Chart of Accounts: total=${total}`);

    // ── 5. BRANCHES ──
    console.log('\n═══ 5. BRANCHES ═══');
    for (let i = 0; i < COUNT; i++) {
      await apiPost(request, `tenants/${TENANT}/branches`, {
        code: `BR-${TS}-${String(i + 1).padStart(4, '0')}`,
        name: `Cabang Seeded ${i + 1}`,
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/branches`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Branches: total=${total}`);

    // ── 6. TRANSACTIONS ──
    console.log('\n═══ 6. TRANSACTIONS ═══');
    const acctList = await apiGetList(request, `tenants/${TENANT}/accounts`);
    const acct1 = acctList[0]?.id || '';
    const acct2 = acctList[Math.min(1, acctList.length - 1)]?.id || '';
    for (let i = 0; i < COUNT; i++) {
      const txnType = i % 2 === 0 ? 'income' : 'expense';
      await apiPost(request, `tenants/${TENANT}/transactions`, {
        transaction_date: dayAgo(i % 7),
        type: txnType,
        description: `Transaksi Seeded ${i + 1}`,
        amount: String(50000 + i * 1000),
        account_id: i % 2 === 0 ? acct1 : acct2,
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/transactions`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Transactions: total=${total}`);

    // ── 7. INVOICES ──
    console.log('\n═══ 7. INVOICES ═══');
    const custList = await apiGetList(request, `tenants/${TENANT}/customers`);
    for (let i = 0; i < COUNT && i < custList.length; i++) {
      const custId = custList[i % custList.length].id;
      const day = 22 + (i % 7);
      await apiPost(request, `tenants/${TENANT}/invoices`, {
        customer_id: custId,
        invoice_date: `2026-07-${String(day).padStart(2, '0')}`,
        due_date: `2026-08-${String(Math.min(day + 14, 30)).padStart(2, '0')}`,
        lines: [
          { item_name: `Item ${i + 1}`, quantity: '1', unit_price: String(100000 + i * 500) },
        ],
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/invoices`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Invoices: total=${total}`);

    // ── 8. JOURNALS ──
    console.log('\n═══ 8. JOURNALS ═══');
    for (let i = 0; i < COUNT; i++) {
      await apiPost(request, `tenants/${TENANT}/journals`, {
        journal_date: dayAgo(i % 7),
        description: `Jurnal Seeded ${i + 1}`,
        lines: [
          { account_id: acct1, debit: String(100000 + i * 1000), credit: '0', description: 'Debit line' },
          { account_id: acct2, debit: '0', credit: String(100000 + i * 1000), description: 'Credit line' },
        ],
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/journals`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Journals: total=${total}`);

    // ── 9. PURCHASE ORDERS ──
    console.log('\n═══ 9. PURCHASE ORDERS ═══');
    const supList = await apiGetList(request, `tenants/${TENANT}/suppliers`);
    for (let i = 0; i < COUNT && i < supList.length; i++) {
      const supId = supList[i % supList.length].id;
      await apiPost(request, `tenants/${TENANT}/purchase-orders`, {
        supplier_id: supId,
        order_date: `2026-07-${String(22 + (i % 7)).padStart(2, '0')}`,
        lines: [
          { item_name: `PO Item ${i + 1}`, quantity: String(1 + (i % 10)), unit_price: String(50000 + i * 500) },
        ],
      });
    }
    total = await apiGetTotal(request, `tenants/${TENANT}/purchase-orders`);
    expect(total).toBeGreaterThanOrEqual(COUNT);
    console.log(`   ✅ Purchase Orders: total=${total}`);

    console.log('\n🎉 SEEDING COMPLETE: 100 records × 9 CRUD pages ✅');
  });
});
