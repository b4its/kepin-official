# KePin — Keuangan Pintar

**E RP SaaS multi-tenant untuk manajemen keuangan dan operasional bisnis kecil-menengah.** Backend FastAPI + SvelteKit 5 frontend, PostgreSQL, containerized via Docker Compose.

---

## Daftar Isi

- [Arsitektur](#arsitektur)
- [Tech Stack](#tech-stack)
- [Fitur](#fitur)
- [Model Data](#model-data)
- [API Endpoints](#api-endpoints)
- [Autentikasi & Otorisasi](#autentikasi--otorisasi)
- [Sidebar Customization](#sidebar-customization)
- [Makefile (Quick Start)](#makefile-quick-start)
- [Pengembangan Lokal](#pengembangan-lokal)
- [Docker Compose](#docker-compose)
- [Environment Variables](#environment-variables)
- [Struktur Direktori](#struktur-direktori)
- [Frontend Routes](#frontend-routes)

---

## Arsitektur

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│ SvelteKit 5  │     │  FastAPI     │     │    16-alpine  │
│  (Vite HMR)  │◀────│  Python 3.14 │◀────│   port 5434  │
│   port 3001  │     │   port 8001  │     └──────────────┘
└──────────────┘     └──────────────┘
                            │
                    ┌───────┴───────┐
                    │    Modules    │
                    │  (11 modul)   │
                    └───────────────┘
```

- **Backend + DB** berjalan di Docker.
- **Frontend** berjalan secara lokal (Vite dev server) untuk HMR — tidak di dalam container.

---

## Tech Stack

### Backend
| Komponen | Teknologi |
|---|---|
| Framework | FastAPI 0.140 |
| Python | 3.14-slim |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 (via psycopg 3) |
| Migrasi | Alembic |
| Auth | bcrypt + python-jose (JWT HS256) |
| Validasi | Pydantic v2 |
| Logging | structlog |
| Serializer | orjson |

### Frontend
| Komponen | Teknologi |
|---|---|
| Framework | SvelteKit 5 |
| Bahasa | TypeScript 6 |
| Styling | Tailwind CSS 4 |
| Ikon | Lucide Svelte |
| Chart | Chart.js 4 |
| Export PDF | jsPDF + jspdf-autotable |
| Export Excel | SheetJS (xlsx) |
| Bundler | Vite 8 |

---

## Fitur

### Auth & Tenant
- Registrasi & login dengan JWT (bcrypt)
- Multi-tenant: setiap organisasi adalah tenant terpisah
- Dua role: `tenant_owner` dan `employee`
- Pembuatan organisasi baru (dengan join code unik)
- Bergabung ke organisasi via `tenant_id` + `join_code`
- Empat paket langganan: Free, Basic, Premium, Platinum

### Modul Bisnis
- **Sales** — invoice, pelanggan, pembayaran
- **Purchasing** — purchase order, pemasok, goods receipt
- **Inventory** — produk, stok, stock movement, stock balance
- **Accounting** — chart of accounts, jurnal, transaksi, rekonsiliasi, bank account
- **Reporting** — laporan keuangan, laporan investor (export PDF/Excel)
- **Notifications** — notifikasi per tenant
- **Audit** — audit trail per tenant + platform-wide
- **Organization** — anggota, sidebar settings, branches, integrations, roles

### Export
- PDF (jsPDF + autoTable) — invoice, customers, products, stock movements, suppliers, PO, journals, COA, audit, reports, investor report
- Excel (SheetJS) — semua data di atas
- Export button via `ExportModal.svelte`

### Sidebar Customization
- `TenantSidebarSetting` (JSONB) menyimpan menu yang diaktifkan/dinonaktifkan
- `tenant_owner` dapat mengatur visibilitas menu via halaman Settings → Sidebar
- `employee` hanya melihat menu yang sudah diatur owner
- Setiap menu memiliki `key` unik yang stabil (`sales_invoices`, `inventory_products`, dll.)
- Menu `pinned` (Dashboard) tidak bisa disembunyikan

---

## Model Data

Backend memiliki **39 model SQLAlchemy**, di antaranya:

### Core
- `Tenant` — organisasi, memiliki `slug` (unik), `owner_id`, `join_code`, `plan_code`
- `User` — akun pengguna global, memiliki `password_hash`
- `Membership` — relasi User ↔ Tenant, dengan `role_name` (`tenant_owner`/`employee`)
- `Plan` — paket langganan (kode, nama, harga)
- `Subscription` — status langganan tenant
- `TenantSidebarSetting` — preferensi sidebar per tenant (JSONB `enabled_items`)

### Bisnis
- `Account`, `AccountBalance` — chart of accounts
- `JournalEntry`, `JournalLine` — jurnal akuntansi
- `Customer`, `Invoice`, `InvoiceLine`, `CustomerPayment`, `CustomerPaymentAllocation`
- `Supplier`, `PurchaseOrder`, `PurchaseOrderLine`, `GoodsReceipt`, `GoodsReceiptLine`
- `Product`, `InventoryLocation`, `StockBalance`, `StockMovement`
- `BankAccount`, `BankTransaction`, `ReconciliationMatch`
- `Notification`, `TenantAuditEvent`, `PlatformAuditEvent`
- `Branch`, `OrganizationSetting`, `Integration`
- `DocumentCounter`, `ExportJob`, `OutboxEvent`, `Incident`

---

## API Endpoints

Semua endpoint berada di bawah prefix `/api/v1`.

### Health
| Method | Path | Keterangan |
|---|---|---|
| GET | `/health/live` | Liveness check |
| GET | `/health/ready` | Readiness check (termasuk DB) |
| GET | `/health/startup` | Startup check |

### Auth (`/api/v1/auth`)
| Method | Path | Keterangan |
|---|---|---|
| POST | `/auth/register` | Registrasi user baru |
| POST | `/auth/login` | Login, kembalikan JWT + daftar tenant |
| GET | `/auth/me` | Data user saat ini |
| POST | `/auth/create-organization` | Buat tenant baru (dengan plan) |
| POST | `/auth/join-organization` | Gabung tenant via join code |
| GET | `/auth/plans` | Daftar paket langganan |

### Platform (`/api/v1/platform`)
| Method | Path | Keterangan |
|---|---|---|
| GET | `/platform/tenants` | Semua tenant (admin) |

### Tenant-Scoped (`/api/v1/tenants/{tenantSlug}`)

#### Organization
| Method | Path | Keterangan |
|---|---|---|
| GET | `/org/members` | Daftar anggota |
| POST | `/org/members` | Tambah anggota |
| PUT | `/org/members/{id}` | Ubah role anggota |
| DELETE | `/org/members/{id}` | Hapus anggota |
| GET | `/org/roles` | Daftar role |
| GET | `/org/branches` | Daftar cabang |
| POST | `/org/branches` | Tambah cabang |
| PUT | `/org/branches/{id}` | Ubah cabang |
| DELETE | `/org/branches/{id}` | Hapus cabang |

#### Accounting
| Method | Path | Keterangan |
|---|---|---|
| GET | `/accounts` | Chart of accounts |
| POST | `/accounts` | Buat akun |
| GET | `/journals` | Daftar jurnal |
| POST | `/journals` | Buat jurnal |
| GET | `/transactions` | Daftar transaksi |
| GET | `/reconciliation` | Rekonsiliasi bank |
| POST | `/reconciliation/match` | Cocokkan transaksi |

#### Sales
| Method | Path | Keterangan |
|---|---|---|
| GET | `/invoices` | Daftar invoice |
| POST | `/invoices` | Buat invoice |
| GET | `/customers` | Daftar pelanggan |
| POST | `/customers` | Tambah pelanggan |
| GET | `/payments` | Daftar pembayaran |

#### Purchasing
| Method | Path | Keterangan |
|---|---|---|
| GET | `/purchase-orders` | Daftar PO |
| POST | `/purchase-orders` | Buat PO |
| GET | `/suppliers` | Daftar pemasok |
| POST | `/suppliers` | Tambah pemasok |
| GET | `/goods-receipts` | Daftar goods receipt |

#### Inventory
| Method | Path | Keterangan |
|---|---|---|
| GET | `/products` | Daftar produk |
| POST | `/products` | Tambah produk |
| GET | `/stock-movements` | Pergerakan stok |
| POST | `/stock-movements/adjust` | Penyesuaian stok |
| GET | `/stock-balances` | Saldo stok |

#### Reports
| Method | Path | Keterangan |
|---|---|---|
| GET | `/reports` | Laporan keuangan |
| GET | `/reports/investor` | Laporan investor |
| GET | `/reports/export` | Export laporan |

#### Notifications & Audit
| Method | Path | Keterangan |
|---|---|---|
| GET | `/notifications` | Notifikasi |
| GET | `/audit-events` | Audit trail |

#### Sidebar Settings
| Method | Path | Keterangan |
|---|---|---|
| GET | `/sidebar-settings` | Ambil pengaturan sidebar |
| PUT | `/sidebar-settings` | Simpan pengaturan sidebar (owner only) |

---

## Autentikasi & Otorisasi

### Flow
1. `POST /auth/register` → buat `User` dengan `password_hash` (bcrypt)
2. `POST /auth/login` → verifikasi password → return `access_token` (JWT) + daftar `Tenant` milik user
3. Semua request tenant-scoped menyertakan `Authorization: Bearer <token>`
4. `get_current_user` dependency mengekstrak user dari JWT (401 jika invalid/expired)
5. `get_tenant_membership` dependency mengecek apakah user adalah member tenant (403 jika bukan)

### Role
- `tenant_owner` — akses penuh, bisa atur sidebar, kelola anggota
- `employee` — akses terbatas sesuai pengaturan sidebar

### Isolasi Tenant
Semua query tenant-scoped memfilter dengan `tenant_id`. Setiap modul menggunakan `get_tenant_membership` untuk memastikan user hanya bisa mengakses data tenannya sendiri.

---

## Sidebar Customization

- Model `TenantSidebarSetting` dengan kolom `enabled_items` (JSONB) di tabel `tenant_sidebar_settings`
- `GET /tenants/{slug}/sidebar-settings` — ambil setting (semua role)
- `PUT /tenants/{slug}/sidebar-settings` — simpan setting (hanya `tenant_owner`, 403 untuk `employee`)
- Frontend: `isNavEnabled(key)` membaca `enabled_items`; item yang tidak ada di setting default-nya enabled
- Menu `pinned` (Dashboard) tidak bisa disembunyikan

---

## Makefile (Quick Start)

Makefile menyediakan dua **mode** dan tiga **varian** per mode, dengan domain default `kepin.oryphem.com` (frontend) dan `api.kepin.oryphem.com` (backend).

### Mode
| Mode | Deskripsi |
|---|---|
| `dev` | Frontend vite dev (HMR) di host + backend/db/smtp di docker |
| `local` | Seluruh stack (frontend+backend+db+smtp) di docker |

### Varian per mode
| Varian | Perintah | Keterangan |
|---|---|---|
| Run | `make dev` / `make local` | Jalankan stack tanpa build ulang image |
| Build | `make dev-build` / `make local-build` | Build ulang image lalu jalankan |
| Build + Seed | `make dev-build-seed` / `make local-build-seed` | Build ulang + database fresh + **seed demo lengkap** (semua tenant & modul) lalu jalankan |

### Contoh penggunaan
```bash
# Mode development (HMR) — frontend di http://localhost:3001, backend :8001/docs
make dev

# Mode development + build backend
make dev-build

# Mode development + build + seed lengkap dari nol
make dev-build-seed

# Mode local (semua docker) — frontend :3001, backend :8001/docs
make local
make local-build
make local-build-seed
```

### Domain
```
kepin.oryphem.com     → frontend (port 3001)
api.kepin.oryphem.com → backend  (port 8001)
```

Semua URL domain dapat di-override:
```bash
# Contoh: pakai localhost alih-alih domain
make dev DOMAIN=localhost API_DOMAIN=localhost

# Override penuh URL API (mis. backend di port lokal)
make local-build PUBLIC_API_URL=http://localhost:8001/api/v1
```

### Utilitas
```bash
make seed          # wipe DB + seed demo lengkap (image yang sudah ada)
make seed-dev      # wipe DB + seed lengkap (hanya backend, untuk mode dev)
make ps            # status container
make logs          # tail log semua service
make down          # stop + hapus container (volume tetap)
make reset-db      # hapus container + volume DB (fresh total)
```

---

## Pengembangan Lokal

### Prasyarat
- Python 3.12+
- Node.js 22+
- pnpm
- Docker & Docker Compose
- GNU Make

### Setup
```bash
# 1. Clone repo
git clone <repo-url>
cd kepin

# 2. Jalankan backend + database (docker) & frontend vite dev (HMR)
make dev

# 3. (Opsional) Tanpa Makefile — manual:
#    docker compose --profile full up -d backend
#    cd frontend && pnpm install && pnpm dev --host 0.0.0.0
```

### Seed Data
Backend secara otomatis menjalankan `alembic upgrade head && python -m kepin.scripts.seed_demo` saat startup. Untuk regenerate seed lengkap dari nol (semua tenant & modul): `make dev-build-seed`, `make local-build-seed`, atau `make seed`.

Akun demo:
| Email | Password | Tenant |
|---|---|---|
| `budi@tokomaju.com` | `budi123` | `toko-maju` |
| `ani@tokomaju.com` | `ani12345` | `toko-maju` |
| `siti@warungsegar.com` | `siti123` | `warung-segar` |
| `admin@kepin.io` | `admin123` | — (platform admin) |

### Verifikasi
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001/api/v1
- API Docs: http://localhost:8001/docs
- DB: `psql -h localhost -p 5434 -U kepin -d kepin` (password: `kepin`)

### Commands Penting

```bash
# Backend (dalam container)
docker compose exec backend alembic upgrade head
docker compose exec backend python -m kepin.scripts.seed_demo
docker compose logs -f backend

# Frontend (dev HMR — atau gunakan `make dev`)
cd frontend && pnpm dev --host 0.0.0.0 --port 3001
cd frontend && pnpm build
cd frontend && pnpm check

# Build + jalankan frontend container (production build)
docker compose --profile full build frontend && docker compose --profile full up -d frontend
```

---

## Docker Compose

### Services

| Service | Image | Port | Profiles |
|---|---|---|---|
| `db` | postgres:16-alpine | 5434 | default |
| `backend` | python:3.14-slim (build) | 8001 | `full` |
| `frontend` | node:22-alpine (build) | 3001 | `full` |

### Profiles
- **Default** (`docker compose up -d`) — hanya database
- **Full** (`docker compose --profile full up -d`) — semua service

### Environment Backend (di compose.yaml)
```yaml
APP_ENV: production
APP_DEBUG: "false"
DATABASE_URL: postgresql+psycopg://kepin:kepin@db:5432/kepin
CORS_ORIGINS: "*"
AUTHORIZATION_ENABLED: "false"
SQL_ECHO: "false"
LOG_LEVEL: INFO
SMTP_HOST: smtp-sink
SMTP_PORT: "1025"
SMTP_TLS: "false"
SMTP_FROM: noreply@kepin.io
PUBLIC_APP_URL: ${PUBLIC_APP_URL:-http://localhost:3001}   # default, override via make/domain
```
`PUBLIC_API_URL` (build arg frontend): `${PUBLIC_API_URL:-http://localhost:8001/api/v1}` — default localhost, di-override jadi `http://api.kepin.oryphem.com/api/v1` lewat Makefile.

### Volume & Bind Mount
- `pgdata` — persistent PostgreSQL data (local driver)
- `./backend/src:/app/src:ro` — source backend live (perubahan cukup `docker restart kepin-backend`)
- `./backend/alembic:/app/alembic:ro` — migrasi live
- SMTP aktif di compose; untuk uji email jalankan sink di dalam container:
  ```sh
  docker exec kepin-backend pip install -q aiosmtpd
  docker cp backend/tests/regression/smtp_sink.py kepin-backend:/tmp/
  docker exec -d kepin-backend python /tmp/smtp_sink.py
  ```
  Tanpa sink, forgot-password fallback ke `dev_reset_token` di respons.

### Perubahan Frontend → Rebuild Image
Container `kepin-frontend` menjalankan **production build** (`node build/index.js`), bukan dev server.
Perubahan source frontend TIDAK otomatis terlihat; wajib rebuild:

```sh
docker compose build frontend && docker compose up -d frontend
```

---

## Environment Variables

### Backend (`Settings` class di `core/config.py`)
| Variable | Default | Keterangan |
|---|---|---|
| `APP_ENV` | `development` | Environment |
| `APP_DEBUG` | `true` | Debug mode |
| `DATABASE_URL` | `postgresql+psycopg://kepin:kepin@localhost:5432/kepin` | Koneksi DB |
| `SECRET_KEY` | `kepin-dev-secret-key-change-in-production` | Secret untuk JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritma JWT |
| `JWT_EXPIRE_MINUTES` | `1440` | Expiry token (24 jam) |
| `CORS_ORIGINS` | `*` | Origin CORS |
| `AUTHORIZATION_ENABLED` | `false` | Otorisasi aktif/nonaktif |
| `SQL_ECHO` | `false` | Log query SQL |
| `LOG_LEVEL` | `INFO` | Level logging |
| `SMTP_HOST` | `smtp-sink` | Host SMTP untuk email (reset password) |
| `SMTP_PORT` | `1025` | Port SMTP |
| `SMTP_TLS` | `false` | TLS SMTP |
| `SMTP_FROM` | `noreply@kepin.io` | Pengirim email |
| `PUBLIC_APP_URL` | `http://localhost:3001` | URL publik untuk link di email (default; via Makefile → `http://kepin.oryphem.com`) |

### Frontend
| Variable | Contoh | Keterangan |
|---|---|---|
| `PUBLIC_API_URL` | `http://localhost:8001/api/v1` | Base URL API (via Makefile → `http://api.kepin.oryphem.com/api/v1`) |

---

## Struktur Direktori

```
kepin/
├── compose.yaml                          # Docker Compose
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/                          # Migrasi database
│   │   ├── env.py
│   │   └── versions/
│   └── src/
│       └── kepin/
│           ├── main.py                   # Entrypoint FastAPI
│           ├── app.py                    # Factory aplikasi
│           ├── api/
│           │   ├── router.py             # Route aggregator
│           │   └── dependencies.py       # get_current_user, get_tenant_membership
│           ├── core/
│           │   ├── config.py             # Settings via pydantic-settings
│           │   ├── auth.py               # hash_password, verify_password, JWT
│           │   ├── logging.py            # structlog setup
│           │   └── exceptions.py
│           ├── db/
│           │   ├── base.py               # SQLAlchemy Base
│           │   ├── models.py             # 39 model ORM
│           │   └── session.py            # get_session async generator
│           ├── modules/
│           │   ├── accounting/api.py
│           │   ├── audit/api.py
│           │   ├── auth/
│           │   │   ├── api.py            # Endpoint auth
│           │   │   └── schemas.py        # Request/response schema
│           │   ├── inventory/api.py
│           │   ├── notifications/api.py
│           │   ├── organization/api.py
│           │   ├── platform/api.py
│           │   ├── purchasing/api.py
│           │   ├── reporting/api.py
│           │   ├── sales/api.py
│           │   ├── tenants/api.py
│           │   └── users/api.py          # Dev helper (not mounted)
│           └── scripts/
│               └── seed_demo.py          # Seeder data demo
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── pnpm-lock.yaml
    ├── tsconfig.json
    ├── svelte.config.js
    ├── vite.config.ts
    ├── .env                              # PUBLIC_API_URL
    └── src/
        ├── app.html
        ├── app.css
        ├── lib/
        │   ├── api.ts                    # api() fetch wrapper
        │   ├── config/
        │   │   └── navigation.ts         # clientNavigation, menu items
        │   ├── stores/
        │   │   ├── auth.ts               # Auth store (masih localStorage mock)
        │   │   └── data.ts               # sidebarSettings, currentRole, isNavEnabled
        │   ├── components/
        │   │   ├── layout/
        │   │   │   ├── WorkspaceShell.svelte
        │   │   │   ├── WorkspaceSidebar.svelte
        │   │   │   └── Topbar.svelte
        │   │   └── ui/
        │   │       ├── Card.svelte
        │   │       ├── Modal.svelte
        │   │       ├── ExportModal.svelte
        │   │       ├── DataTable.svelte
        │   │       └── ...
        │   └── utils/
        │       └── export.ts             # downloadPdf, downloadExcel
        └── routes/                       # 47 file route
            ├── +layout.svelte            # Root layout
            ├── (auth)/
            ├── (marketing)/
            ├── (platform)/admin/
            └── (workspace)/app/[tenantSlug]/
```

---

## Frontend Routes

### Auth (`/auth/*`)
| Route | Halaman |
|---|---|
| `/auth/login` | Login |
| `/auth/register` | Registrasi |
| `/auth/forgot-password` | Lupa password |
| `/auth/reset-password` | Reset password |
| `/auth/mfa` | MFA |

### Marketing (`/`)
| Route | Halaman |
|---|---|
| `/` | Landing page |
| `/privacy` | Kebijakan privasi |
| `/terms` | Syarat & ketentuan |
| `/security` | Keamanan |

### Platform Admin (`/admin/*`)
| Route | Halaman |
|---|---|
| `/admin` | Dashboard admin |
| `/admin/tenants` | Kelola tenant |
| `/admin/users` | Kelola user |
| `/admin/subscriptions` | Langganan |
| `/admin/audit` | Audit global |
| `/admin/incidents` | Insiden |
| `/admin/notifications` | Notifikasi global |
| `/admin/security` | Keamanan platform |

### Workspace (`/app/[tenantSlug]/*`)
| Route | Halaman |
|---|---|
| `/app/[slug]` | Dashboard tenant |
| `/app/[slug]/sales/invoices` | Invoice penjualan |
| `/app/[slug]/sales/customers` | Pelanggan |
| `/app/[slug]/purchasing/orders` | Purchase order |
| `/app/[slug]/purchasing/suppliers` | Pemasok |
| `/app/[slug]/inventory/products` | Produk |
| `/app/[slug]/inventory/products/[id]` | Detail produk |
| `/app/[slug]/inventory/movements` | Pergerakan stok |
| `/app/[slug]/transactions` | Transaksi |
| `/app/[slug]/accounting/chart-of-accounts` | COA |
| `/app/[slug]/accounting/journals` | Jurnal |
| `/app/[slug]/accounting/reconciliation` | Rekonsiliasi |
| `/app/[slug]/reports` | Laporan keuangan |
| `/app/[slug]/reports/investor` | Laporan investor |
| `/app/[slug]/insights` | Insight bisnis |
| `/app/[slug]/notifications` | Notifikasi |
| `/app/[slug]/audit` | Audit trail |
| `/app/[slug]/settings/organization` | Pengaturan organisasi |
| `/app/[slug]/settings/branches` | Cabang |
| `/app/[slug]/settings/members` | Anggota |
| `/app/[slug]/settings/roles` | Role & izin |
| `/app/[slug]/settings/sidebar` | Kustomisasi sidebar |
| `/app/[slug]/settings/billing` | Tagihan |
| `/app/[slug]/settings/integrations` | Integrasi |

---

## Catatan Pengembangan

### Authentication Store
Frontend `auth.ts` masih menggunakan localStorage mock dan belum terhubung ke backend API. Untuk production, store ini perlu diintegrasikan dengan endpoint `/auth/*`.

### Frontend Development
Frontend dijalankan secara lokal (bukan di Docker) agar HMR SvelteKit berfungsi penuh. Container `kepin-frontend` tersedia untuk production build via profile `full`.

### Authorization Flag
`AUTHORIZATION_ENABLED=false` di compose.yaml — dependency `get_current_user` tidak memblokir request. Set ke `true` untuk production.

### Migrasi
Alembic menjalankan migrasi otomatis saat container backend start. Untuk migrasi manual:
```bash
docker compose exec backend alembic revision --autogenerate -m "deskripsi"
docker compose exec backend alembic upgrade head
```
