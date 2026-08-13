import { test, expect } from '@playwright/test';
import { DEMO_EMPLOYEE } from '../../helpers/ids';

const WEB = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';
const TENANT = DEMO_EMPLOYEE.tenant;

test.describe('Anggota Tim — non-owner', () => {
  test('menu Anggota Tim muncul di sidebar, tetapi kode bergabung disembunyikan', async ({ page }) => {
    // 1) Sidebar menampilkan "Anggota Tim" untuk karyawan
    await page.goto(`${WEB}/app/${TENANT}`);
    await page.waitForLoadState('networkidle');
    const sidebar = page.locator('[data-tour="workspace-sidebar"]');
    await expect(sidebar.getByRole('button', { name: /Anggota Tim/i }).first()).toBeVisible({ timeout: 10000 });

    // 2) Buka halaman Anggota Tim
    await sidebar.getByRole('button', { name: /Anggota Tim/i }).first().click();
    await expect(page).toHaveURL(/\/settings\/members$/, { timeout: 15000 });
    await page.waitForLoadState('networkidle');

    // 3) Tabel anggota tampil (read-only)
    await expect(page.locator('[data-tour="members-table"]')).toBeVisible({ timeout: 10000 });

    // 4) Kode bergabung TIDAK tampil untuk non-owner
    await expect(page.locator('[data-tour="join-code-card"]')).toHaveCount(0);

    // 5) Petunjuk read-only tampil untuk non-owner
    await expect(page.getByText(/Hanya tenant_owner yang dapat mengundang/i)).toBeVisible();

    // 6) Tombol "Undang Anggota" tidak tampil untuk non-owner
    await expect(page.getByRole('button', { name: /Undang Anggota/i })).toHaveCount(0);

    // 7) Karyawan TIDAK melihat opsi "Gabung Perusahaan" (single-company),
    //    tetapi melihat "Keluar dari Perusahaan Ini" di menu profil.
    await page.locator('header').getByRole('button', { name: /Profil/i }).first().click();
    await expect(page.locator('header').getByRole('button', { name: /Gabung Perusahaan/i })).toHaveCount(0);
    await expect(page.locator('header').getByRole('button', { name: /Keluar dari Perusahaan Ini/i }).first()).toBeVisible();
  });

  test('halaman Gabung Perusahaan menampilkan peringatan karena sudah punya perusahaan', async ({ page }) => {
    await page.goto(`${WEB}/auth/join-company`);
    await page.waitForLoadState('networkidle');

    // Karyawan yang sudah punya perusahaan tidak melihat form kode,
    // melainkan peringatan single-company.
    await expect(page.getByLabel(/Kode Bergabung/i)).toHaveCount(0);
    await expect(page.getByText(/sudah menjadi anggota perusahaan/i)).toBeVisible();
  });
});
