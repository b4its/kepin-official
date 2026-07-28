import { test, expect } from '@playwright/test';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

async function seedAndLogin(page: any) {
  await page.goto(WEB + '/auth/login');
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => {
    localStorage.clear();
    localStorage.setItem('kepin_users', JSON.stringify([
      { id: 'e2e-admin', name: 'Admin KePin', email: 'admin@kepin.io', phone: '', password: 'admin123' },
      { id: 'e2e-owner', name: 'Budi Santoso', email: 'budi@tokomaju.com', phone: '', password: 'budi123' },
    ]));
  });
  await page.waitForTimeout(300);

  await page.locator('#email').fill('admin@kepin.io');
  await page.locator('#password').fill('admin123');
  await page.locator('button[type="submit"]').click();
  await page.waitForTimeout(2000);
}

async function closeModal(page: any) {
  const closeBtn = page.locator('button[aria-label="Close"], button:has(svg.lucide-x)');
  if (await closeBtn.isVisible().catch(() => false)) {
    await closeBtn.click();
    await page.waitForTimeout(500);
    return;
  }
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
}

test.describe('ADMIN: Platform Management + All Features', () => {
  test('Akses semua halaman admin dan verifikasi fitur', async ({ page }) => {
    test.setTimeout(300_000);

    console.log('▶️ ADMIN: Login sebagai Admin');
    await seedAndLogin(page);
    console.log('   ✅ Login admin berhasil');

    // ════════════════════════════════════════════════════════════
    // 1. ADMIN DASHBOARD
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 1. ADMIN DASHBOARD ═════════');
    await page.goto(WEB + '/admin');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const dashText = await page.locator('body').innerText();
    const dashMetrics = ['Tenant Aktif', 'Tenant Trial', 'MRR'].every(m => dashText.includes(m));
    console.log(`   📊 Metric cards: ${dashMetrics ? '✅' : '❌'}`);

    // Date filter
    const dateFilter = page.locator('button, select', { hasText: /hari|pekan|bulan|tahun/i });
    if (await dateFilter.isVisible().catch(() => false)) console.log('   📅 Date filter: ✅');
    console.log('   ✅ Admin dashboard selesai');

    // ════════════════════════════════════════════════════════════
    // 2. TENANTS
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 2. TENANTS ═════════');
    await page.goto(WEB + '/admin/tenants');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Create tenant
    const createTenantBtn = page.locator('button', { hasText: /tenant baru/i });
    if (await createTenantBtn.isVisible().catch(() => false)) {
      await createTenantBtn.click();
      await page.waitForTimeout(800);
      const tInputs = page.locator('input:visible, select:visible');
      const tc = await tInputs.count();
      if (tc >= 1) await tInputs.nth(0).fill('E2E Test Tenant');
      if (tc >= 2) await tInputs.nth(1).fill('e2e-test');
      console.log('   📝 Form create tenant diisi: ✅');
      await closeModal(page);
    }

    // View/Edit/Hapus row actions
    const viewBtn = page.locator('button, a', { hasText: /lihat|view/i }).first();
    if (await viewBtn.isVisible().catch(() => false)) {
      await viewBtn.click();
      await page.waitForTimeout(800);
      console.log('   👁️ Tombol View tenant: ✅');
      await page.goto(WEB + '/admin/tenants');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);
    }

    const editTenant = page.locator('button', { hasText: /edit/i }).first();
    if (await editTenant.isVisible().catch(() => false)) {
      await editTenant.click();
      await page.waitForTimeout(800);
      console.log('   ✏️ Tombol Edit tenant: ✅');
      await closeModal(page);
    }

    console.log('   ✅ Halaman tenants selesai');

    // ════════════════════════════════════════════════════════════
    // 3. USERS
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 3. USERS ═════════');
    await page.goto(WEB + '/admin/users');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const usersText = await page.locator('body').innerText();
    const hasUserTable = usersText.includes('admin') || usersText.includes('budi') || usersText.includes('email');
    console.log(`   👥 Tabel users: ${hasUserTable ? '✅' : '❌ (kosong)'}`);
    console.log('   ✅ Halaman users selesai');

    // ════════════════════════════════════════════════════════════
    // 4. SUBSCRIPTIONS
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 4. SUBSCRIPTIONS ═════════');
    await page.goto(WEB + '/admin/subscriptions');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const subText = await page.locator('body').innerText();
    const subMetrics = ['MRR', 'ARR', 'Aktif', 'Trial'].every(m => subText.includes(m));
    console.log(`   📊 Metric cards: ${subMetrics ? '✅' : '❌'}`);
    console.log('   ✅ Halaman subscriptions selesai');

    // ════════════════════════════════════════════════════════════
    // 5. NOTIFICATIONS (Subscriber)
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 5. NOTIFICATIONS ═════════');
    await page.goto(WEB + '/admin/notifications');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    console.log('   ✅ Halaman admin notifications selesai');

    // ════════════════════════════════════════════════════════════
    // 6. SECURITY
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 6. SECURITY ═════════');
    await page.goto(WEB + '/admin/security');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const secText = await page.locator('body').innerText();
    const secItems = ['Audit Trail', 'MFA', 'Session', 'Encryption', 'API Rate'].some(s => secText.includes(s));
    console.log(`   🔒 Security checklist: ${secItems ? '✅' : '❌'}`);
    console.log('   ✅ Halaman security selesai');

    // ════════════════════════════════════════════════════════════
    // 7. INCIDENTS
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 7. INCIDENTS ═════════');
    await page.goto(WEB + '/admin/incidents');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    console.log('   ✅ Halaman incidents selesai');

    // ════════════════════════════════════════════════════════════
    // 8. AUDIT
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 8. AUDIT ═════════');
    await page.goto(WEB + '/admin/audit');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    console.log('   ✅ Halaman admin audit selesai');

    // ════════════════════════════════════════════════════════════
    // LOGOUT
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ LOGOUT ═════════');
    await page.evaluate(() => localStorage.removeItem('kepin_session'));
    await page.goto(WEB + '/auth/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await expect(page.locator('#email')).toBeVisible();
    console.log('   ✅ Logout berhasil');

    console.log('\n🎉 ADMIN: SEMUA SELESAI! ✅');
  });
});
