import { test, expect } from '@playwright/test';
import { DEMO_OWNER } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8001/api/v1';
const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';
const TENANT = DEMO_OWNER.tenant;

test.describe('Kode Bergabung', () => {
  test('owner melihat kode bergabung & dapat membagikannya; kode valid di join-info', async ({ page }) => {
    // 0) Sidebar menampilkan menu "Anggota Tim" untuk owner
    await page.goto(`${WEB}/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    const sidebar = page.locator('[data-tour="workspace-sidebar"]');
    await expect(sidebar.getByRole('button', { name: /Anggota Tim/i }).first()).toBeVisible({ timeout: 10000 });

    // 1) Buka halaman anggota tim sebagai owner
    await sidebar.getByRole('button', { name: /Anggota Tim/i }).first().click();
    await expect(page).toHaveURL(/\/settings\/members$/, { timeout: 15000 });
    await page.waitForLoadState('networkidle');

    // 2) Kartu "Kode Bergabung" tampil untuk owner dengan kode non-kosong
    const codeCard = page.locator('[data-tour="join-code-card"]');
    await expect(codeCard).toBeVisible({ timeout: 10000 });
    const codeEl = codeCard.locator('code').first();
    await expect(codeEl).toBeVisible();
    const code = (await codeEl.textContent())?.trim() ?? '';
    expect(code.length).toBeGreaterThanOrEqual(8);

    // 3) Tombol Salin & Perbarui tersedia
    await expect(codeCard.getByRole('button', { name: /Salin/i })).toBeVisible();
    await expect(codeCard.getByRole('button', { name: /Perbarui Kode/i })).toBeVisible();

    // 4) Kode tersebut valid: join-info mengembalikan organisasi toko-maju
    const base = apiURL.replace(/\/+$/, '');
    const res = await page.request.get(`${base}/auth/join-info?code=${encodeURIComponent(code)}`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.tenant.slug).toBe(TENANT);

    // 5) Menu profil memuat pintu masuk "Gabung Perusahaan Lain"
    await page.locator('header').getByRole('button', { name: /Profil/i }).first().click();
    const menu = page.locator('header').getByRole('button', { name: /Gabung Perusahaan Lain/i }).first();
    await expect(menu).toBeVisible();
    // Navigasi ke halaman Gabung Perusahaan berfungsi
    await menu.click();
    await expect(page).toHaveURL(/\/auth\/join-company/, { timeout: 15000 });
    await expect(page.getByLabel(/Kode Bergabung/i)).toBeVisible();
  });
});
