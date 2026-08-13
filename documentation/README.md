# Pedoman Testing KePin

Dokumen ini adalah pintu masuk utama untuk seluruh aktivitas pengujian sistem KePin. Semua panduan, referensi, dan dokumentasi teknis dapat diakses dari sini.

## Daftar Dokumen

| Dokumen | Isi |
|---------|-----|
| [README.md](./README.md) | **Halaman ini** — navigasi utama, prasyarat, cara menjalankan semua pengujian satu per satu |
| [testing.md](./testing.md) | Strategi, filosofi, jenis testing, dan siklus hidup pengujian |
| [playwright-e2e.md](./playwright-e2e.md) | Panduan implementasi teknis Playwright: konfigurasi, fixture, lokator, isolasi tenant, CI |
| [api_setup.md](./api_setup.md) | Setup environment dan koneksi API untuk pengujian |
| [swagger.md](./swagger.md) | Dokumentasi lengkap seluruh endpoint backend OpenAPI/Swagger |
| [admin.md](./admin.md) | Skenario dan acceptance criteria untuk platform admin |
| [tenant-owner.md](./tenant-owner.md) | Skenario dan acceptance criteria untuk pemilik tenant |
| [tenant-employee.md](./tenant-employee.md) | Skenario dan acceptance criteria untuk karyawan tenant |
| [employee-without-organization.md](./employee-without-organization.md) | Skenario untuk user yang belum memiliki organisasi |

## Prasyarat Sistem

Sebelum menjalankan pengujian, pastikan seluruh komponen sistem berjalan. Gunakan Makefile di root proyek:

```bash
# 1. Build dan jalankan seluruh stack (mode local, semua docker)
cd /home/xmitsu/programming/python/kepin
make local-build          # atau `make local` jika image sudah ada

# 2. (Opsional) Seed demo lengkap dari nol
make local-build-seed     # build + database fresh + seed semua tenant/modul

# 3. Verifikasi semua service hidup
make ps

# 4. Tunggu hingga backend siap (max 2 menit)
curl --retry 30 --retry-delay 4 --fail http://127.0.0.1:8001/api/v1/health/ready

# 5. Verifikasi frontend siap
curl --fail http://127.0.0.1:3001/

# 6. Cek Swagger UI bisa diakses
curl --fail http://127.0.0.1:8001/docs
```

Untuk mode development (frontend HMR di host):
```bash
make dev                  # backend/db docker + frontend vite dev di :3001
```

Domain default (dapat di-override): `kepin.oryphem.com` → frontend, `api.kepin.oryphem.com` → backend.
Lihat `make help` untuk semua varian: `make dev`, `make dev-build`, `make dev-build-seed`, `make local`, `make local-build`, `make local-build-seed`, `make seed`, `make seed-dev`, `make ps`, `make logs`, `make down`, `make reset-db`.

## Instalasi Playwright

```bash
cd /home/xmitsu/programming/python/kepin/frontend
pnpm install
# Verifikasi Google Chrome tersedia
google-chrome-stable --version
# Untuk sistem tanpa sudo (seperti environment saat ini), 
# Playwright sudah dikonfigurasi memakai channel: 'chrome'
# Tidak perlu menjalankan playwright install --with-deps
```

## Cara Menjalankan Pengujian Satu per Satu

Semua perintah dijalankan dari direktori `frontend/`.

### 1. API Tests (tanpa browser)

Menguji health, auth, tenant isolation, dan kontrak domain API backend.

```bash
# Semua API test dalam satu project
bash node_modules/.bin/playwright test --project=api

# Satu file API test
bash node_modules/.bin/playwright test e2e/api/health.spec.ts --project=api
bash node_modules/.bin/playwright test e2e/api/auth.spec.ts --project=api
bash node_modules/.bin/playwright test e2e/api/tenant-isolation.spec.ts --project=api
bash node_modules/.bin/playwright test e2e/api/domain-contracts.spec.ts --project=api

# Satu test dalam file (gunakan --grep dengan nama test)
bash node_modules/.bin/playwright test --project=api --grep "health endpoint"
bash node_modules/.bin/playwright test --project=api --grep "login valid"
bash node_modules/.bin/playwright test --project=api --grep "cross-tenant"
```

### 2. Public / Marketing Pages (browser, tanpa login)

Menguji halaman publik yang bisa diakses siapa saja.

