import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Accounting Detailed', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/accounts/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/accounts?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/accounts/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('code');
    }
  });

  test('PATCH /tenants/:slug/accounts/:id updates account', async () => {
    const runId = uniqueId();
    const code = `99${Date.now().toString().slice(-4)}`;
    const create = await api.post(`tenants/${TENANT}/accounts`, {
      data: { code, name: `E2E Acct ${runId}`, type: 'expense', normalBalance: 'debit' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const patchRes = await api.patch(`tenants/${TENANT}/accounts/${id}`, {
      data: { name: `${created.name}-patched` },
    });
    expect(patchRes.status()).toBe(200);
    const patched = await patchRes.json();
    expect(patched.name).toBe(`${created.name}-patched`);
  });

  test('DELETE /tenants/:slug/accounts/:id - non-system account', async () => {
    const runId = uniqueId();
    const code = `98${Date.now().toString().slice(-4)}`;
    const create = await api.post(`tenants/${TENANT}/accounts`, {
      data: { code, name: `E2E Del Acct ${runId}`, type: 'expense', normalBalance: 'debit' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const delRes = await api.delete(`tenants/${TENANT}/accounts/${id}`);
    expect(delRes.status()).toBe(204);

    const getRes = await api.get(`tenants/${TENANT}/accounts/${id}`);
    expect([404, 403]).toContain(getRes.status());
  });

  test('GET /tenants/:slug/accounts/:id/balance returns balance', async () => {
    const list = await api.get(`tenants/${TENANT}/accounts?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const balance = await api.get(`tenants/${TENANT}/accounts/${id}/balance`);
      expect(balance.status()).toBe(200);
      const balBody = await balance.json();
      expect(balBody).toHaveProperty('balance');
    }
  });

  test('POST /tenants/:slug/transactions creates draft', async () => {
    const accountList = await api.get(`tenants/${TENANT}/accounts?pageSize=1`);
    const accBody = await accountList.json();
    if (accBody.items.length === 0) throw new Error('No accounts found');

    const accountId = accBody.items[0].id;
    const runId = uniqueId();
    const res = await api.post(`tenants/${TENANT}/transactions`, {
      data: {
        transaction_date: new Date().toISOString().slice(0, 10),
        type: 'expense',
        description: `E2E Transaction ${runId}`,
        amount: '100000',
        account_id: accountId,
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty('id');
    expect(body.status).toBe('draft');
  });

  test('GET /tenants/:slug/transactions/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/transactions?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/transactions/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
    }
  });

  test('PATCH /tenants/:slug/transactions/:id updates draft', async () => {
    const accountList = await api.get(`tenants/${TENANT}/accounts?pageSize=1`);
    const accBody = await accountList.json();
    if (accBody.items.length === 0) throw new Error('No accounts found');
    const accountId = accBody.items[0].id;

    const runId = uniqueId();
    const create = await api.post(`tenants/${TENANT}/transactions`, {
      data: { transaction_date: new Date().toISOString().slice(0, 10), type: 'expense', description: `E2E Txn ${runId}`, amount: '50000', account_id: accountId },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const patchRes = await api.patch(`tenants/${TENANT}/transactions/${id}`, {
      data: { description: `${created.description}-patched`, amount: '75000' },
    });
    expect(patchRes.status()).toBe(200);
    const patched = await patchRes.json();
    expect(patched.description).toBe(`${created.description}-patched`);
  });

  test('POST /tenants/:slug/journals creates draft', async () => {
    const accountList = await api.get(`tenants/${TENANT}/accounts?pageSize=2`);
    const accBody = await accountList.json();
    if (accBody.items.length >= 2) {
      const acc1 = accBody.items[0].id;
      const acc2 = accBody.items[1].id;
      const runId = uniqueId();
      const res = await api.post(`tenants/${TENANT}/journals`, {
        data: {
          journal_date: new Date().toISOString().slice(0, 10),
          description: `E2E Journal ${runId}`,
          lines: [
            { account_id: acc1, debit: '100000', credit: '0' },
            { account_id: acc2, debit: '0', credit: '100000' },
          ],
        },
      });
      expect(res.status()).toBe(201);
      const body = await res.json();
      expect(body).toHaveProperty('id');
      expect(body.status).toBe('draft');
    }
  });

  test('GET /tenants/:slug/journals/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/journals?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/journals/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('lines');
    }
  });
});
