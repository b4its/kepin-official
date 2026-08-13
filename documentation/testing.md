# Strategi Testing KePin

Dokumen ini menjelaskan filosofi, jenis-jenis pengujian, dan siklus hidup testing pada sistem KePin.

## Filosofi Testing

KePin menggunakan strategi testing piramida terbalik untuk proyek ERP multi-tenant:

1. **Unit test** — Menguji logika bisnis murni (service layer, helper, utility) tanpa IO.
2. **Integration test** — Menguji interaksi antar komponen (API + database, API + cache).
3. **E2E / System test** — Menguji sistem sebagai satu kesatuan (frontend + backend + database).

Untuk fase saat ini, fokus utama adalah **E2E test dengan Playwright** yang mencakup API system test dan browser end-to-end test.

## Jenis Pengujian

### 1. Smoke Test

Tujuan: Memastikan sistem bisa dijalankan dan endpoint paling kritis merespons.

Cakupan:
- Health check backend (`/health/live`, `/health/ready`, `/health/startup`)
- Landing page frontend dapat diakses
- Halaman legal (privacy, terms, security) dapat dibuka
- Tidak ada HTTP 500 yang tidak terduga

Trigger: Setiap pull request, setiap kali stack dijalankan.

### 2. API System Test

Tujuan: Memvalidasi kontrak API, autentikasi, otorisasi, dan isolasi tenant tanpa browser.

Cakupan:
- Auth flow: register, login, me, error handling
- CRUD semua domain: sales, purchasing, inventory, accounting
- Pagination, search, filter, sort
- Tenant isolation: detail dan list lintas tenant harus ditolak
- Subscription plans dan organization lifecycle

Trigger: Setiap pull request, sebelum browser test.

### 3. Browser E2E Test

Tujuan: Memvalidasi alur pengguna dari UI hingga data tersimpan di backend dan kembali ke UI.

Cakupan:
- Marketing pages: landing, login form, register form
- Admin platform: dashboard, tenants, users, subscriptions, audit
- Client owner: seluruh workflow ERP (sales, purchasing, inventory, accounting, report)
- Client employee: operational read + owner-only negative test
- User tanpa organisasi: empty state, create organization, join organization

Trigger: Setiap pull request untuk smoke, nightly untuk full regression.

### 4. Visual / Responsive Test

Tujuan: Memastikan tampilan konsisten di berbagai ukuran layar.

Cakupan:
- Desktop 1440x900
- Mobile (Pixel 7)
- Sidebar, modal, form, data table tidak overflow
- Export dialog tidak terpotong

Trigger: Sebelum rilis, nightly.

### 5. Tenant Isolation Test

Tujuan: Quality gate wajib — tidak boleh ada kebocoran data antar tenant.

Pendekatan:
- Setiap test menggunakan dua tenant berbeda (`toko-maju` dan `warung-segar`)
- Resource dibuat di tenant A, diverifikasi tidak muncul di tenant B
- Detail/update/delete silang tenant mengembalikan 403/404
- Audit dan notification juga terisolasi per tenant

Trigger: Setiap pull request, sebagai bagian dari API system test.

### 6. Negative Test

Tujuan: Memastikan sistem menolak aksi yang tidak sah dengan cara yang aman.

Cakupan:
- Password salah: 401
- Email duplikat: 409
- Token expired / invalid: 401
- Employee mengakses owner-only endpoint: 403
- User tanpa membership mengakses tenant: 403
- Journal tidak seimbang: ditolak
- Join code salah: ditolak

## Siklus Hidup Test

### Development

1. Developer menulis test bersama fitur (test-first atau test-after).
2. Test dijalankan secara lokal dengan stack Docker.
3. Semua test harus lulus sebelum commit.

### Pull Request

1. Smoke test dijalankan pertama (3 menit).
2. API system test dijalankan (5 menit).
3. Browser test dijalankan per actor secara paralel (10-15 menit).
4. Jika ada yang gagal: artifact dikumpulkan, PR tidak digabung.

### Nightly / Release

1. Full regression: semua project Playwright dijalankan.
2. Visual regression test diaktifkan.
3. Test dengan jumlah data besar (pagination, stress) dijalankan.

## Prioritas Implementasi

| Prioritas | Area | Alasan |
|-----------|------|--------|
| 1 | Health, auth, marketing | Gate paling dasar |
| 2 | Tenant isolation | Quality gate keamanan |
| 3 | API CRUD per domain | Kontrak API harus stabil |
| 4 | Browser owner workflow | Workflow bisnis utama |
| 5 | Browser employee + no-org | Role-based access |
| 6 | Admin platform | Control plane |
| 7 | Export (PDF/Excel) | Fitur important |
| 8 | Visual/responsive | Polish |

## Tools yang Dipakai

| Tool | Fungsi |
|------|--------|
| Playwright | API system test + Browser E2E test |
| Google Chrome | Browser utama (channel: 'chrome') |
| Docker Compose | Menjalankan stack (backend, frontend, db) |
| Makefile | Quick start: `make local`, `make local-build`, `make local-build-seed`, `make seed` (lihat `make help`) |
| dotenv | Mengelola environment test |
| SvelteKit check | Validasi tipe frontend |
| HTML reporter | Report Playwright |
| JUnit reporter | Integrasi CI |

## Definisi Selesai (Done) untuk Sebuah Test

1. Nama test menjelaskan actor, aksi, dan hasil yang diharapkan.
2. Data yang dibuat unik dan bisa dibersihkan.
3. Tidak bergantung pada urutan eksekusi atau sleep statis.
4. Memakai locator semantik (getByRole, getByLabel).
5. Memverifikasi UI dan dampak backend (via API request).
6. Data tetap benar setelah page reload.
7. Memiliki negative assertion untuk boundary penting.
8. Berjalan di Google Chrome.
9. Lulus 3 kali berturut-turut sebelum masuk CI.
10. Artifact kegagalan cukup untuk diagnosis tanpa rerun.

## Aturan Pemisahan Suite

- Satu file test = satu domain fungsional.
- Satu project Playwright = satu actor.
- Shared code di `e2e/fixtures/` dan `e2e/helpers/`.
- Test tidak boleh bergantung pada data yang dibuat test lain.
- Setup actor disimpan di `storageState` dan dipakai ulang.
- Cleanup data dilakukan melalui API, bukan SQL langsung dari test.
