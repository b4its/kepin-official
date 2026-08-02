import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Reconciliation Suggestions', () => {
  test('auto-match suggestion applies and marks statement matched', async ({ page, request }) => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const extId = `E2E-SUG-${uniqueId()}`;
    const date = '2026-06-15';
    const amount = '175000';

    const banksRes = await api.get(`tenants/${TENANT}/bank-accounts`);
    expect(banksRes.status()).toBe(200);
    const bca = (await banksRes.json()).find((b: any) => b.bankName === 'BCA');
    expect(bca).toBeTruthy();

    const accountsRes = await api.get(`tenants/${TENANT}/accounts?pageSize=100`);
    expect(accountsRes.status()).toBe(200);
    const accounts = await accountsRes.json();
    const cash = accounts.items.find((a: any) => a.code === '1-1002');
    const income = accounts.items.find((a: any) => a.type === 'income');
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

    const row = page.getByRole('row').filter({ hasText: extId });
    await expect(row).toBeVisible();
    await expect(row.getByText('Belum dicocokkan')).toBeVisible();
    await row.getByRole('button', { name: 'Saran' }).click();

    await expect(page.getByText('Saran Pencocokan').first()).toBeVisible();
    await expect(page.getByText('Skor 100')).toBeVisible();
    await page.getByRole('button', { name: 'Cocokkan' }).first().click();

    await expect(page.getByText('Saran diterapkan dan match dikonfirmasi')).toBeVisible();

    const rowMatched = page.getByRole('row').filter({ hasText: extId });
    await expect(rowMatched.getByText('Terkait')).toBeVisible();

    const matchesRes = await api.get(`tenants/${TENANT}/reconciliation?pageSize=100`);
    const match = (await matchesRes.json()).items?.find((x: any) => x.bankTransactionId === stmt.id);
    if (match) await api.delete(`tenants/${TENANT}/reconciliation/matches/${match.id}`);
    await api.delete(`tenants/${TENANT}/bank-transactions/${stmt.id}`);
    await api.post(`tenants/${TENANT}/transactions/${txn.id}/void`, { data: {} });
  });
});
