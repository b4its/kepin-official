import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { uniqueEmail, DEMO_OWNER } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';

test.describe('Auth API', () => {
  test('login valid user returns JWT and tenants', async () => {
    const { api, token } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    expect(token).toBeTruthy();
    expect(typeof token).toBe('string');
    const res = await api.get('/auth/me');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.email).toBe(DEMO_OWNER.email);
    expect(body.tenants.length).toBeGreaterThanOrEqual(1);
    expect(body.tenants.some((t: any) => t.slug === DEMO_OWNER.tenant)).toBeTruthy();
    await api.dispose();
  });

  test('login wrong password returns 401', async () => {
    const anonymous = (await import('@playwright/test')).request;
    const ctx = await anonymous.newContext({ baseURL: apiURL });
    const res = await ctx.post('/auth/login', {
      data: { email: DEMO_OWNER.email, password: 'wrong-password-123!' },
    });
    expect(res.status()).toBe(401);
    await ctx.dispose();
  });

  test('register creates new user', async () => {
    const email = uniqueEmail();
    const anonymous = (await import('@playwright/test')).request;
    const ctx = await anonymous.newContext({ baseURL: apiURL });
    const res = await ctx.post('/auth/register', {
      data: { name: 'E2E Test User', email, password: 'E2E-password-123' },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.email).toBe(email);
    expect(body.message).toContain('Registrasi berhasil');
    await ctx.dispose();
  });

  test('register duplicate email returns 409', async () => {
    const anonymous = (await import('@playwright/test')).request;
    const ctx = await anonymous.newContext({ baseURL: apiURL });
    const res = await ctx.post('/auth/register', {
      data: { name: 'Duplicate', email: DEMO_OWNER.email, password: 'E2E-password-123' },
    });
    expect(res.status()).toBe(409);
    await ctx.dispose();
  });

  test('/auth/me with valid token returns user', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const res = await api.get('/auth/me');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.email).toBe(DEMO_OWNER.email);
    expect(body.name).toBeTruthy();
    await api.dispose();
  });
});