```bash
# Semua test public
bash node_modules/.bin/playwright test --project=chrome-public

# Satu file
bash node_modules/.bin/playwright test e2e/public/marketing-auth.spec.ts --project=chrome-public

# Satu test
bash node_modules/.bin/playwright test --project=chrome-public --grep "landing page"
```

### 3. Admin Platform (browser, login sebagai admin)

Menguji seluruh halaman control plane admin.

```bash
# Setup admin dulu (login & simpan storageState)
bash node_modules/.bin/playwright test --project=setup-admin

# Jalankan test admin (secara otomatis menjalankan setup-admin sebagai dependency)
bash node_modules/.bin/playwright test --project=chrome-admin

# Satu file
bash node_modules/.bin/playwright test e2e/admin/dashboard.spec.ts --project=chrome-admin

# Dengan browser terlihat (debugging)
bash node_modules/.bin/playwright test e2e/admin/dashboard.spec.ts --project=chrome-admin --headed
```

### 4. Tenant Owner (browser, login sebagai budi@tokomaju.com)

Menguji seluruh workspace client sebagai pemilik tenant.

```bash
# Setup owner dulu
bash node_modules/.bin/playwright test --project=setup-owner

# Semua test owner
bash node_modules/.bin/playwright test --project=chrome-tenant-owner

# Per domain
bash node_modules/.bin/playwright test e2e/client/owner/auth-context.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/sales.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/purchasing-inventory.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/accounting.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/reports.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/organization.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/notifications-audit.spec.ts --project=chrome-tenant-owner
bash node_modules/.bin/playwright test e2e/client/owner/all-pages.spec.ts --project=chrome-tenant-owner

# Satu test spesifik
bash node_modules/.bin/playwright test --project=chrome-tenant-owner --grep "create customer"
```

### 5. Tenant Employee (browser, login sebagai ani@tokomaju.com)

Menguji akses operational karyawan dan pembatasan owner-only.

```bash
# Setup employee dulu
bash node_modules/.bin/playwright test --project=setup-employee

# Semua test employee
bash node_modules/.bin/playwright test --project=chrome-tenant-employee

# Satu file
bash node_modules/.bin/playwright test e2e/client/employee/employee.spec.ts --project=chrome-tenant-employee

# Satu test
bash node_modules/.bin/playwright test --project=chrome-tenant-employee --grep "employee can open"
```

### 6. User Tanpa Organisasi (browser, user baru)

Menguji onboarding user yang belum punya tenant.

```bash
# Semua test no-organization
bash node_modules/.bin/playwright test --project=chrome-no-organization

# Satu file
bash node_modules/.bin/playwright test e2e/client/no-organization/no-org.spec.ts --project=chrome-no-organization

# Satu test
bash node_modules/.bin/playwright test --project=chrome-no-organization --grep "dashboard shows"
```

### 7. Menjalankan Ulang Setup Saja

Jika storageState sudah ada tetapi ingin memperbarui sesi login:

```bash
bash node_modules/.bin/playwright test --project=setup-admin
bash node_modules/.bin/playwright test --project=setup-owner
bash node_modules/.bin/playwright test --project=setup-employee
```

### 8. Full Regression (semua project)

Menjalankan seluruh suite sekaligus:

```bash
bash node_modules/.bin/playwright test --project=api --project=chrome-public --project=chrome-admin --project=chrome-tenant-owner --project=chrome-tenant-employee --project=chrome-no-organization
```

## Mode Khusus

### Headed mode (lihat browser)

```bash
bash node_modules/.bin/playwright test --project=chrome-tenant-owner --headed
```

### UI mode (debug interaktif)

```bash
bash node_modules/.bin/playwright test --ui
```

### Debug mode (PWDEBUG)

```bash
PWDEBUG=1 bash node_modules/.bin/playwright test e2e/api/auth.spec.ts --project=api
```

### Slow mo (perlambat eksekusi)

```bash
bash node_modules/.bin/playwright test --project=chrome-tenant-owner --headed --slow-mo 500
```

### Trace viewer

```bash
bash node_modules/.bin/playwright show-trace test-results/artifacts/<trace-file>.zip
```

## Urutan Quality Gate yang Direkomendasikan

Pipeline lokal untuk pull request:

