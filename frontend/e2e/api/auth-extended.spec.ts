import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, uniqueEmail, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';

test.describe('Auth Extended', () => {
  test('GET /auth/plans returns subscription plans', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get('auth/plans');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('plans');
    expect(Array.isArray(body.plans)).toBeTruthy();
    await api.dispose();
  });

  test('POST /auth/create-organization creates tenant', async () => {
    const email = uniqueEmail();
    const password = 'test-pass-123!';

    const { api: anon } = await (async () => {
      const { request } = await import('@playwright/test');
      const ctx = await request.newContext({ baseURL: apiURL });
      const res = await ctx.post('auth/register', {
        data: { name: 'Org Test User', email, password },
      });
      expect(res.status()).toBe(201);
      return ctx;
    })();

    const { api } = await loginApi(apiURL, email, password);
    const slug = `e2e-org-${uniqueId().slice(-8).toLowerCase()}`;
    const res = await api.post('auth/create-organization', {
      data: { slug, name: `E2E Org ${uniqueId()}`, plan: 'free' },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('tenant');
    expect(body.tenant.slug).toBe(slug);
    await api.dispose();
  });
});
