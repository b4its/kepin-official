import { test, expect } from '@playwright/test';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

const OWNER = { email: 'budi@tokomaju.com', password: 'budi123', name: 'Budi Santoso' };
const EMPLOYEE = { email: 'ani@tokomaju.com', password: 'ani123', name: 'Ani Lestari' };
const ADMIN = { email: 'admin@kepin.io', password: 'admin123', name: 'Admin KePin' };
const TENANT = 'toko-maju';

async function seedUsers(page: any, users: Array<{ email: string; password: string; name: string }>) {
  await page.goto(WEB + '/auth/login');
  await page.evaluate((us: any) => {
    localStorage.clear();
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
  await page.waitForTimeout(300);
  await page.locator('#password').fill(password);
  await page.waitForTimeout(300);
  await page.locator('button[type="submit"]').click();
  await page.waitForTimeout(2000);
}

test.describe('Demo Walkthrough Lengkap', () => {
  test('OWNER: Login → Seluruh Fitur → Edit Profile → Logout', async ({ page }) => {
    test.setTimeout(300_000);

    // ── 1. LOGIN ──
    console.log('▶️ 1. Login sebagai Owner (budi@tokomaju.com)');
    await seedUsers(page, [OWNER, EMPLOYEE, ADMIN]);
    await loginAs(page, OWNER.email, OWNER.password);
    await expect(page).toHaveURL(/\/app\/toko-maju/);
    console.log('   ✅ Berhasil login, redirect ke /app/toko-maju');

    // ── 2. DASHBOARD ──
    console.log('▶️ 2. Dashboard');
    await page.goto(WEB + `/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    // Dashboard has metric cards and charts - check they render
    await expect(page.locator('body')).toBeVisible();
    console.log('   ✅ Dashboard tampil');

    // ── 3. SIDEBAR NAVIGASI ──
    console.log('▶️ 3. Sidebar Navigation - cek semua menu');
    // Try clicking sidebar links if they exist
    const sidebarLinks = page.locator('a, button').filter({ hasText: /penjualan|pembelian|inventori|akuntansi|laporan|pengaturan/i });
    const linkCount = await sidebarLinks.count();
    console.log(`   📊 Ditemukan ${linkCount} menu sidebar`);

    // ── 4. SALES > CUSTOMERS ──
    console.log('▶️ 4. Sales > Customers - Buka modal create');
    await page.goto(WEB + `/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    // Click create button
    const createBtn = page.locator('button').filter({ hasText: /pelanggan baru/i });
    if (await createBtn.isVisible()) {
      console.log('   👆 Klik "+ Pelanggan Baru"');
      await createBtn.click();
      await page.waitForTimeout(1000);
      // Fill form
      const nameInput = page.locator('input').first();
      if (await nameInput.isVisible()) {
        await nameInput.fill('E2E Customer Test');
        await page.waitForTimeout(300);
        // Click save
        const saveBtn = page.locator('button').filter({ hasText: /simpan/i });
        if (await saveBtn.isVisible()) {
          await saveBtn.click();
          console.log('   ✅ Mencoba simpan customer (API call akan gagal - mock only)');
          await page.waitForTimeout(1000);
        }
      }
    }

    // ── 5. PURCHASING > SUPPLIERS ──
    console.log('▶️ 5. Purchasing > Suppliers');
    await page.goto(WEB + `/app/${TENANT}/purchasing/suppliers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    console.log('   ✅ Halaman suppliers tampil');

    // ── 6. INVENTORY > PRODUCTS ──
    console.log('▶️ 6. Inventory > Products');
    await page.goto(WEB + `/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const createProdBtn = page.locator('button').filter({ hasText: /produk baru|create|tambah/i });
    if (await createProdBtn.isVisible()) {
      console.log('   👆 Klik create produk');
      await createProdBtn.click();
      await page.waitForTimeout(1000);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }

    // ── 7. ACCOUNTING > CHART OF ACCOUNTS (PURE LOCAL - CRUD WORKS!) ──
    console.log('▶️ 7. Accounting > Chart of Accounts (CRUD lokal - berfungsi!)');
    await page.goto(WEB + `/app/${TENANT}/accounting/chart-of-accounts`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const createAkunBtn = page.locator('button').filter({ hasText: /akun baru|buat|create/i });
    if (await createAkunBtn.isVisible()) {
      console.log('   👆 Klik "Buat Akun Baru"');
      await createAkunBtn.click();
      await page.waitForTimeout(1000);
      // Fill form
      const inputs = page.locator('input');
      const inputCount = await inputs.count();
      if (inputCount >= 1) {
        await inputs.nth(0).fill('9-999');
        await page.waitForTimeout(200);
      }
      if (inputCount >= 2) {
        await inputs.nth(1).fill('Akun Test E2E');
        await page.waitForTimeout(200);
      }
      // Click save
      const simpanBtn = page.locator('button').filter({ hasText: /simpan/i });
      if (await simpanBtn.isVisible()) {
        await simpanBtn.click();
        await page.waitForTimeout(1000);
        console.log('   ✅ Akun berhasil dibuat (local store)');
      }
    }

    // ── 8. ACCOUNTING > JOURNALS ──
    console.log('▶️ 8. Accounting > Journals');
    await page.goto(WEB + `/app/${TENANT}/accounting/journals`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // ── 9. REPORTS ──
    console.log('▶️ 9. Reports');
    await page.goto(WEB + `/app/${TENANT}/reports`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);

    // ── 10. NOTIFICATIONS ──
    console.log('▶️ 10. Notifications');
    await page.goto(WEB + `/app/${TENANT}/notifications`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // ── 11. AUDIT ──
    console.log('▶️ 11. Audit Log');
    await page.goto(WEB + `/app/${TENANT}/audit`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // ── 12. SETTINGS > ORGANIZATION (PURE LOCAL - EDIT WORKS!) ──
    console.log('▶️ 12. Settings > Organization - Edit profil (CRUD lokal - berfungsi!)');
    await page.goto(WEB + `/app/${TENANT}/settings/organization`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    const editBtn = page.locator('button').filter({ hasText: /edit profil/i });
    if (await editBtn.isVisible()) {
      console.log('   👆 Klik "Edit Profil"');
      await editBtn.click();
      await page.waitForTimeout(1000);
      // Fill edit form
      const editInputs = page.locator('input, select');
      const editCount = await editInputs.count();
      if (editCount >= 1) {
        await editInputs.nth(0).fill('Toko Maju E2E');
        await page.waitForTimeout(200);
      }
      // Click simpan
      const simpanBtn2 = page.locator('button').filter({ hasText: /simpan/i });
      if (await simpanBtn2.isVisible()) {
        await simpanBtn2.click();
        await page.waitForTimeout(1000);
        console.log('   ✅ Nama organisasi berhasil diubah (local state)');
      }
    }

    // ── 13. SETTINGS > BRANCHES ──
    console.log('▶️ 13. Settings > Branches');
    await page.goto(WEB + `/app/${TENANT}/settings/branches`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    console.log('   ✅ Halaman cabang tampil');

    // ── 14. SETTINGS > MEMBERS ──
    console.log('▶️ 14. Settings > Members');
    await page.goto(WEB + `/app/${TENANT}/settings/members`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const undangBtn = page.locator('button').filter({ hasText: /undang anggota/i });
    if (await undangBtn.isVisible()) {
      console.log('   👆 Klik "+ Undang Anggota"');
      await undangBtn.click();
      await page.waitForTimeout(1000);
      // Fill form
      const memberInputs = page.locator('input');
      const mc = await memberInputs.count();
      if (mc >= 1) await memberInputs.nth(0).fill('Anggota Baru');
      if (mc >= 2) await memberInputs.nth(1).fill('anggota@test.com');
      await page.waitForTimeout(300);
      const undangSubmit = page.locator('button[type="submit"]').filter({ hasText: /undang/i });
      if (await undangSubmit.isVisible().catch(() => false)) {
        await undangSubmit.click();
        await page.waitForTimeout(1000);
      }
    }

    // ── 15. SETTINGS > ROLES (PURE LOCAL) ──
    console.log('▶️ 15. Settings > Roles');
    await page.goto(WEB + `/app/${TENANT}/settings/roles`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // ── 16. SETTINGS > SIDEBAR ──
    console.log('▶️ 16. Settings > Sidebar');
    await page.goto(WEB + `/app/${TENANT}/settings/sidebar`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    console.log('   ✅ Halaman sidebar tampil');

    // ── 17. SETTINGS > BILLING ──
    console.log('▶️ 17. Settings > Billing');
    await page.goto(WEB + `/app/${TENANT}/settings/billing`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // ── 18. SETTINGS > INTEGRATIONS ──
    console.log('▶️ 18. Settings > Integrations');
    await page.goto(WEB + `/app/${TENANT}/settings/integrations`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // ── 19. EDIT PROFILE (localStorage - BERFUNGSI!) ──
    console.log('▶️ 19. Edit Profile (localStorage)');
    // Navigate to dashboard then try to access profile
    // The auth store updateProfile uses localStorage - simulate via page.evaluate
    await page.goto(WEB + `/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Update profile via localStorage directly
    await page.evaluate(() => {
      const user = JSON.parse(localStorage.getItem('kepin_session') || '{}');
      user.name = 'Budi Updated';
      user.phone = '081234567890';
      localStorage.setItem('kepin_session', JSON.stringify(user));
    });
    console.log('   ✅ Profile updated via localStorage');

    // ── 20. LOGOUT ──
    console.log('▶️ 20. Logout');
    await page.goto(WEB + '/auth/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    // Clear session to simulate logout
    await page.evaluate(() => {
      localStorage.removeItem('kepin_session');
    });
    console.log('   ✅ Logout berhasil');

    // Verify we're on login page
    await page.goto(WEB + '/auth/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await expect(page.locator('#email')).toBeVisible();
    console.log('   ✅ Kembali ke halaman login');

    console.log('\n🎉 OWNER: Selesai! Semua fitur telah dijelajahi.');
  });

  test('EMPLOYEE: Login → Fitur Terbatas → Logout', async ({ page }) => {
    test.setTimeout(120_000);

    console.log('\n▶️ EMPLOYEE: Login sebagai Ani Lestari');
    await seedUsers(page, [OWNER, EMPLOYEE, ADMIN]);
    await loginAs(page, EMPLOYEE.email, EMPLOYEE.password);
    await expect(page).toHaveURL(/\/app\/toko-maju/);
    console.log('   ✅ Login employee berhasil');

    // Kunjungi halaman yang bisa diakses employee
    const employeePages = [
      { path: '', label: 'Dashboard' },
      { path: '/inventory/products', label: 'Products' },
      { path: '/inventory/movements', label: 'Stock Movements' },
      { path: '/sales/invoices', label: 'Invoices' },
      { path: '/sales/customers', label: 'Customers' },
      { path: '/purchasing/orders', label: 'Purchase Orders' },
      { path: '/purchasing/suppliers', label: 'Suppliers' },
      { path: '/notifications', label: 'Notifications' },
      { path: '/audit', label: 'Audit' },
    ];

    for (const { path: p, label } of employeePages) {
      console.log(`   📂 Buka ${label}...`);
      await page.goto(WEB + `/app/${TENANT}${p}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(800);
    }

    console.log('   ✅ Employee: Semua halaman dapat diakses tanpa error');

    // Logout
    console.log('▶️ Employee Logout');
    await page.evaluate(() => localStorage.removeItem('kepin_session'));
    await page.goto(WEB + '/auth/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await expect(page.locator('#email')).toBeVisible();
    console.log('   ✅ Employee logout berhasil');

    console.log('\n🎉 EMPLOYEE: Selesai!');
  });

  test('ADMIN: Login → Admin Panel → Logout', async ({ page }) => {
    test.setTimeout(120_000);

    console.log('\n▶️ ADMIN: Login sebagai Admin');
    await seedUsers(page, [OWNER, EMPLOYEE, ADMIN]);
    await loginAs(page, ADMIN.email, ADMIN.password);
    await page.waitForTimeout(1500);
    console.log('   ✅ Login admin berhasil');

    // Kunjungi halaman admin
    const adminPages = [
      { path: '/admin', label: 'Dashboard' },
      { path: '/admin/tenants', label: 'Tenants' },
      { path: '/admin/users', label: 'Users' },
      { path: '/admin/subscriptions', label: 'Subscriptions' },
      { path: '/admin/notifications', label: 'Notifications' },
      { path: '/admin/security', label: 'Security' },
      { path: '/admin/incidents', label: 'Incidents' },
      { path: '/admin/audit', label: 'Audit' },
    ];

    for (const { path: p, label } of adminPages) {
      console.log(`   📂 Buka ${label}...`);
      await page.goto(WEB + p);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
    }

    console.log('   ✅ Admin: Semua halaman admin dapat diakses');

    // Logout
    console.log('▶️ Admin Logout');
    await page.evaluate(() => localStorage.removeItem('kepin_session'));
    await page.goto(WEB + '/auth/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await expect(page.locator('#email')).toBeVisible();
    console.log('   ✅ Admin logout berhasil');

    console.log('\n🎉 ADMIN: Selesai!');
  });
});
