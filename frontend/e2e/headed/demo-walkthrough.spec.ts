import { test, expect } from '@playwright/test';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

const OWNER = { email: 'budi@tokomaju.com', password: 'budi123', name: 'Budi Santoso' };
const EMPLOYEE = { email: 'ani@tokomaju.com', password: 'ani123', name: 'Ani Lestari' };
const ADMIN = { email: 'admin@kepin.io', password: 'admin123', name: 'Admin KePin' };
const TENANT = 'toko-maju';

async function seedUsers(page: any, users: Array<{ email: string; password: string; name: string }>) {
  await page.goto(WEB + '/auth/login');
  await page.evaluate((us: any) => {
    const stored = us.map((u: any, i: number) => ({
      id: `e2e-${i}-${Date.now()}`,
      name: u.name,
      email: u.email,
      phone: '',
      password: u.password,
    }));
    localStorage.setItem('kepin_users', JSON.stringify(stored));
    localStorage.removeItem('kepin_session');
  }, users);
}

async function loginAs(page: any, email: string, password: string) {
  await page.goto(WEB + '/auth/login');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  await page.locator('#email').fill(email);
  await page.locator('#password').fill(password);
  await page.locator('button[type="submit"]').click();
  await page.waitForTimeout(1500);
}

test.describe('Demo Walkthrough - Headed Mode', () => {
  test('OWNER: login and explore all features', async ({ page }) => {
    test.setTimeout(180_000);

    // --- Seed users then login as owner ---
    await seedUsers(page, [OWNER, EMPLOYEE, ADMIN]);
    await loginAs(page, OWNER.email, OWNER.password);

    // Should redirect to /app/toko-maju
    await expect(page).toHaveURL(/\/app\/toko-maju/);
    await page.waitForTimeout(1000);

    // 1. Dashboard
    await page.goto(WEB + `/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);

    // 2. Sales > Customers
    await page.goto(WEB + `/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    // Click "Pelanggan Baru" button
    const createCustBtn = page.locator('button').filter({ hasText: /pelanggan baru/i });
    if (await createCustBtn.isVisible()) {
      await createCustBtn.click();
      await page.waitForTimeout(800);
      // Close modal by pressing Escape
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }

    // 3. Sales > Invoices
    await page.goto(WEB + `/app/${TENANT}/sales/invoices`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 4. Purchasing > Orders
    await page.goto(WEB + `/app/${TENANT}/purchasing/orders`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 5. Purchasing > Suppliers
    await page.goto(WEB + `/app/${TENANT}/purchasing/suppliers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 6. Inventory > Products
    await page.goto(WEB + `/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 7. Inventory > Movements
    await page.goto(WEB + `/app/${TENANT}/inventory/movements`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 8. Transactions
    await page.goto(WEB + `/app/${TENANT}/transactions`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 9. Accounting
    await page.goto(WEB + `/app/${TENANT}/accounting/chart-of-accounts`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    // Try clicking create button
    const createAcctBtn = page.locator('button').filter({ hasText: /buat|create|tambah|akun baru/i });
    if (await createAcctBtn.isVisible()) {
      await createAcctBtn.click();
      await page.waitForTimeout(800);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }

    await page.goto(WEB + `/app/${TENANT}/accounting/journals`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/accounting/reconciliation`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 10. Reports
    await page.goto(WEB + `/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/reports/investor`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 11. Insights
    await page.goto(WEB + `/app/${TENANT}/insights`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 12. Notifications
    await page.goto(WEB + `/app/${TENANT}/notifications`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 13. Audit
    await page.goto(WEB + `/app/${TENANT}/audit`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // 14. Settings
    await page.goto(WEB + `/app/${TENANT}/settings/organization`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    // Click edit profile
    const editBtn = page.locator('button').filter({ hasText: /edit profil/i });
    if (await editBtn.isVisible()) {
      await editBtn.click();
      await page.waitForTimeout(800);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }

    await page.goto(WEB + `/app/${TENANT}/settings/branches`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/settings/members`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const inviteBtn = page.locator('button').filter({ hasText: /undang anggota/i });
    if (await inviteBtn.isVisible()) {
      await inviteBtn.click();
      await page.waitForTimeout(800);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }

    await page.goto(WEB + `/app/${TENANT}/settings/roles`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/settings/sidebar`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/settings/billing`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/settings/integrations`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Final assertion - no crash
    await expect(page.locator('body')).toBeVisible();
  });

  test('EMPLOYEE: login and explore accessible features', async ({ page }) => {
    test.setTimeout(120_000);

    // Seed users then login as employee
    await seedUsers(page, [OWNER, EMPLOYEE, ADMIN]);
    await loginAs(page, EMPLOYEE.email, EMPLOYEE.password);

    await expect(page).toHaveURL(/\/app\/toko-maju/);
    await page.waitForTimeout(1000);

    // Visit all pages accessible to employee
    await page.goto(WEB + `/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/inventory/movements`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/sales/invoices`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/purchasing/orders`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/purchasing/suppliers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/notifications`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + `/app/${TENANT}/audit`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await expect(page.locator('body')).toBeVisible();
  });

  test('ADMIN: login and explore admin features', async ({ page }) => {
    test.setTimeout(120_000);

    // Seed users then login as admin
    await seedUsers(page, [OWNER, EMPLOYEE, ADMIN]);
    await loginAs(page, ADMIN.email, ADMIN.password);

    // Admin should redirect to /admin
    await page.waitForTimeout(1000);

    // Visit all admin pages
    await page.goto(WEB + '/admin');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);

    await page.goto(WEB + '/admin/tenants');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + '/admin/users');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + '/admin/subscriptions');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + '/admin/notifications');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + '/admin/security');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + '/admin/incidents');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await page.goto(WEB + '/admin/audit');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    await expect(page.locator('body')).toBeVisible();
  });
});
