# API Setup KePin

## Base URL

Development: `http://localhost:8000/api/v1`

## Format Umum

### Request

- JSON body menggunakan **camelCase**
- Date format: `YYYY-MM-DD`
- Timestamp: ISO 8601 UTC

### Response List

```json
{
  "items": [],
  "page": 1,
  "pageSize": 5,
  "total": 24,
  "totalPages": 5
}
```

### Response Error

```json
{
  "code": "ERROR_CODE",
  "message": "Deskripsi error",
  "fieldErrors": {
    "fieldName": ["Error message"]
  },
  "requestId": "0190..."
}
```

### Query Parameter Umum

| Parameter | Tipe | Default | Keterangan |
|---|---|---|---|
| `page` | int | 1 | Halaman |
| `pageSize` | int | 5 | Item per halaman (max 100) |
| `search` | string | - | Pencarian |
| `sort` | string | - | Sort field (prefix `-` untuk DESC) |
| `status` | string | - | Filter status |
| `branchId` | UUID | - | Filter cabang |

### Filter Periode

| Parameter | Keterangan |
|---|---|
| `preset=last_week` | 7 hari terakhir |
| `preset=last_2_weeks` | 14 hari terakhir |
| `preset=last_3_weeks` | 21 hari terakhir |
| `preset=last_month` | 30 hari terakhir |
| `startDate=2026-07-01&endDate=2026-07-31` | Periode kustom |

## Endpoints

### Health

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/health/live` | Liveness check |
| GET | `/health/ready` | Readiness check (termasuk DB) |
| GET | `/health/startup` | Startup check |

### Platform Admin

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/platform/dashboard` | Dashboard platform |
| GET | `/platform/tenants` | List tenant |
| POST | `/platform/tenants` | Buat tenant |
| GET | `/platform/tenants/{id}` | Detail tenant |
| PATCH | `/platform/tenants/{id}` | Update tenant |
| DELETE | `/platform/tenants/{id}` | Hapus tenant |
| POST | `/platform/tenants/{id}/suspend` | Suspend tenant |
| POST | `/platform/tenants/{id}/reactivate` | Aktifkan tenant |
| GET | `/platform/users` | List users |
| POST | `/platform/users` | Buat user |
| GET | `/platform/users/{id}` | Detail user |
| PATCH | `/platform/users/{id}` | Update user |
| DELETE | `/platform/users/{id}` | Hapus user |
| GET | `/platform/subscriptions` | List subscriptions |
| GET | `/platform/subscription-events` | List subscription events |
| GET | `/platform/incidents` | List insiden |
| POST | `/platform/incidents` | Buat insiden |
| PATCH | `/platform/incidents/{id}` | Update insiden |
| GET | `/platform/audit-events` | List audit platform |
| GET | `/platform/health-summary` | Ringkasan kesehatan |

### Tenant Workspace

