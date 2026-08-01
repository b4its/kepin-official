# Dokumentasi API / Swagger KePin

Dokumen ini berisi daftar lengkap seluruh endpoint REST API KePin yang dapat diakses melalui Swagger UI di `http://127.0.0.1:8000/docs`.

## Informasi Sistem

| Item | Nilai |
|------|-------|
| Title | KePin API |
| Version | 1.0.0 |
| Framework | FastAPI (Python) |
| Format | REST + JSON |
| Auth | JWT Bearer Token (HS256, expiry 24 jam) |
| Default response | ORJSON |
| Docs UI | `/docs` (Swagger), `/redoc` (ReDoc) |
| Schema | `/openapi.json` |

## Prefix Seluruh Route

```
/api/v1
```

## Health Check

Endpoint untuk memverifikasi status aplikasi. Tidak memerlukan autentikasi.

### GET `/api/v1/health/live`

Liveness probe — memastikan aplikasi berjalan.

Response `200`:
```json
{ "status": "live" }
```

### GET `/api/v1/health/ready`

Readiness probe — memastikan database dapat diakses.

Response `200`:
```json
{ "status": "ready" }
```

Response `503` (jika database tidak tersedia):
```json
{ "detail": "Database unavailable" }
```

### GET `/api/v1/health/startup`

Startup probe — memastikan aplikasi sudah selesai inisialisasi.

Response `200`:
```json
{ "status": "startup" }
```

## Auth

Endpoint autentikasi dan manajemen user. Tidak memerlukan token (kecuali `/auth/me`).

### GET `/api/v1/auth/plans`

Mendapatkan daftar subscription plan yang tersedia.

