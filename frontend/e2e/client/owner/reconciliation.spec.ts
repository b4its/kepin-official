import { test, expect, type APIRequestContext } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

async function cleanupStatements(api: APIRequestContext, prefix: string, txnDesc: string) {
  const listRes = await api.get(`tenants/${TENANT}/bank-transactions?pageSize=100`);
  const rows = (await listRes.json()).items ?? [];
  for (const b of rows.filter((x: any) => x.externalId.startsWith(prefix))) {
    await api.delete(`tenants/${TENANT}/bank-transactions/${b.id}`);
  }
  const txnRes = await api.get(`tenants/${TENANT}/transactions?pageSize=100&startDate=2000-01-01&endDate=2099-12-31`);
  const txns = (await txnRes.json()).items ?? [];
  for (const t of txns.filter((x: any) => x.description === txnDesc)) {
    await api.post(`tenants/${TENANT}/transactions/${t.id}/void`, { data: {} });
  }
}

async function fetchAllAccounts(api: APIRequestContext): Promise<any[]> {
  const all: any[] = [];
  let page = 1;
  while (true) {
    const res = await api.get(`tenants/${TENANT}/accounts?pageSize=100&page=${page}`);
    const body = await res.json();
    all.push(...(body.items ?? []));
    if (all.length >= (body.total ?? 0)) break;
    page += 1;
  }
  return all;
}

