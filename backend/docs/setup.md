# Setup Backend KePin

## Prasyarat

- Python 3.12+
- PostgreSQL 16+
- Virtual environment (direkomendasikan)

## Instalasi

```bash
# Clone repository
git clone <repo-url>
cd kepin/backend

# Buat virtual environment
python3 -m venv env
source env/bin/activate  # Linux/Mac
# atau
env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Konfigurasi

Salin `.env.example` menjadi `.env` dan sesuaikan:

```bash
cp .env.example .env
```

Variabel penting:

| Variabel | Default | Keterangan |
|---|---|---|
| `APP_ENV` | `development` | Mode environment |
| `DATABASE_URL` | `postgresql+psycopg://kepin:kepin@localhost:5432/kepin` | Koneksi database |
| `CORS_ORIGINS` | `http://localhost:5173` | Origin frontend yang diizinkan |
| `AUTHORIZATION_ENABLED` | `false` | Nonaktifkan auth untuk development |

## Database

```bash
# Buat database PostgreSQL
createdb kepin

# Jalankan migration
alembic upgrade head

# Seed data demo (opsional)
python -m kepin.scripts.seed_demo
```

## Menjalankan Server

```bash
# Development
uvicorn kepin.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn kepin.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verifikasi

```bash
curl http://localhost:8000/api/v1/health/live
# Response: {"status":"ok"}
```

## Struktur Direktori

```
backend/
├── alembic/           # Migration scripts
├── docs/              # Dokumentasi
├── src/kepin/         # Source code
│   ├── api/           # Router, middleware, dependencies
│   ├── core/          # Config, pagination, money, time
│   ├── db/            # Base, session, models
│   ├── modules/       # Domain modules (platform, tenants, accounting, etc.)
│   └── scripts/       # Utility scripts (seed_demo)
├── tests/             # Test files
├── .env.example
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```
