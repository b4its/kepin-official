import { test as setup, expect, request } from '@playwright/test';
import { uniqueEmail } from '../helpers/ids';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const authFile = resolve(__dirname, '../.auth/no-org.json');
const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1/';
const webURL = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

setup('setup no-org storage state', async ({ page }) => {
  const email = uniqueEmail();
  const password = 'test123';

  const anonymous = await request.newContext({ baseURL: apiURL });
  const regRes = await anonymous.post('auth/register', {
    data: { email, password, name: 'No Org User' },
  });
  expect(regRes.status()).toBe(201);
  await anonymous.dispose();

  const ctx = await request.newContext({ baseURL: apiURL });
  const loginRes = await ctx.post('auth/login', { data: { email, password } });
  const loginBody = await loginRes.json();
  expect(loginRes.status()).toBe(200);
  await ctx.dispose();

  await page.goto(webURL + '/auth/login');
  await page.evaluate((data) => {
    localStorage.setItem('kepin_token', data.access_token);
    const user = { id: data.user.id, name: data.user.name, email: data.user.email, phone: data.user.phone || '', avatar: data.user.avatarUrl };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    const tenants = (data.tenants || []).map((t: any) => ({ slug: t.slug, role: t.role }));
    localStorage.setItem('kepin_tenants', JSON.stringify(tenants));
  }, loginBody);

  await page.goto(webURL + '/app');
  await page.waitForTimeout(2000);
  await page.context().storageState({ path: authFile });
});