```bash
# 1. Pastikan service hidup
curl --fail http://127.0.0.1:8001/api/v1/health/live
curl --fail http://127.0.0.1:8001/api/v1/health/ready
curl --fail http://127.0.0.1:3001/

# 2. API test (paling cepat, tanpa browser)
bash node_modules/.bin/playwright test --project=api

# 3. Public pages (smoke test browser)
bash node_modules/.bin/playwright test --project=chrome-public

# 4. Admin platform
bash node_modules/.bin/playwright test --project=chrome-admin

# 5. Tenant owner (workflow terlengkap)
bash node_modules/.bin/playwright test --project=chrome-tenant-owner

# 6. Tenant employee
bash node_modules/.bin/playwright test --project=chrome-tenant-employee

# 7. No organization
bash node_modules/.bin/playwright test --project=chrome-no-organization

# 8. Jika gagal, kumpulkan log
docker compose logs --no-color backend db frontend > test-results/docker.log
```

## Melihat Report

```bash
cd /home/xmitsu/programming/python/kepin/frontend
bash node_modules/.bin/playwright show-report
```

Report HTML tersedia di `frontend/playwright-report/index.html`. Artifact kegagalan (screenshot, video, trace) ada di `frontend/test-results/artifacts/`.

## Catatan Penting

- Karena environment saat ini tidak memiliki sudo, Playwright menggunakan **Google Chrome sistem** melalui `channel: 'chrome'` — bukan Chromium bundle.
- `pnpm exec playwright` adalah shell script; gunakan `bash node_modules/.bin/playwright` untuk menjalankan langsung.
- Setup harus login ke backend API terlebih dahulu karena frontend belum terintegrasi penuh dengan JWT.
- Workaround `localStorage` (seed session) dipakai sementara di fixture setup sampai frontend auth terhubung ke backend.
- Jangan menjalankan test paralel untuk workflow yang mengubah data yang sama. Gunakan `workers: 1` untuk suite yang memodifikasi resource.

## Akun Demo untuk Testing

| Aktor | Email | Password | Tenant | Role |
|-------|-------|----------|--------|------|
| Admin | admin@kepin.io | admin123 | — | Platform admin |
| Owner | budi@tokomaju.com | budi123 | toko-maju | tenant_owner |
| Employee | ani@tokomaju.com | ani12345 | toko-maju | employee |
| Employee 2 | siti@warungsegar.com | siti123 | warung-segar | employee |

## Struktur Test File

```
frontend/e2e/
├── admin/
│   └── dashboard.spec.ts          # 8 test — halaman admin
├── api/
│   ├── health.spec.ts             # 3 test — live, ready, startup
│   ├── auth.spec.ts               # 5 test — login, register, me, error
│   ├── tenant-isolation.spec.ts   # 2 test — cross-tenant block
│   └── domain-contracts.spec.ts   # 7 test — CRUD domain
├── client/
│   ├── employee/
│   │   └── employee.spec.ts       # 12 test — operational + restrictions
│   ├── no-organization/
│   │   └── no-org.spec.ts         # 3 test — empty state, public, redirect
│   └── owner/
│       ├── accounting.spec.ts     # 4 test — CoA, journal, transaction
│       ├── all-pages.spec.ts      # 22 test — setiap route workspace
│       ├── auth-context.spec.ts   # 2 test — dashboard, navigation
│       ├── notifications-audit.spec.ts # 4 test
│       ├── organization.spec.ts   # 8 test — settings, members, sidebar
│       ├── purchasing-inventory.spec.ts # 4 test
│       ├── reports.spec.ts        # 3 test
│       └── sales.spec.ts          # 3 test
├── fixtures/
│   ├── api.fixture.ts             # loginApi() helper
│   └── auth.fixture.ts            # seedFrontendSession() workaround
├── helpers/
│   └── ids.ts                     # uniqueId, uniqueEmail, akun demo constants
├── public/
│   └── marketing-auth.spec.ts     # 6 test — landing, login, register, legal
└── setup/
    ├── auth.setup.ts              # Setup admin
    ├── auth-owner.setup.ts        # Setup owner
    ├── auth-employee.setup.ts     # Setup employee
    └── global.ts                  # Load .env.e2e before all workers
```

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `browserType.launch: Executable doesn't exist` | Pastikan Google Chrome terinstal: `which google-chrome-stable` |
| `ECONNREFUSED backend` | Jalankan `docker compose --profile full up -d` dari root proyek |
| `401 Unauthorized` | Sesuaikan `.env.e2e` dengan kredensial yang benar |
| `storageState not found` | Jalankan setup project terlebih dahulu |
| Playwright gagal di invoke | Gunakan `bash node_modules/.bin/playwright` bukan `pnpm exec playwright` |
