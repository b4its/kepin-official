import { test as setup, expect, request } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
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

  const { api: authedApi } = await loginApi(apiURL, email, password);
  const res = await authedApi.get('auth/me');
  expect(res.ok()).toBeTruthy();

  await page.goto(webURL + '/auth/login');
  await page.evaluate(([e, p]) => {
    const user = { id: 'no-org-setup', name: 'No Org User', email: e, phone: '' };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    localStorage.setItem('kepin_users', JSON.stringify([{ ...user, password: p }]));
  }, [email, password] as [string, string]);
  await page.goto(webURL + '/app');
  await page.waitForTimeout(1000);
  await page.context().storageState({ path: authFile });
  await authedApi.dispose();
});