Semua endpoint di bawah prefiks `/tenants/{tenantSlug}`.

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/context` | Konteks tenant (profil, cabang) |
| GET | `/dashboard` | Dashboard tenant |
| GET | `/organization` | Pengaturan organisasi |
| PATCH | `/organization` | Update pengaturan |
| GET/POST | `/branches` | CRUD cabang |
| GET/PATCH/DELETE | `/branches/{id}` | Detail/update/hapus cabang |
| GET/POST | `/members` | CRUD anggota |
| GET/POST | `/roles` | Daftar roles |
| GET | `/integrations` | Daftar integrasi |
| GET | `/billing` | Informasi billing |

#### Akuntansi

| Method | Endpoint | Keterangan |
|---|---|---|
| GET/POST | `/accounts` | CRUD akun |
| GET/PATCH/DELETE | `/accounts/{id}` | Detail/update/hapus akun |
| GET | `/accounts/{id}/balance` | Saldo akun |
| GET/POST | `/transactions` | CRUD transaksi |
| GET/PATCH/DELETE | `/transactions/{id}` | Detail/update/hapus transaksi |
| POST | `/transactions/{id}/post` | Posting transaksi |
| POST | `/transactions/{id}/void` | Void transaksi |
| GET/POST | `/journals` | CRUD jurnal |
| GET/PATCH/DELETE | `/journals/{id}` | Detail/update/hapus jurnal |
| POST | `/journals/{id}/post` | Posting jurnal |
| POST | `/journals/{id}/reverse` | Reversal jurnal |
| GET | `/reconciliation` | List rekonsiliasi |
| POST | `/reconciliation/matches` | Buat match |
| POST | `/reconciliation/matches/{id}/confirm` | Konfirmasi match |
| DELETE | `/reconciliation/matches/{id}` | Hapus match |

#### Penjualan

| Method | Endpoint | Keterangan |
|---|---|---|
| GET/POST | `/customers` | CRUD pelanggan |
| GET/PATCH/DELETE | `/customers/{id}` | Detail/update/hapus |
| GET/POST | `/invoices` | CRUD invoice |
| GET/PATCH/DELETE | `/invoices/{id}` | Detail/update/hapus |
| POST | `/invoices/{id}/send` | Kirim invoice |
| POST | `/invoices/{id}/cancel` | Batal invoice |
| GET | `/invoices/{id}/pdf` | Download PDF |
| GET/POST | `/customer-payments` | CRUD pembayaran |
| POST | `/customer-payments/{id}/void` | Void pembayaran |

#### Pembelian

| Method | Endpoint | Keterangan |
|---|---|---|
| GET/POST | `/suppliers` | CRUD pemasok |
| GET/PATCH/DELETE | `/suppliers/{id}` | Detail/update/hapus |
| GET/POST | `/purchase-orders` | CRUD PO |
| GET/PATCH/DELETE | `/purchase-orders/{id}` | Detail/update/hapus |
| POST | `/purchase-orders/{id}/send` | Kirim PO |
| POST | `/purchase-orders/{id}/receive` | Terima barang |
| POST | `/purchase-orders/{id}/cancel` | Batal PO |

#### Inventaris

| Method | Endpoint | Keterangan |
|---|---|---|
| GET/POST | `/products` | CRUD produk |
| GET/PATCH/DELETE | `/products/{id}` | Detail/update/hapus |
| GET | `/stock-balances` | Saldo stok |
| GET | `/stock-movements` | Mutasi stok |
| POST | `/stock-movements/receipts` | Penerimaan stok |
| POST | `/stock-movements/issues` | Pengeluaran stok |
| POST | `/stock-movements/adjustments` | Penyesuaian stok |

#### Laporan

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/reports/summary` | Ringkasan keuangan |
| GET | `/reports/profit-loss` | Laba rugi |
| GET | `/reports/balance-sheet` | Neraca |
| GET | `/reports/cash-flow` | Arus kas |
| GET | `/reports/general-ledger` | Buku besar |
| GET | `/reports/receivable-aging` | Aging piutang |
| GET | `/reports/investor` | Laporan investor |

#### Notifikasi & Audit

| Method | Endpoint | Keterangan |
|---|---|---|
| GET/POST | `/notifications` | Daftar notifikasi |
| GET/DELETE | `/notifications/{id}` | Detail/hapus |
| PATCH | `/notifications/{id}/read` | Tandai dibaca |
| POST | `/notifications/read-all` | Tandai semua dibaca |
| GET | `/audit-events` | Daftar audit |
| GET | `/audit-events/{id}` | Detail audit |

### Dev Auth (hanya development)

| Method | Endpoint |
|---|---|
| POST | `/dev-auth/register` |
| POST | `/dev-auth/login` |
| POST | `/dev-auth/logout` |
| POST | `/dev-auth/forgot-password` |
| POST | `/dev-auth/reset-password` |
| GET | `/dev-auth/profile` |
| PATCH | `/dev-auth/profile` |
