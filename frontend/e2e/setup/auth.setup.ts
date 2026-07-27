import { type Page, test as setup } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_ADMIN } from '../helpers/ids';
import * as fs from 'fs';
import * as path from 'path';

const authFile = path.resolve(__dirname, '../.auth/admin.json');
const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const webURL = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

setup('setup admin storage state', async ({ page }) => {
  const { api } = await loginApi(apiURL, DEMO_ADMIN.email, DEMO_ADMIN.password);
  const res = await api.get('/auth/me');
  const body = await res.json();
  console.log('Admin login OK:', body.email);

  await page.goto(webURL + '/auth/login');
  await page.evaluate(([email, pass]) => {
    const user = { id: 'admin-setup', name: 'Admin KePin', email, phone: '' };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    localStorage.setItem('kepin_users', JSON.stringify([{ ...user, password: pass }]));
  }, [DEMO_ADMIN.email, DEMO_ADMIN.password] as [string, string]);
  await page.goto(webURL + '/admin');
  await page.waitForTimeout(1000);
  await page.context().storageState({ path: authFile });
  await api.dispose();
});
