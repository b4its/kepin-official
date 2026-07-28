import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';

test.describe('Domain Contracts', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];
  let token: string;

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
    token = ctx.token;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/toko-maju/customers returns paginated', async () => {
    const res = await api.get('tenants/toko-maju/customers');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body).toHaveProperty('page');
    expect(body).toHaveProperty('pageSize');
    expect(body).toHaveProperty('total');
  });

  test('POST /tenants/toko-maju/customers creates resource', async () => {
    const runId = uniqueId();
    const name = `E2E-Contract-${runId}`;
    const res = await api.post('tenants/toko-maju/customers', {
      data: { code: `CT-${runId.slice(-12)}`, name, email: '', phone: '', address: 'Test address' },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.name).toBe(name);
  });

  test('GET /tenants/toko-maju/accounts returns list', async () => {
    const res = await api.get('tenants/toko-maju/accounts');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/toko-maju/invoices returns paginated', async () => {
    const res = await api.get('tenants/toko-maju/invoices');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/toko-maju/products returns paginated', async () => {
    const res = await api.get('tenants/toko-maju/products');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/toko-maju/suppliers returns paginated', async () => {
    const res = await api.get('tenants/toko-maju/suppliers');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('PATCH /tenants/toko-maju/customers/:id updates resource', async () => {
    const name = `E2E-Update-${uniqueId()}`;
    const code = `CU-${uniqueId().slice(-12)}`;
    const create = await api.post('tenants/toko-maju/customers', {
      data: { code, name, email: '', phone: '', address: '' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const newName = `${name}-updated`;
    const updateRes = await api.patch(`tenants/toko-maju/customers/${id}`, {
      data: { name: newName },
    });
    expect(updateRes.status()).toBe(200);

    const getRes = await api.get(`tenants/toko-maju/customers/${id}`);
    expect(getRes.status()).toBe(200);
    const updated = await getRes.json();
    expect(updated.name).toBe(newName);
  });

  test('DELETE /tenants/toko-maju/customers/:id removes resource', async () => {
    const name = `E2E-Delete-${uniqueId()}`;
    const code = `CD-${uniqueId().slice(-12)}`;
    const create = await api.post('tenants/toko-maju/customers', {
      data: { code, name, email: '', phone: '', address: '' },
    });
    expect(create.status()).toBe(201);
    const created = await create.json();
    const id = created.id;

    const delRes = await api.delete(`tenants/toko-maju/customers/${id}`);
    expect(delRes.status()).toBe(204);

    const getRes = await api.get(`tenants/toko-maju/customers/${id}`);
    expect([404, 403]).toContain(getRes.status());
  });
});
