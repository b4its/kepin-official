# API Setup untuk Testing

Dokumen ini menjelaskan cara menghubungkan test ke backend API KePin, mulai dari environment, autentikasi, hingga pola pemakaian fixture.

## Base URL

Semua endpoint REST API berada di bawah prefix:

```
/api/v1
```

Base URL untuk testing (dari `.env.e2e`):

```
E2E_API_URL=http://127.0.0.1:8000/api/v1
```

Jika backend berjalan di port berbeda, sesuaikan variable `E2E_API_URL`.

## Environment Test

Buat file `frontend/.env.e2e`:

```env
E2E_WEB_URL=http://127.0.0.1:5173
E2E_API_URL=http://127.0.0.1:8000/api/v1
E2E_OWNER_EMAIL=budi@tokomaju.com
E2E_OWNER_PASSWORD=budi123
E2E_OWNER_TENANT=toko-maju
E2E_EMPLOYEE_EMAIL=ani@tokomaju.com
E2E_EMPLOYEE_PASSWORD=ani12345
E2E_EMPLOYEE_TENANT=toko-maju
E2E_ADMIN_EMAIL=admin@kepin.io
E2E_ADMIN_PASSWORD=admin123
```

Global setup (`e2e/setup/global.ts`) akan memuat file ini sebelum worker Playwright dijalankan.

## Autentikasi

### Login API

Backend menggunakan JWT. Login dilakukan via `POST /auth/login`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "budi@tokomaju.com", "password": "budi123"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-user",
    "name": "Budi Santoso",
    "email": "budi@tokomaju.com"
  },
  "tenants": [
    {
      "id": "uuid-tenant",
      "name": "Toko Maju",
      "slug": "toko-maju",
      "role": "tenant_owner",
      "plan": "premium"
    }
  ]
}
```

### Memakai Token di Request

Semua endpoint terproteksi memakai header:

```
Authorization: Bearer <access_token>
```

### Fixture Login di Playwright

`e2e/fixtures/api.fixture.ts`:

```ts
import { expect, request } from '@playwright/test';

export async function loginApi(
  apiURL: string,
  email: string,
  password: string,
) {
  const anonymous = await request.newContext({ baseURL: apiURL });
  const response = await anonymous.post('/auth/login', {
    data: { email, password },
  });
  expect(response.status()).toBe(200);
  const body = await response.json();
  await anonymous.dispose();

  const api = await request.newContext({
    baseURL: apiURL,
    extraHTTPHeaders: {
      Authorization: `Bearer ${body.access_token}`,
      'Content-Type': 'application/json',
    },
  });

  return { api, token: body.access_token, userId: body.user.id };
}
```

## Membuat Data Unik

Setiap test harus membuat data miliknya sendiri. Gunakan helper `uniqueId` dari `e2e/helpers/ids.ts`:

```ts
export function uniqueId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function uniqueEmail(): string {
  return `e2e.${uniqueId()}@test.example`;
}
```

Contoh:

```ts
const customerName = `E2E Customer ${uniqueId()}`;
const sku = `SKU-${uniqueId()}`;
const slug = `tenant-${uniqueId().toLowerCase()}`;
```

## Cleanup Data

Setelah test selesai, data harus dibersihkan melalui API (bukan SQL langsung):

```ts
let createdId: string | undefined;

try {
  const create = await api.post(`/tenants/${slug}/customers`, { data: { name } });
  expect(create.ok()).toBeTruthy();
  createdId = (await create.json()).id;

  // ... assertions ...
} finally {
  if (createdId) {
    await api.delete(`/tenants/${slug}/customers/${createdId}`).catch(() => {});
  }
}
```

API context harus di-dispose setelah selesai:

```ts
await api.dispose();
```

## Verifikasi Backend dari Browser Test

Di dalam browser test, gunakan `request` fixture untuk verifikasi langsung ke backend:

```ts
test('customer tersimpan setelah reload', async ({ page, request }) => {
  // ... aksi UI ...
  await page.reload();
  await expect(page.getByText(customerName)).toBeVisible();

  // Verifikasi via API
  const res = await request.get(`/tenants/toko-maju/customers?search=${runId}`);
  expect(res.ok()).toBeTruthy();
});
```

## Daftar Semua Route API

Endpoint lengkap dicantumkan di [swagger.md](./swagger.md).

Ringkasan modul:

| Modul | Prefix Route | File API |
|-------|-------------|----------|
| Health | `/api/v1/health/*` | `router.py` (inline) |
| Auth | `/api/v1/auth/*` | `modules/auth/api.py` |
| Platform | `/api/v1/platform/*` | `modules/platform/api.py` |
| Tenants | `/api/v1/tenants/{slug}/*` | `modules/tenants/api.py` |
| Organization | `/api/v1/tenants/{slug}/*` | `modules/organization/api.py` |
| Accounting | `/api/v1/tenants/{slug}/*` | `modules/accounting/api.py` |
| Sales | `/api/v1/tenants/{slug}/*` | `modules/sales/api.py` |
| Purchasing | `/api/v1/tenants/{slug}/*` | `modules/purchasing/api.py` |
| Inventory | `/api/v1/tenants/{slug}/*` | `modules/inventory/api.py` |
| Reporting | `/api/v1/tenants/{slug}/reports/*` | `modules/reporting/api.py` |
| Notifications | `/api/v1/tenants/{slug}/notifications/*` | `modules/notifications/api.py` |
| Audit | `/api/v1/tenants/{slug}/audit-events/*` | `modules/audit/api.py` |

## Status Code yang Umum

| Status | Arti |
|--------|------|
| 200 | Success (GET, PATCH, PUT) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Bad Request (validasi gagal) |
| 401 | Unauthorized (token tidak ada/expired) |
| 403 | Forbidden (tidak punya akses) |
| 404 | Not Found (resource tidak ada) |
| 409 | Conflict (duplikat) |
| 422 | Unprocessable Entity (validasi schema) |
| 500 | Internal Server Error |

## Menjalankan API Test

```bash
cd /home/xmitsu/programming/python/kepin/frontend

# Semua API test
bash node_modules/.bin/playwright test --project=api

# Satu file
bash node_modules/.bin/playwright test e2e/api/health.spec.ts --project=api
bash node_modules/.bin/playwright test e2e/api/auth.spec.ts --project=api
bash node_modules/.bin/playwright test e2e/api/tenant-isolation.spec.ts --project=api
bash node_modules/.bin/playwright test e2e/api/domain-contracts.spec.ts --project=api

# Dengan grep
bash node_modules/.bin/playwright test --project=api --grep "login"
```
