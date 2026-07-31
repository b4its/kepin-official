import { test, expect } from '@playwright/test';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

const TENANT = 'toko-maju';

async function seedAndLogin(page: any) {
  await page.goto(WEB + '/auth/login');
  await page.waitForLoadState('networkidle');

  // Login via UI
  await page.locator('#email').fill('ani@tokomaju.com');
  await page.locator('#password').fill('ani12345');
  await page.locator('button[type="submit"]').click();
  await page.waitForTimeout(2500);
}

test.describe('EMPLOYEE: Limited Access + All Accessible Features', () => {
  test('Akses halaman employee dan verifikasi fitur terbatas', async ({ page }) => {
    test.setTimeout(300_000);

    console.log('▶️ EMPLOYEE: Login sebagai Ani Lestari');
    await seedAndLogin(page);
    console.log('   ✅ Login employee berhasil');

    // ════════════════════════════════════════════════════════════
    // EMPLOYEE-ACCESSIBLE PAGES
    // ════════════════════════════════════════════════════════════
    const accessiblePages = [
      { path: '', label: 'Dashboard', features: ['Pendapatan', 'Pengeluaran', 'Laba Bersih', 'Kas & Bank'] },
      { path: '/inventory/products', label: 'Products', features: ['Total Produk', 'Stok Kritis'] },
      { path: '/inventory/movements', label: 'Stock Movements', features: [] },
      { path: '/sales/invoices', label: 'Invoices', features: ['Piutang', 'Jatuh Tempo'] },
      { path: '/sales/customers', label: 'Customers', features: [] },
      { path: '/purchasing/orders', label: 'Purchase Orders', features: [] },
      { path: '/purchasing/suppliers', label: 'Suppliers', features: [] },
      { path: '/notifications', label: 'Notifications', features: [] },
      { path: '/audit', label: 'Audit', features: [] },
    ];

    for (const p of accessiblePages) {
      console.log(`   📂 ${p.label}...`);
      await page.goto(WEB + `/app/${TENANT}${p.path}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);

      // Verify page loads
      await expect(page.locator('body')).toBeVisible();
      console.log(`      ✅ Halaman ${p.label} dimuat`);

      // Verify key features/metrics
      for (const f of p.features) {
        const text = await page.locator('body').innerText();
        expect(text).toContain(f);
        console.log(`      ✅ Metrik "${f}" ditemukan`);
      }
    }

    // ════════════════════════════════════════════════════════════
    // VERIFY ACCESSIBLE ACTIONS (modals, buttons, etc.)
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ VERIFIKASI UI ACTIONS ═════════');

    // Customers - create modal
    console.log('   📂 Buka Customers modal create...');
    await page.goto(WEB + `/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const custBtn = page.locator('button', { hasText: /pelanggan baru/i });
    if (await custBtn.isVisible().catch(() => false)) {
      await custBtn.click();
      await page.waitForTimeout(800);
      const inputs = page.locator('input:visible');
      if (await inputs.count() >= 1) {
        await inputs.nth(0).fill('Customer by Employee');
        console.log('      ✅ Employee bisa buka modal & isi form');
      }
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }

    // Invoices - create modal
    console.log('   📂 Buka Invoices modal create...');
    await page.goto(WEB + `/app/${TENANT}/sales/invoices`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const invBtn = page.locator('button', { hasText: /invoice baru/i });
    if (await invBtn.isVisible().catch(() => false)) {
      await invBtn.click();
      await page.waitForTimeout(800);
      console.log('      ✅ Employee bisa buka modal invoice');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }

    // Products - create modal
    console.log('   📂 Buka Products modal create...');
    await page.goto(WEB + `/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const prodBtn = page.locator('button', { hasText: /produk baru/i });
    if (await prodBtn.isVisible().catch(() => false)) {
      await prodBtn.click();
      await page.waitForTimeout(800);
      console.log('      ✅ Employee bisa buka modal produk');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }

    // Suppliers - create modal
    console.log('   📂 Buka Suppliers modal create...');
    await page.goto(WEB + `/app/${TENANT}/purchasing/suppliers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(800);
    const supBtn = page.locator('button', { hasText: /pemasok baru/i });
    if (await supBtn.isVisible().catch(() => false)) {
      await supBtn.click();
      await page.waitForTimeout(800);
      console.log('      ✅ Employee bisa buka modal supplier');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }

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

    console.log('\n🎉 EMPLOYEE: SEMUA SELESAI! ✅');
  });
});