Response `200`:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Free",
      "code": "free",
      "price": 0,
      "currency": "IDR",
      "maxUsers": 3,
      "maxBranches": 1,
      "features": { "inventory": true, "accounting": false }
    }
  ]
}
```

### POST `/api/v1/auth/register`

Mendaftarkan user baru.

Request body:
```json
{
  "name": "Budi Santoso",
  "email": "budi@example.com",
  "password": "securePassword123",
  "phone": "08123456789"
}
```

Response `201`:
```json
{
  "id": "uuid",
  "name": "Budi Santoso",
  "email": "budi@example.com",
  "phone": "08123456789",
  "isActive": true,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

Error: `409` jika email sudah terdaftar.

### POST `/api/v1/auth/login`

Login dan mendapatkan JWT.

Request body:
```json
{
  "email": "budi@tokomaju.com",
  "password": "budi123"
}
```

Response `200`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "Budi Santoso",
    "email": "budi@tokomaju.com"
  },
  "tenants": [
    {
      "id": "uuid",
      "name": "Toko Maju",
      "slug": "toko-maju",
      "role": "tenant_owner",
      "plan": "free",
      "isActive": true
    }
  ]
}
```

Error: `401` jika email/password salah.

### GET `/api/v1/auth/me`

Mendapatkan profil user dan daftar tenant yang dimiliki. Memerlukan token.

Headers: `Authorization: Bearer <token>`

Response `200`:
```json
{
  "id": "uuid",
  "name": "Budi Santoso",
  "email": "budi@tokomaju.com",
  "phone": "08123456789",
  "isActive": true,
  "tenants": [
    {
      "id": "uuid",
      "name": "Toko Maju",
      "slug": "toko-maju",
      "role": "tenant_owner",
      "plan": "free",
      "isActive": true
    }
  ]
}
```

### POST `/api/v1/auth/create-organization`

Membuat organisasi/tenant baru untuk user yang sudah login.

Headers: `Authorization: Bearer <token>`

Request body:
```json
{
  "name": "Toko Baru",
  "slug": "toko-baru",
  "planCode": "free"
}
```

Response `201`:
```json
{
  "tenant": {
    "id": "uuid",
    "name": "Toko Baru",
    "slug": "toko-baru",
    "plan": "free",
    "isActive": true
  },
  "joinCode": "ABC123",
  "membership": {
    "role": "tenant_owner",
    "userId": "uuid",
    "tenantId": "uuid"
  }
}
```

### POST `/api/v1/auth/join-organization`

Bergabung ke organisasi yang sudah ada menggunakan join code.

Headers: `Authorization: Bearer <token>`

Request body:
```json
{
  "tenantId": "uuid",
  "joinCode": "ABC123"
}
```

Response `200`:
```json
{
  "tenant": { "id": "uuid", "name": "Toko Maju", "slug": "toko-maju", "role": "employee" },
  "membership": { "role": "employee", "userId": "uuid", "tenantId": "uuid" }
}
```

Error: `404` jika tenant tidak ditemukan, `400` jika join code salah.

## Platform Admin

Endpoint khusus platform administrator. Memerlukan role admin.

### GET `/api/v1/platform/dashboard`

Dashboard admin.

### GET `/api/v1/platform/tenants`

Daftar semua tenant (dengan pagination, search, filter).

Query params: `page`, `perPage`, `search`, `status`, `plan`

### POST `/api/v1/platform/tenants`

Membuat tenant baru dari admin panel.

### GET `/api/v1/platform/tenants/{tenant_id}`

Detail tenant.

### PATCH `/api/v1/platform/tenants/{tenant_id}`

Update tenant.

### DELETE `/api/v1/platform/tenants/{tenant_id}`

Hapus tenant.

### POST `/api/v1/platform/tenants/{tenant_id}/suspend`

Suspend tenant.

### POST `/api/v1/platform/tenants/{tenant_id}/reactivate`

Reactivate tenant.

### GET `/api/v1/platform/users`

Daftar semua user.

### POST `/api/v1/platform/users`

Buat user dari admin.

### GET `/api/v1/platform/users/{user_id}`

Detail user.

### PATCH `/api/v1/platform/users/{user_id}`

Update user.

### DELETE `/api/v1/platform/users/{user_id}`

Hapus user.

### GET `/api/v1/platform/subscriptions`

Daftar subscription.

### GET `/api/v1/platform/subscription-events`

Daftar event subscription (history perubahan plan).

### GET `/api/v1/platform/incidents`

Daftar incident.

### POST `/api/v1/platform/incidents`

Buat incident.

### PATCH `/api/v1/platform/incidents/{incident_id}`

Update incident.

### GET `/api/v1/platform/audit-events`

Daftar audit event platform.

### GET `/api/v1/platform/health-summary`

Ringkasan kesehatan platform.

## Tenant Workspace

Semua endpoint di bawah path `/api/v1/tenants/{tenantSlug}` memerlukan:
- JWT valid
- User terdaftar sebagai anggota tenant (role `tenant_owner` atau `employee`)

Parameter `{tenantSlug}` diganti dengan slug tenant, misal `toko-maju`.

### Tenants Context & Dashboard

#### GET `/api/v1/tenants/{tenantSlug}/context`

Konfigurasi dan konteks tenant aktif — user, branches, organization, sidebar settings.

#### GET `/api/v1/tenants/{tenantSlug}/dashboard`

Data dashboard dengan KPI dan metrik.

### Organization

#### GET `/api/v1/tenants/{tenantSlug}/organization`

Profil organisasi.

#### PATCH `/api/v1/tenants/{tenantSlug}/organization`

Update profil organisasi.

Request body:
```json
{
  "name": "Toko Maju Updated",
  "address": "Jl. Baru No. 1",
  "phone": "021-123456",
  "email": "info@tokomaju.com",
  "website": "https://tokomaju.com",
  "description": "Toko kelontong terbesar"
}
```

### Branches

#### GET `/api/v1/tenants/{tenantSlug}/branches`

Daftar cabang.

#### POST `/api/v1/tenants/{tenantSlug}/branches`

Buat cabang.

Request body:
```json
{
  "name": "Cabang Sudirman",
  "code": "CSM",
  "address": "Jl. Sudirman No. 1",
  "phone": "021-654321",
  "isActive": true
}
```

#### GET `/api/v1/tenants/{tenantSlug}/branches/{branch_id}`

Detail cabang.

#### PATCH `/api/v1/tenants/{tenantSlug}/branches/{branch_id}`

Update cabang.

#### DELETE `/api/v1/tenants/{tenantSlug}/branches/{branch_id}`

Hapus cabang.

### Members

#### GET `/api/v1/tenants/{tenantSlug}/members`

Daftar anggota tenant.

#### POST `/api/v1/tenants/{tenantSlug}/members`

Tambah anggota baru.

Request body:
```json
{
  "email": "user@example.com",
  "role": "employee"
}
```

#### PATCH `/api/v1/tenants/{tenantSlug}/members/{membership_id}`

Update role anggota.

Request body:
```json
{
  "role": "employee",
  "isActive": true
}
```

#### DELETE `/api/v1/tenants/{tenantSlug}/members/{membership_id}`

Hapus anggota dari tenant.

### Roles

#### GET `/api/v1/tenants/{tenantSlug}/roles`

Daftar role yang tersedia.

### Integrations

#### GET `/api/v1/tenants/{tenantSlug}/integrations`

Daftar integrasi yang terpasang.

#### POST `/api/v1/tenants/{tenantSlug}/integrations`

Mencatat integrasi baru (status awal `disconnected`).

#### PATCH `/api/v1/tenants/{tenantSlug}/integrations/{integrationId}`

Update nama tampilan atau status (`active` / `disconnected` / `error`).

#### DELETE `/api/v1/tenants/{tenantSlug}/integrations/{integrationId}`

Hapus integrasi; transaksi bank yang sudah diimpor tetap tersimpan.

#### POST `/api/v1/tenants/{tenantSlug}/integrations/{integrationId}/sync`

Sinkronisasi batch transaksi bank (khusus integrasi `active`). Body berisi
`bankAccountId` dan daftar `transactions` (`externalId`, `transactionDate`,
`description`, `amount`). Duplikat external ID dilewati; respons
`{ integration, imported, skipped }`.

### Billing

#### GET `/api/v1/tenants/{tenantSlug}/billing`

Informasi billing / subscription tenant.

### Sidebar Settings

#### GET `/api/v1/tenants/{tenantSlug}/sidebar-settings`

Mendapatkan konfigurasi visibilitas menu sidebar.

Response `200`:
```json
{
  "enabledItems": {
    "sales_invoices": true,
    "sales_customers": true,
    "purchasing_orders": true,
    "inventory_products": true,
    "accounting_chart_of_accounts": true,
    "reports": true,
    "notifications": true
  },
  "pinnedItems": ["dashboard"]
}
```

#### PUT `/api/v1/tenants/{tenantSlug}/sidebar-settings`

Update konfigurasi sidebar. Owner-only.

Request body:
```json
{
  "enabledItems": {
    "sales_invoices": true,
    "inventory_products": false
  }
}
```

### Accounting

#### GET `/api/v1/tenants/{tenantSlug}/accounts`

Daftar chart of accounts. Mendukung query params: `type`, `category`, `search`, `page`, `perPage`.

#### POST `/api/v1/tenants/{tenantSlug}/accounts`

Buat account baru.

Request body:
```json
{
  "code": "1-1000",
  "name": "Kas Besar",
  "type": "asset",
  "category": "current_asset",
  "balance": 0,
  "isSystem": false,
  "status": "active"
}
```

Field codes:
- `type`: `asset`, `liability`, `equity`, `revenue`, `expense`
- `category`: tergantung type (misal: `current_asset`, `fixed_asset`, `current_liability`, `long_term_liability`)

#### GET `/api/v1/tenants/{tenantSlug}/accounts/{account_id}`

Detail account.

#### PATCH `/api/v1/tenants/{tenantSlug}/accounts/{account_id}`

Update account.

#### DELETE `/api/v1/tenants/{tenantSlug}/accounts/{account_id}`

Hapus account (hanya non-system).

#### GET `/api/v1/tenants/{tenantSlug}/accounts/{account_id}/balance`

Saldo account.

#### GET `/api/v1/tenants/{tenantSlug}/transactions`

Daftar transaksi.

Query params: `type`, `status`, `fromDate`, `toDate`, `accountId`, `search`, `page`, `perPage`

#### POST `/api/v1/tenants/{tenantSlug}/transactions`

Buat transaksi.

#### GET `/api/v1/tenants/{tenantSlug}/transactions/{transaction_id}`

Detail transaksi.

#### PATCH `/api/v1/tenants/{tenantSlug}/transactions/{transaction_id}`

Update transaksi.

#### DELETE `/api/v1/tenants/{tenantSlug}/transactions/{transaction_id}`

Hapus transaksi.

#### POST `/api/v1/tenants/{tenantSlug}/transactions/{transaction_id}/post`

Post transaksi (mengunci, tidak bisa diedit).

#### POST `/api/v1/tenants/{tenantSlug}/transactions/{transaction_id}/void`

Void transaksi.

#### GET `/api/v1/tenants/{tenantSlug}/journals`

Daftar journal entries.

#### POST `/api/v1/tenants/{tenantSlug}/journals`

Buat journal entry.

Request body:
```json
{
  "date": "2025-01-15",
  "description": "Pembelian inventaris",
  "lines": [
    { "accountId": "uuid-account-1", "debit": 0, "credit": 500000 },
    { "accountId": "uuid-account-2", "debit": 500000, "credit": 0 }
  ]
}
```

#### GET `/api/v1/tenants/{tenantSlug}/journals/{journal_id}`

Detail journal.

#### PATCH `/api/v1/tenants/{tenantSlug}/journals/{journal_id}`

Update journal (jika belum dipost).

#### DELETE `/api/v1/tenants/{tenantSlug}/journals/{journal_id}`

Hapus journal (jika belum dipost).

#### POST `/api/v1/tenants/{tenantSlug}/journals/{journal_id}/post`

Post journal (mengunci).

#### POST `/api/v1/tenants/{tenantSlug}/journals/{journal_id}/reverse`

Reverse journal (membuat journal pembalik).

#### GET `/api/v1/tenants/{tenantSlug}/reconciliation`

Daftar reconciliation.

#### POST `/api/v1/tenants/{tenantSlug}/reconciliation/matches`

Buat reconciliation match.

#### POST `/api/v1/tenants/{tenantSlug}/reconciliation/matches/{match_id}/confirm`

Konfirmasi match.

#### DELETE `/api/v1/tenants/{tenantSlug}/reconciliation/matches/{match_id}`

Hapus match.

### Sales

#### GET `/api/v1/tenants/{tenantSlug}/customers`

Daftar customer. Query params: `search`, `status`, `page`, `perPage`

#### POST `/api/v1/tenants/{tenantSlug}/customers`

Buat customer.

Request body:
```json
{
  "name": "PT Customer Baru",
  "email": "customer@example.com",
  "phone": "08123456789",
  "address": "Jl. Example No. 1",
  "status": "active"
}
```

#### GET `/api/v1/tenants/{tenantSlug}/customers/{customer_id}`

Detail customer.

#### PATCH `/api/v1/tenants/{tenantSlug}/customers/{customer_id}`

Update customer.

#### DELETE `/api/v1/tenants/{tenantSlug}/customers/{customer_id}`

Hapus customer.

#### GET `/api/v1/tenants/{tenantSlug}/invoices`

Daftar invoice. Query params: `status`, `customerId`, `fromDate`, `toDate`, `search`, `page`, `perPage`

#### POST `/api/v1/tenants/{tenantSlug}/invoices`

Buat invoice.

Request body:
```json
{
  "customerId": "uuid",
  "date": "2025-01-15",
  "dueDate": "2025-02-14",
  "status": "draft",
  "lines": [
    {
      "description": "Produk A",
      "quantity": 2,
      "unitPrice": 50000,
      "taxRate": 11
    }
  ]
}
```

#### GET `/api/v1/tenants/{tenantSlug}/invoices/{invoice_id}`

Detail invoice.

#### PATCH `/api/v1/tenants/{tenantSlug}/invoices/{invoice_id}`

Update invoice.

#### DELETE `/api/v1/tenants/{tenantSlug}/invoices/{invoice_id}`

Hapus invoice.

#### POST `/api/v1/tenants/{tenantSlug}/invoices/{invoice_id}/send`

Tandai invoice sebagai terkirim.

#### POST `/api/v1/tenants/{tenantSlug}/invoices/{invoice_id}/cancel`

Batalkan invoice.

#### GET `/api/v1/tenants/{tenantSlug}/invoices/{invoice_id}/pdf`

Download invoice sebagai PDF.

#### GET `/api/v1/tenants/{tenantSlug}/customer-payments`

Daftar pembayaran customer.

#### POST `/api/v1/tenants/{tenantSlug}/customer-payments`

Buat pembayaran customer.

Request body:
```json
{
  "invoiceId": "uuid",
  "amount": 100000,
  "paymentDate": "2025-01-20",
  "paymentMethod": "bank_transfer",
  "reference": "TRF-001",
  "notes": "Pembayaran invoice"
}
```

#### POST `/api/v1/tenants/{tenantSlug}/customer-payments/{payment_id}/void`

Void pembayaran.

### Purchasing

#### GET `/api/v1/tenants/{tenantSlug}/suppliers`

Daftar supplier.

#### POST `/api/v1/tenants/{tenantSlug}/suppliers`

Buat supplier.

Request body:
```json
{
  "name": "PT Supplier Baru",
  "email": "supplier@example.com",
  "phone": "08123456789",
  "address": "Jl. Supplier No. 1",
  "status": "active"
}
```

#### GET `/api/v1/tenants/{tenantSlug}/suppliers/{supplier_id}`

Detail supplier.

#### PATCH `/api/v1/tenants/{tenantSlug}/suppliers/{supplier_id}`

Update supplier.

#### DELETE `/api/v1/tenants/{tenantSlug}/suppliers/{supplier_id}`

Hapus supplier.

#### GET `/api/v1/tenants/{tenantSlug}/purchase-orders`

Daftar purchase order.

#### POST `/api/v1/tenants/{tenantSlug}/purchase-orders`

Buat PO.

Request body:
```json
{
  "supplierId": "uuid",
  "date": "2025-01-15",
  "expectedDate": "2025-01-25",
  "status": "draft",
  "lines": [
    {
      "productId": "uuid",
      "description": "Produk X",
      "quantity": 10,
      "unitPrice": 25000
    }
  ]
}
```

#### GET `/api/v1/tenants/{tenantSlug}/purchase-orders/{po_id}`

Detail PO.

#### PATCH `/api/v1/tenants/{tenantSlug}/purchase-orders/{po_id}`

Update PO.

#### DELETE `/api/v1/tenants/{tenantSlug}/purchase-orders/{po_id}`

Hapus PO.

#### POST `/api/v1/tenants/{tenantSlug}/purchase-orders/{po_id}/send`

Tandai PO sebagai terkirim ke supplier.

#### POST `/api/v1/tenants/{tenantSlug}/purchase-orders/{po_id}/receive`

Terima barang dari PO (goods receipt). Ini akan menambah stok.

#### POST `/api/v1/tenants/{tenantSlug}/purchase-orders/{po_id}/cancel`

Batalkan PO.

### Inventory

#### GET `/api/v1/tenants/{tenantSlug}/products`

Daftar produk. Query params: `search`, `category`, `status`, `page`, `perPage`

#### POST `/api/v1/tenants/{tenantSlug}/products`

Buat produk.

Request body:
```json
{
  "sku": "SKU-001",
  "name": "Produk Contoh",
  "category": "Elektronik",
  "unit": "pcs",
  "price": 100000,
  "cost": 75000,
  "stock": 50,
  "minStock": 5,
  "maxStock": 100,
  "location": "Gudang A",
  "status": "active"
}
```

#### GET `/api/v1/tenants/{tenantSlug}/products/{product_id}`

Detail produk (termasuk stok per cabang jika ada).

#### PATCH `/api/v1/tenants/{tenantSlug}/products/{product_id}`

Update produk.

#### DELETE `/api/v1/tenants/{tenantSlug}/products/{product_id}`

Hapus produk.

#### GET `/api/v1/tenants/{tenantSlug}/stock-balances`

Saldo stok per produk dan cabang.

#### GET `/api/v1/tenants/{tenantSlug}/stock-movements`

Riwayat pergerakan stok.

Query params: `productId`, `type`, `fromDate`, `toDate`, `referenceType`, `page`, `perPage`

#### POST `/api/v1/tenants/{tenantSlug}/stock-movements/receipts`

Mencatat penerimaan stok (manual, tanpa PO).

#### POST `/api/v1/tenants/{tenantSlug}/stock-movements/issues`

Mencatat pengeluaran stok.

#### POST `/api/v1/tenants/{tenantSlug}/stock-movements/adjustments`

Mencatat penyesuaian stok (misal: hasil opname).

### Reports

#### GET `/api/v1/tenants/{tenantSlug}/reports/summary`

Ringkasan keuangan (total revenue, expense, profit, dsb).

Query params: `fromDate`, `toDate`, `branchId`

#### GET `/api/v1/tenants/{tenantSlug}/reports/profit-loss`

Laporan laba rugi.

#### GET `/api/v1/tenants/{tenantSlug}/reports/balance-sheet`

Neraca.

#### GET `/api/v1/tenants/{tenantSlug}/reports/cash-flow`

Arus kas.

#### GET `/api/v1/tenants/{tenantSlug}/reports/general-ledger`

Buku besar.

#### GET `/api/v1/tenants/{tenantSlug}/reports/receivable-aging`

Aging piutang.

#### GET `/api/v1/tenants/{tenantSlug}/reports/investor`

Laporan investor (ringkasan eksekutif).

### Notifications

#### GET `/api/v1/tenants/{tenantSlug}/notifications`

Daftar notifikasi tenant.

Query params: `isRead`, `type`, `page`, `perPage`

#### GET `/api/v1/tenants/{tenantSlug}/notifications/{notification_id}`

Detail notifikasi.

#### PATCH `/api/v1/tenants/{tenantSlug}/notifications/{notification_id}/read`

Tandai notifikasi sebagai sudah dibaca.

#### POST `/api/v1/tenants/{tenantSlug}/notifications/read-all`

Tandai semua notifikasi sebagai sudah dibaca.

#### DELETE `/api/v1/tenants/{tenantSlug}/notifications/{notification_id}`

Hapus notifikasi.

### Audit

#### GET `/api/v1/tenants/{tenantSlug}/audit-events`

Daftar audit event tenant.

Query params: `actorId`, `action`, `module`, `objectId`, `fromDate`, `toDate`, `page`, `perPage`

#### GET `/api/v1/tenants/{tenantSlug}/audit-events/{event_id}`

Detail audit event.

Response:
```json
{
  "id": "uuid",
  "actorId": "uuid",
  "action": "CREATE",
  "module": "sales.invoice",
  "objectId": "uuid",
  "objectType": "invoice",
  "changes": { "status": { "old": null, "new": "draft" } },
  "tenantId": "uuid",
  "createdAt": "2025-01-15T10:00:00Z"
}
```

## Status Code yang Sering Muncul

| Status | Kondisi |
|--------|---------|
| 200 | GET/PATCH/PUT berhasil |
| 201 | POST berhasil (resource baru) |
| 204 | DELETE berhasil (tanpa body) |
| 400 | Validasi input gagal (salah format) |
| 401 | Token tidak ada, expired, atau invalid |
| 403 | Token valid tetapi tidak punya akses ke resource |
| 404 | Resource tidak ditemukan |
| 409 | Konflik (duplikat) |
| 422 | Validasi schema Pydantic gagal |
| 500 | Error server internal |

## Cara Mengakses Swagger UI

1. Pastikan backend berjalan: `docker compose --profile full up -d`
2. Buka browser: `http://127.0.0.1:8000/docs`
3. Klik "Authorize" dan masukkan token: `Bearer <access_token>`
4. Coba endpoint langsung dari Swagger UI

## Catatan Penting

- Semua response menggunakan format **camelCase** (bukan snake_case).
- Pagination standar: `{ "items": [...], "total": 100, "page": 1, "perPage": 10, "pages": 10 }`.
- Filter tanggal memakai format ISO 8601: `YYYY-MM-DD`.
- Semua endpoint tenant-scoped memerlukan parameter `{tenantSlug}` di path.
- Token JWT dikirim sebagai `Authorization: Bearer <token>`.
