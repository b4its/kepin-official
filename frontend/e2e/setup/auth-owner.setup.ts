import { test as setup, request } from '@playwright/test';
import { DEMO_OWNER } from '../helpers/ids';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const authFile = resolve(__dirname, '../.auth/tenant-owner.json');
const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1/';
const webURL = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

setup('setup tenant owner storage state', async ({ page }) => {
  const ctx = await request.newContext({ baseURL: apiURL });
  const loginRes = await ctx.post('auth/login', { data: { email: DEMO_OWNER.email, password: DEMO_OWNER.password } });
  const loginBody = await loginRes.json();
  console.log('Owner login OK:', loginBody.user.email);
  await ctx.dispose();

  await page.goto(webURL + '/auth/login');
  await page.waitForLoadState('networkidle');
  await page.evaluate((data) => {
    localStorage.setItem('kepin_token', data.access_token);
    const user = { id: data.user.id, name: data.user.name, email: data.user.email, phone: data.user.phone || '', avatar: data.user.avatarUrl };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    const tenants = (data.tenants || []).map((t: any) => ({ slug: t.slug, role: t.role, id: t.id, joinCode: t.joinCode }));
    localStorage.setItem('kepin_tenants', JSON.stringify(tenants));
  }, loginBody);

  await page.goto(webURL + '/app/toko-maju');
  await page.waitForTimeout(2000);
  await page.context().storageState({ path: authFile });
});
