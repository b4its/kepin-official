import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Notifications & Audit', () => {
  let api: Awaited<ReturnType<typeof loginApi>>['api'];

  test.beforeAll(async () => {
    const ctx = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    api = ctx.api;
  });

  test.afterAll(async () => {
    await api.dispose();
  });

  test('GET /tenants/:slug/notifications returns paginated', async () => {
    const res = await api.get(`tenants/${TENANT}/notifications`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/:slug/notifications/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/notifications?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const detail = await api.get(`tenants/${TENANT}/notifications/${id}`);
      expect(detail.status()).toBe(200);
      const detailBody = await detail.json();
      expect(detailBody).toHaveProperty('id');
      expect(detailBody).toHaveProperty('title');
    }
  });

  test('PATCH /tenants/:slug/notifications/:id/read marks read', async () => {
    const list = await api.get(`tenants/${TENANT}/notifications?pageSize=1`);
    const body = await list.json();
    if (body.items.length > 0) {
      const id = body.items[0].id;
      const readRes = await api.patch(`tenants/${TENANT}/notifications/${id}/read`);
      expect(readRes.status()).toBe(200);
    }
  });

  test('POST /tenants/:slug/notifications/read-all marks all read', async () => {
    const res = await api.post(`tenants/${TENANT}/notifications/read-all`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('count');
  });

  test('GET /tenants/:slug/audit-events returns paginated', async () => {
    const res = await api.get(`tenants/${TENANT}/audit-events`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('GET /tenants/:slug/audit-events/:id returns detail', async () => {
    const list = await api.get(`tenants/${TENANT}/audit-events?pageSize=1`);
    expect(list.status()).toBe(200);
    const body = await list.json();
    if (body.items.length > 0) {
      const item = body.items[0];
      const eventId = item.id;
      if (eventId) {
        const detail = await api.get(`tenants/${TENANT}/audit-events/${eventId}`);
        expect(detail.status()).toBe(200);
        const detailBody = await detail.json();
        expect(detailBody).toHaveProperty('action');
      }
    }
  });
});
