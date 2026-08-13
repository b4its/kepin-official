import { test, expect } from '@playwright/test';
import { DEMO_OWNER, uniqueId } from '../../helpers/ids';
import { loginApi } from '../../fixtures/api.fixture';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8001/api/v1';
const TENANT = DEMO_OWNER.tenant;

test.describe('Tour Panduan', () => {
  test('tour step-by-step dari dashboard ke halaman lain', async ({ page }) => {
    // Login via API dulu (untuk localStorage token)
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    await api.dispose();

    // Buka dashboard
    await page.goto(`/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    await expect(page.locator('body')).toBeVisible();

    // Klik tombol "?" (bantuan) di topbar
    const tourBtn = page.getByRole('button', { name: /panduan/i });
    await expect(tourBtn).toBeVisible();
    await tourBtn.click();

    // Step 1: Selamat Datang — popover harus muncul
    const popover = page.locator('[class*="driver-popover"]').first();
    await expect(popover).toBeVisible({ timeout: 8000 });
    await expect(popover).toContainText(/Selamat Datang/i);

    // Klik Lanjut → step 2 (ringkasan dashboard)
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover).toContainText(/Ringkasan Dashboard/i);

    // Klik Lanjut → step 3 (sidebar)
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover).toContainText(/Navigasi Sidebar/i);

    // Klik Lanjut → step 4 (Produk — navigasi ke halaman produk)
    await popover.getByRole('button', { name: /Lanjut/i }).click();
    // Tunggu navigasi ke halaman produk
    await expect(page).toHaveURL(/products/);
    await page.waitForLoadState('networkidle');
    const popover2 = page.locator('[class*="driver-popover"]').first();
    await expect(popover2).toBeVisible({ timeout: 10000 });
    await expect(popover2).toContainText(/Daftar Produk/i);

    // Lanjutkan beberapa langkah, lalu tutup
    await popover2.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover2).toContainText(/Tambah Produk Baru/i);
    await popover2.getByRole('button', { name: /Lanjut/i }).click();
    await expect(popover2).toContainText(/Edit & Hapus Produk/i);

    // Tutup tour
    const closeBtn = popover2.locator('[class*="driver-close-btn"]').first();
    await closeBtn.click();
    await expect(popover2).not.toBeVisible({ timeout: 5000 });
  });
});