test.describe('Owner Reconciliation Suggestions', () => {
  test('auto-match suggestion applies and marks statement matched', async ({ page, request }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    await cleanupStatements(api, 'E2E-SUG-', 'e2e auto-match');
    const extId = `E2E-SUG-${uniqueId()}`;
    const date = '2026-06-15';
    const amount = '175000';

    const banksRes = await api.get(`tenants/${TENANT}/bank-accounts`);
    expect(banksRes.status()).toBe(200);
    const bca = (await banksRes.json()).find((b: any) => b.bankName === 'BCA');
    expect(bca).toBeTruthy();

    const accountsRes = await api.get(`tenants/${TENANT}/accounts?pageSize=100`);
    expect(accountsRes.status()).toBe(200);
    const accounts = await fetchAllAccounts(api);
    const cash = accounts.find((a: any) => a.code === '1-1002');
    const income = accounts.find((a: any) => a.type === 'income');
    expect(cash && income).toBeTruthy();

    const stmtRes = await api.post(`tenants/${TENANT}/bank-transactions`, {
      data: { bankAccountId: bca.id, externalId: extId, transactionDate: date, description: 'e2e auto-match', amount },
    });
    expect(stmtRes.status()).toBe(201);
    const stmt = await stmtRes.json();

    const txnRes = await api.post(`tenants/${TENANT}/transactions`, {
      data: { transactionDate: date, type: 'income', description: 'e2e auto-match', amount, accountId: cash.id, counterAccountId: income.id },
    });
    expect(txnRes.status()).toBe(201);
    const txn = await txnRes.json();
    const postRes = await api.post(`tenants/${TENANT}/transactions/${txn.id}/post`, { data: {} });
    expect(postRes.status()).toBe(200);

    await page.goto(`/app/${TENANT}/accounting/reconciliation`);
    await page.waitForLoadState('networkidle');

    const search = page.getByPlaceholder('Cari...').first();
    await search.fill(extId);
    const row = page.getByRole('row').filter({ hasText: extId });
    await expect(row).toBeVisible();
    await expect(row.getByText('Belum dicocokkan')).toBeVisible();
    await row.getByRole('button', { name: 'Saran' }).click();

    await expect(page.getByText('Saran Pencocokan').first()).toBeVisible();
    await expect(page.getByText('Skor 100').first()).toBeVisible();
    await page.getByRole('dialog').getByRole('button', { name: 'Cocokkan' }).first().click();

    await expect(page.getByText('Saran diterapkan dan match dikonfirmasi')).toBeVisible();

    const rowMatched = page.getByRole('row').filter({ hasText: extId });
    await expect(rowMatched.getByText('Terkait')).toBeVisible();

    const matchesRes = await api.get(`tenants/${TENANT}/reconciliation?pageSize=100`);
    const match = (await matchesRes.json()).items?.find((x: any) => x.bankTransactionId === stmt.id);
    if (match) await api.delete(`tenants/${TENANT}/reconciliation/matches/${match.id}`);
    await api.delete(`tenants/${TENANT}/bank-transactions/${stmt.id}`);
    await api.post(`tenants/${TENANT}/transactions/${txn.id}/void`, { data: {} });
  });

  test('csv import adds statements and skips duplicates', async ({ page, request }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    await cleanupStatements(api, 'E2E-CSV-', '');
    const tag = `E2E-CSV-${uniqueId()}`;
    const csvText = `tanggal;deskripsi;jumlah\n2026-06-10;${tag} A;75000\n2026-06-11;${tag} B;-50000`;

    const banksRes = await api.get(`tenants/${TENANT}/bank-accounts`);
    const bca = (await banksRes.json()).find((b: any) => b.bankName === 'BCA');
    expect(bca).toBeTruthy();

    await page.goto(`/app/${TENANT}/accounting/reconciliation`);
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: '+ Impor CSV' }).click();

    const dialog = page.getByRole('dialog');
    await dialog.locator('#csv-bank').selectOption(bca.id);
    await dialog.locator('#csv-text').fill(csvText);
    await dialog.getByRole('button', { name: 'Impor CSV' }).click();

    await expect(page.getByText('2 transaksi diimpor dari CSV')).toBeVisible();
    await page.getByRole('dialog').getByRole('button', { name: 'Tutup' }).last().click();

    await page.getByRole('button', { name: '+ Impor CSV' }).click();
    const dialog2 = page.getByRole('dialog');
    await dialog2.locator('#csv-bank').selectOption(bca.id);
    await dialog2.locator('#csv-text').fill(csvText);
    await dialog2.getByRole('button', { name: 'Impor CSV' }).click();
    await expect(page.getByText('0 transaksi diimpor dari CSV')).toBeVisible();
    await dialog2.getByRole('button', { name: 'Tutup' }).last().click();

    const listRes = await api.get(`tenants/${TENANT}/bank-transactions?pageSize=100&search=CSV-`);
    const rows = (await listRes.json()).items ?? [];
    const tagged = rows.filter((b: any) => b.description.includes(tag));
    expect(tagged.length).toBe(2);
    for (const b of tagged) {
      await api.delete(`tenants/${TENANT}/bank-transactions/${b.id}`);
    }
  });

  test('bulk auto-match applies top suggestions for unmatched statements', async ({ page, request }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    await cleanupStatements(api, 'E2E-BULK-', 'e2e bulk auto-match');
    const tag = `E2E-BULK-${uniqueId()}`;
    const date = '2026-06-20';
    const amount = '265000';

    const banksRes = await api.get(`tenants/${TENANT}/bank-accounts`);
    const bca = (await banksRes.json()).find((b: any) => b.bankName === 'BCA');
    expect(bca).toBeTruthy();

    const accountsRes = await api.get(`tenants/${TENANT}/accounts?pageSize=100`);
    const accounts = await fetchAllAccounts(api);
    const cash = accounts.find((a: any) => a.code === '1-1002');
    const income = accounts.find((a: any) => a.type === 'income');
    expect(cash && income).toBeTruthy();

    const stmtRes = await api.post(`tenants/${TENANT}/bank-transactions`, {
      data: { bankAccountId: bca.id, externalId: tag, transactionDate: date, description: 'e2e bulk auto-match', amount },
    });
    expect(stmtRes.status()).toBe(201);
    const stmt = await stmtRes.json();

    const txnRes = await api.post(`tenants/${TENANT}/transactions`, {
      data: { transactionDate: date, type: 'income', description: 'e2e bulk auto-match', amount, accountId: cash.id, counterAccountId: income.id },
    });
    expect(txnRes.status()).toBe(201);
    const txn = await txnRes.json();
    const postRes = await api.post(`tenants/${TENANT}/transactions/${txn.id}/post`, { data: {} });
    expect(postRes.status()).toBe(200);

    await page.goto(`/app/${TENANT}/accounting/reconciliation`);
    await page.waitForLoadState('networkidle');

    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: 'Cocokkan Semua Saran' }).click();
    await expect(page.getByText(/statement dicocokkan otomatis/).first()).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Hasil Cocokkan Semua Saran' })).toBeVisible();
    await page.getByRole('dialog').getByRole('button', { name: 'Tutup' }).last().click();

    const search = page.getByPlaceholder('Cari...').first();
    await search.fill(tag);
    const rowMatched = page.getByRole('row').filter({ hasText: tag });
    await expect(rowMatched.getByText('Terkait')).toBeVisible();

    const matchesRes = await api.get(`tenants/${TENANT}/reconciliation?pageSize=100`);
    const match = (await matchesRes.json()).items?.find((x: any) => x.bankTransactionId === stmt.id);
    expect(match?.status).toBe('confirmed');
    if (match) await api.delete(`tenants/${TENANT}/reconciliation/matches/${match.id}`);
    await api.delete(`tenants/${TENANT}/bank-transactions/${stmt.id}`);
    await api.post(`tenants/${TENANT}/transactions/${txn.id}/void`, { data: {} });
  });

  test('bank account filter narrows transactions table', async ({ page }) => {
    const errors: string[] = [];
    let bankTxnUrl = '';
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    page.on('request', (req) => { if (req.url().includes('/bank-transactions?')) bankTxnUrl = req.url(); });
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const banksRes = await api.get(`tenants/${TENANT}/bank-accounts`);
    const banks = (await banksRes.json()) as any[];
    expect(banks.length).toBeGreaterThanOrEqual(1);

    await page.goto(`/app/${TENANT}/accounting/reconciliation`);
    await page.waitForLoadState('networkidle');

    const filter = page.getByLabel('Rekening:');
    await expect(filter).toBeVisible();

    await filter.selectOption({ label: `${banks[0].bankName} · ${banks[0].maskedNumber || '-'}` });
    await page.waitForLoadState('networkidle');
    expect(bankTxnUrl).toContain(`bankAccountId=${banks[0].id}`);

    await filter.selectOption({ label: 'Semua rekening' });
    await page.waitForLoadState('networkidle');
    expect(bankTxnUrl).not.toContain('bankAccountId=');
    expect(errors).toEqual([]);
  });
});
