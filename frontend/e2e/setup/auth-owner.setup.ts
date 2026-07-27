import { test as setup } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER } from '../helpers/ids';
import * as path from 'path';

const authFile = path.resolve(__dirname, '../.auth/tenant-owner.json');
const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const webURL = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

setup('setup tenant owner storage state', async ({ page }) => {
  const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
  const res = await api.get('/auth/me');
  const body = await res.json();
  console.log('Owner login OK:', body.email);

  await page.goto(webURL + '/auth/login');
  await page.evaluate(([email, pass]) => {
    const user = { id: 'owner-setup', name: 'Budi Santoso', email, phone: '' };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    localStorage.setItem('kepin_users', JSON.stringify([{ ...user, password: pass }]));
  }, [DEMO_OWNER.email, DEMO_OWNER.password] as [string, string]);
  await page.goto(webURL + '/app/toko-maju');
  await page.waitForTimeout(1000);
  await page.context().storageState({ path: authFile });
  await api.dispose();
});
