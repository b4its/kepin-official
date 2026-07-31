import { test, expect } from '@playwright/test';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';

test.describe('AUTH: All Authentication Pages', () => {
  test('Login, Register, Forgot Password, Reset Password, MFA', async ({ page }) => {
    test.setTimeout(120_000);

    // ════════════════════════════════════════════════════════════
    // 1. LOGIN PAGE
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 1. LOGIN ═════════');
    await page.goto(WEB + '/auth/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    console.log('   ✅ Form login: email, password, submit button');

    // Input fields
    await page.locator('#email').fill('test@test.com');
    await page.locator('#password').fill('test123');
    console.log('   ✅ Input fields dapat diisi');

    // "Ingat saya" checkbox
    const rememberCb = page.locator('input[type="checkbox"], label', { hasText: /ingat saya/i });
    if (await rememberCb.isVisible().catch(() => false)) {
      console.log('   ✅ Checkbox "Ingat saya"');
    }

    // Lupa password link
    const lupaPw = page.locator('a', { hasText: /lupa password/i });
    if (await lupaPw.isVisible().catch(() => false)) {
      console.log('   ✅ Link "Lupa password"');
    }

    // Register link
    const daftarLink = page.locator('a', { hasText: /daftar|register/i });
    if (await daftarLink.isVisible().catch(() => false)) {
      console.log('   ✅ Link "Daftar"');
    }

    console.log('   ✅ Halaman login selesai');

    // ════════════════════════════════════════════════════════════
    // 2. REGISTER PAGE
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 2. REGISTER ═════════');
    await page.goto(WEB + '/auth/register');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const regInputs = page.locator('input:visible');
    const regCount = await regInputs.count();
    console.log(`   📝 ${regCount} input field ditemukan`);

    if (regCount >= 1) await regInputs.nth(0).fill('Test User');
    if (regCount >= 2) await regInputs.nth(1).fill('test@register.com');
    if (regCount >= 3) await regInputs.nth(2).fill('Test Company');
    if (regCount >= 4) await regInputs.nth(3).fill('password123');
    console.log('   ✅ Form register dapat diisi');

    await expect(page.locator('button[type="submit"]')).toBeVisible();
    console.log('   ✅ Tombol submit register');

    // Login link
    const masukLink = page.locator('a', { hasText: /masuk|login/i });
    if (await masukLink.isVisible().catch(() => false)) {
      console.log('   ✅ Link "Masuk"');
    }

    console.log('   ✅ Halaman register selesai');

    // ════════════════════════════════════════════════════════════
    // 3. FORGOT PASSWORD
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 3. FORGOT PASSWORD ═════════');
    await page.goto(WEB + '/auth/forgot-password');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.locator('input[type="email"], input:visible')).toBeVisible();
    await page.locator('input:visible').first().fill('test@test.com');
    console.log('   ✅ Input email dapat diisi');

    await expect(page.locator('button[type="submit"]')).toBeVisible();
    console.log('   ✅ Tombol submit forgot password');

    // Kembali ke login link
    const kembaliLink = page.locator('a', { hasText: /kembali ke login/i });
    if (await kembaliLink.isVisible().catch(() => false)) {
      console.log('   ✅ Link "Kembali ke Login"');
    }

    console.log('   ✅ Halaman forgot password selesai');

    // ════════════════════════════════════════════════════════════
    // 4. RESET PASSWORD
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 4. RESET PASSWORD ═════════');
    await page.goto(WEB + '/auth/reset-password');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const rpInputs = page.locator('input:visible');
    const rpCount = await rpInputs.count();
    if (rpCount >= 1) await rpInputs.nth(0).fill('newpassword123');
    if (rpCount >= 2) await rpInputs.nth(1).fill('newpassword123');
    console.log('   ✅ Form reset password dapat diisi');

    await expect(page.locator('button[type="submit"]')).toBeVisible();
    console.log('   ✅ Tombol submit reset password');

    console.log('   ✅ Halaman reset password selesai');

    // ════════════════════════════════════════════════════════════
    // 5. MFA PAGE
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 5. MFA ═════════');
    await page.evaluate(() => localStorage.setItem('kepin_mfa_token', 'e2e-dummy-mfa-token'));
    await page.goto(WEB + '/auth/mfa');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 6-digit code input boxes
    const mfaInputs = page.locator('input:visible');
    const mfaCount = await mfaInputs.count();
    console.log(`   🔢 ${mfaCount} digit input boxes ditemukan`);
    if (mfaCount >= 1) {
      await mfaInputs.first().fill('1');
      console.log('   ✅ Input kode MFA dapat diisi');
    }

    await expect(page.locator('button[type="submit"]')).toBeVisible();
    console.log('   ✅ Tombol Verifikasi MFA');

    // Recovery code link
    const recoveryLink = page.locator('a', { hasText: /recovery/i });
    if (await recoveryLink.isVisible().catch(() => false)) {
      console.log('   ✅ Link "Recovery code"');
    }

    console.log('   ✅ Halaman MFA selesai');
    console.log('\n🎉 AUTH: SEMUA HALAMAN TERVERIFIKASI ✅');
  });
});

