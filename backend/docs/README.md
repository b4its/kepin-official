# KePin Backend

Backend API untuk **KePin (Keuangan Pintar)** — platform akuntansi dan ERP multi-tenant berbasis SaaS.

## Stack

| Teknologi | Versi |
|---|---|
| Python | 3.14+ |
| FastAPI | 0.140+ |
| SQLAlchemy | 2.0+ (async) |
| PostgreSQL | 16+ |
| Alembic | 1.18+ |
| ORJSON | 3.11+ |
| Pydantic | 2.13+ |

## Arsitektur

- **Modular monolith** — seluruh domain dalam satu aplikasi
- **Async first** — FastAPI async + SQLAlchemy async + psycopg async
- **Multi-tenant** — shared database, shared schema, tenant discriminator
- **Tanpa auth** — mode development (`AUTHORIZATION_ENABLED=false`)

### Struktur Module

```
src/kepin/
├── main.py              # App factory
├── api/                 # Router, middleware, dependencies, error handlers
├── core/                # Config, pagination, money, time, UUID
├── db/                  # Base, session, ORM models
├── modules/             # Domain modules
│   ├── platform/        # Admin control plane
│   ├── tenants/         # Workspace context & dashboard
│   ├── organization/    # Settings, branches, members
│   ├── accounting/      # Chart of accounts, transactions, journals, reconciliation
│   ├── sales/           # Customers, invoices, payments
│   ├── purchasing/      # Suppliers, purchase orders, goods receipt
│   ├── inventory/       # Products, stock balances, movements
│   ├── reporting/       # Financial reports (PL, balance sheet, cash flow, aging)
│   ├── notifications/   # In-app notifications
│   ├── audit/           # Tenant audit trail
│   └── users/           # Dev auth (mock)
└── scripts/             # Seed demo
```

## Memulai

Lihat [setup.md](setup.md) untuk panduan instalasi.

Lihat [api_setup.md](api_setup.md) untuk dokumentasi endpoint.
