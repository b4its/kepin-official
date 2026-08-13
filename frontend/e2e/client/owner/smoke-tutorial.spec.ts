import { test, expect } from '@playwright/test';
import { DEMO_OWNER } from '../../helpers/ids';
import { loginApi } from '../../fixtures/api.fixture';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8001/api/v1';
const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';
const TENANT = DEMO_OWNER.tenant;

test.describe('Smoke: tutorial', () => {
  test('halaman tutorial & tur berjalan lintas halaman', async ({ page }) => {
    test.setTimeout(180000);
    page.on('console', (msg) => {
      if (msg.type() === 'log' || msg.type() === 'error') console.log('[BROWSER]', msg.text());
    });
    page.on('pageerror', (err) => console.log('[PAGEERROR]', err.message));

    // 1) Tur dapat dimulai dari tombol bantuan di halaman awal (landing);
    //    sorotan harus tepat pada elemen yang dijelaskan.
    await page.goto(`${WEB}/`);
    await page.waitForLoadState('networkidle');
    await expect(page.locator('header').getByRole('button', { name: /tutorial/i }).first()).toBeVisible();
    await page.locator('header').getByRole('button', { name: /tutorial/i }).first().click();
    const landingPop = page.locator('[class*="driver-popover"]').first();
    await expect(landingPop).toBeVisible({ timeout: 15000 });
    await expect(landingPop).toContainText(/Selamat Datang di KePin/i);
    await landingPop.getByRole('button', { name: /Lanjut/i }).click();
    await expect(landingPop).toContainText(/Navigasi Halaman Utama/i);
    await expect(page.locator('[data-tour="landing-header"].driver-active-element')).toBeVisible({ timeout: 5000 });
    // "Coba Gratis"/"Masuk" hanya ada saat belum login; bila sudah login
    // (storage state), langkah tampil sebagai popover tengah (tanpa elemen).
    await landingPop.getByRole('button', { name: /Lanjut/i }).click();
    await expect(landingPop).toContainText(/Mulai Coba Gratis/i);
    if (await page.locator('[data-tour="cta-register"]').count()) {
      await expect(page.locator('[data-tour="cta-register"].driver-active-element')).toBeVisible({ timeout: 5000 });
    }
    await landingPop.getByRole('button', { name: /Lanjut/i }).click();
    await expect(landingPop).toContainText(/Masuk ke Akun Anda/i);
    if (await page.locator('[data-tour="cta-login"]').count()) {
      await expect(page.locator('[data-tour="cta-login"].driver-active-element')).toBeVisible({ timeout: 5000 });
    }
    await landingPop.locator('[class*="driver-popover-close-btn"]').first().click();
    await expect(page.locator('[class*="driver-popover"]')).not.toBeVisible({ timeout: 5000 });

    // 2) Tombol bantuan ada di halaman login
    await page.goto(`${WEB}/auth/login`);
    await expect(page.locator('header').getByRole('button', { name: /tutorial/i }).first()).toBeVisible();

    // 3) Login via API
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    await api.dispose();

    // 4) Klik "?" di topbar workspace → halaman tutorial
    await page.goto(`${WEB}/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    await page.locator('header').getByRole('button', { name: /tutorial/i }).first().click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/tutorial$/);
    await expect(page.getByRole('button', { name: /Mulai Tur dari Awal/i }).first()).toBeVisible();
    await expect(page.locator('section', { hasText: 'Halaman Awal' })).toBeVisible();

    // 5) Mulai dari langkah "Dashboard" → popover muncul di dashboard
    const dashboardCard = page.locator('.card', { hasText: 'Dashboard — Pusat Kendali' }).first();
    await dashboardCard.getByRole('button', { name: /Mulai dari sini/i }).click();
    await expect(page).toHaveURL(/\/app\/toko-maju$/);
    const popover = page.locator('[class*="driver-popover"]').first();
    await expect(popover).toBeVisible({ timeout: 15000 });
    await expect(popover).toContainText(/Dashboard — Pusat Kendali/i);

    // 6) Lanjut beberapa langkah dalam satu halaman — sorotan driver.js
    //    harus tepat pada elemen yang dijelaskan (data-tour yang sesuai).
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover).toContainText(/Kartu Metrik Utama/i);
    await expect(page.locator('[data-tour="metric-cards"].driver-active-element')).toBeVisible({ timeout: 5000 });
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover).toContainText(/Grafik Arus Kas/i);
    await expect(page.locator('[data-tour="dashboard-charts"].driver-active-element')).toBeVisible({ timeout: 5000 });

    // 6b) Kembali → kembali ke langkah sebelumnya dalam halaman yang sama
    await popover.getByRole('button', { name: /Kembali/i }).click();
    await expect(popover).toContainText(/Kartu Metrik Utama/i);
    await expect(page.locator('[data-tour="metric-cards"].driver-active-element')).toBeVisible({ timeout: 5000 });
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover).toContainText(/Grafik Arus Kas/i);

    // 7) Lanjut → pindah halaman ke insights, popover muncul di halaman baru
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover).toContainText(/Sidebar Navigasi/i);
    await expect(page.locator('[data-tour="workspace-sidebar"].driver-active-element')).toBeVisible({ timeout: 5000 });
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(page).toHaveURL(/\/insights/, { timeout: 15000 });
    const popover2 = page.locator('[class*="driver-popover"]').first();
    await expect(popover2).toBeVisible({ timeout: 15000 });
    await expect(popover2).toContainText(/Analitik Bisnis/i);

    // 8) Tutup tur
    await popover2.locator('[class*="driver-popover-close-btn"]').first().click();
    await expect(page.locator('[class*="driver-popover"]')).not.toBeVisible({ timeout: 5000 });
  });

  test('tur penuh dari halaman awal hingga workspace', async ({ page }) => {
    test.setTimeout(240000);
    page.on('console', (msg) => {
      console.log('[BROWSER]', msg.type(), msg.text());
    });
    page.on('pageerror', (err) => console.log('[PAGEERROR]', err.message));

    // Buka halaman tutorial dari workspace
    await page.goto(`${WEB}/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    await page.locator('header').getByRole('button', { name: /tutorial/i }).first().click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: /Mulai Tur dari Awal/i }).first().click();

    // Berpindah ke halaman awal (landing)
    await expect(page).toHaveURL(`${WEB}/`, { timeout: 15000 });
    const pop = () => page.locator('[class*="driver-popover"]').first();

    const expectStep = async (text: RegExp) => {
      await expect(pop()).toBeVisible({ timeout: 15000 });
      await expect(pop()).toContainText(text);
    };
    // Sorotan driver.js harus tepat pada elemen yang dijelaskan.
    const expectHighlight = async (hook: string) => {
      await expect(page.locator(`[data-tour="${hook}"].driver-active-element`)).toBeVisible({ timeout: 5000 });
    };

    // Fase 1: Halaman Awal
    await expectStep(/Selamat Datang di KePin/i);
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Navigasi Halaman Utama/i);
    await expectHighlight('landing-header');
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Mulai Coba Gratis/i);
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Masuk ke Akun Anda/i);

    // Fase 2: Akun & Perusahaan
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15000 });
    await expectStep(/Halaman Masuk \(Login\)/i);
    await expectHighlight('auth-form');
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Verifikasi Dua Langkah/i);
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expect(page).toHaveURL(/\/auth\/register/, { timeout: 15000 });
    await expectStep(/Daftar Akun Gratis/i);
    await expectHighlight('auth-form');
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    // Onboarding me-redirect otomatis ke dashboard (sudah punya tenant) —
    // tur melewati langkah onboarding & Buat/Gabung Perusahaan, lalu
    // melanjutkan dari langkah Dashboard di halaman workspace.
    await expect(page).toHaveURL(/\/app\/toko-maju$/, { timeout: 20000 });
    await expectStep(/Dashboard — Pusat Kendali/i);

    // Fase 3: Dashboard hingga Insights
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Kartu Metrik Utama/i);
    await expectHighlight('metric-cards');
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Grafik Arus Kas/i);
    await expectHighlight('dashboard-charts');
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expectStep(/Sidebar Navigasi/i);
    await expectHighlight('workspace-sidebar');
    await pop().getByRole('button', { name: /Lanjut/i }).click();
    await expect(page).toHaveURL(/\/insights/, { timeout: 15000 });
    await expectStep(/Analitik Bisnis/i);

    // Tutup tur
    await pop().locator('[class*="driver-popover-close-btn"]').first().click();
    await expect(page.locator('[class*="driver-popover"]')).not.toBeVisible({ timeout: 5000 });
  });
});