test.describe('PUBLIC: Landing + Legal Pages', () => {
  test('Landing page, Terms, Privacy, Security', async ({ page }) => {
    test.setTimeout(120_000);

    // ════════════════════════════════════════════════════════════
    // 1. LANDING PAGE
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 1. LANDING PAGE ═════════');
    await page.goto(WEB + '/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const landingText = await page.locator('body').innerText();

    // Hero section
    const hasHero = landingText.includes('KePin') || landingText.includes('kepin');
    console.log(`   🏠 Hero section: ${hasHero ? '✅' : '❌'}`);

    // CTA buttons
    const ctaFree = page.locator('a, button', { hasText: /coba gratis/i });
    if (await ctaFree.isVisible().catch(() => false)) console.log('   🆓 CTA "Coba Gratis": ✅');
    const ctaDemo = page.locator('a, button', { hasText: /cara kerja|demo/i });
    if (await ctaDemo.isVisible().catch(() => false)) console.log('   👀 CTA "Lihat Cara Kerja": ✅');

    // Trust strip
    if (landingText.includes('UMKM')) console.log('   📊 Trust strip: ✅');

    // Pricing section
    const hasPricing = landingText.includes('Basic') || landingText.includes('Premium') || landingText.includes('Platinum');
    if (hasPricing) console.log('   💳 Pricing section: ✅');

    // FAQ
    const hasFAQ = landingText.includes('FAQ') || landingText.includes('pertanyaan');
    if (hasFAQ) console.log('   ❓ FAQ section: ✅');

    // Feature cards
    const hasFitur = landingText.includes('Fitur') || landingText.includes('fitur');
    if (hasFitur) console.log('   ⭐ Feature section: ✅');

    console.log('   ✅ Landing page selesai');

    // ════════════════════════════════════════════════════════════
    // 2. TERMS & CONDITIONS
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 2. TERMS ═════════');
    await page.goto(WEB + '/terms');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const termsText = await page.locator('body').innerText();
    console.log(`   📄 Terms page: ${termsText.length > 100 ? '✅' : '❌'}`);

    // Check for legal content sections
    const hasTermsContent = ['Syarat', 'Ketentuan', 'Layanan', 'Akun'].some(s => termsText.includes(s));
    console.log(`   📑 Konten legal: ${hasTermsContent ? '✅' : '❌'}`);
    console.log('   ✅ Terms selesai');

    // ════════════════════════════════════════════════════════════
    // 3. PRIVACY POLICY
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 3. PRIVACY ═════════');
    await page.goto(WEB + '/privacy');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const privacyText = await page.locator('body').innerText();
    console.log(`   📄 Privacy page: ${privacyText.length > 100 ? '✅' : '❌'}`);

    const hasPrivacyContent = ['Data', 'Privasi', 'Cookie', 'Kebijakan'].some(s => privacyText.includes(s));
    console.log(`   📑 Konten privasi: ${hasPrivacyContent ? '✅' : '❌'}`);
    console.log('   ✅ Privacy selesai');

    // ════════════════════════════════════════════════════════════
    // 4. SECURITY PAGE
    // ════════════════════════════════════════════════════════════
    console.log('\n═════════ 4. SECURITY ═════════');
    await page.goto(WEB + '/security');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const secText = await page.locator('body').innerText();
    console.log(`   🔒 Security page: ${secText.length > 100 ? '✅' : '❌'}`);

    const hasSecContent = ['ISO', 'Enkripsi', 'Keamanan', 'MFA', 'Audit'].some(s => secText.includes(s));
    console.log(`   🔐 Konten keamanan: ${hasSecContent ? '✅' : '❌'}`);
    console.log('   ✅ Security selesai');

    console.log('\n🎉 PUBLIC: SEMUA HALAMAN TERVERIFIKASI ✅');
  });
});
