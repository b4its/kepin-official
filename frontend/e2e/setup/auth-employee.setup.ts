import { test as setup } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_EMPLOYEE } from '../helpers/ids';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const authFile = resolve(__dirname, '../.auth/tenant-employee.json');
const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1/';
const webURL = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

setup('setup tenant employee storage state', async ({ page }) => {
  const { api } = await loginApi(apiURL, DEMO_EMPLOYEE.email, DEMO_EMPLOYEE.password);
  const res = await api.get('auth/me');
  const body = await res.json();
  console.log('Employee login OK:', body.email);

  await page.goto(webURL + '/auth/login');
  await page.evaluate(([email, pass]) => {
    const user = { id: 'employee-setup', name: 'Ani Lestari', email, phone: '' };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    localStorage.setItem('kepin_users', JSON.stringify([{ ...user, password: pass }]));
  }, [DEMO_EMPLOYEE.email, DEMO_EMPLOYEE.password] as [string, string]);
  await page.goto(webURL + '/app/toko-maju');
  await page.waitForTimeout(1000);
  await page.context().storageState({ path: authFile });
  await api.dispose();
});
