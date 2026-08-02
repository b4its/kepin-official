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

  test('customer statement shows posted invoice and payment with running balance', async ({ page }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const runId = uniqueId();
    const name = `0E2E Statement ${runId}`;
    let customerId: string | undefined;

    const c = await api.post(`tenants/${TENANT}/customers`, {
      data: {
        code: `C-${runId.slice(-12)}`,
        name,
        email: `${runId}@test.com`,
        phone: '08123456789',
        address: 'Test address',
      },
    });
    expect(c.status()).toBe(201);
    customerId = (await c.json()).id;

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

    const st = await api.get(`tenants/${TENANT}/customer-statements?customerId=${customerId}`);
    expect(st.status()).toBe(200);
    let body = await st.json();
    expect(body.items).toHaveLength(1);
    expect(body.items[0].credit).toBe('500000.00');
    expect(body.items[0].balance).toBe('500000.00');
    expect(body.closing).toBe('500000.00');

    const pay = await api.post(`tenants/${TENANT}/customer-payments`, {
      data: {
        customer_id: customerId,
        payment_date: '2026-07-25',
        amount: '500000',
        method: 'transfer',
        allocations: [{ invoice_id: invoiceId, amount: '500000' }],
      },
    });
    expect(pay.status()).toBe(201);
    const paymentId = (await pay.json()).id;
    expect((await api.post(`tenants/${TENANT}/customer-payments/${paymentId}/post`)).status()).toBe(200);

    const st2 = await api.get(`tenants/${TENANT}/customer-statements?customerId=${customerId}`);
    expect(st2.status()).toBe(200);
    body = await st2.json();
    expect(body.items).toHaveLength(2);
    expect(body.closing).toBe('0.00');

    await page.goto(`/app/${TENANT}/sales/customers`);
    await page.getByPlaceholder('Cari...').fill(name);
    const row = page.locator('tbody tr', { hasText: name }).first();
    await row.getByRole('button', { name: 'Statement' }).click();
    await expect(page.getByRole('heading', { name: /Kartu Piutang/ })).toBeVisible();
    await expect(page.locator('body')).toContainText('Saldo awal Rp 0 · Saldo akhir Rp 0');
    await expect(page.getByRole('cell', { name: /INV-/ })).toBeVisible();
    await expect(page.getByRole('cell', { name: /PAY-/ })).toBeVisible();

    await api.post(`tenants/${TENANT}/customer-payments/${paymentId}/void`).catch(() => {});
    await api.dispose();
  });
});
