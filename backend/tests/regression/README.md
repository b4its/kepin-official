# Regression suites (run inside kepin-backend container)

API-level regression scripts. Mereka memanggil live backend dan memakai data
demo (toko-maju / warung-segar / admin), jadi jalankan hanya di lingkungan
dev/qa yang sudah di-seed.

Cara pakai:

```sh
rtk docker cp backend/tests/regression/<script>.py kepin-backend:/tmp/
rtk docker exec kepin-backend python /tmp/<script>.py
```

Skrip:
- `tenant_test.py`            — sweep E2E tenant-side: 78 checks (RBAC, CRUD, journal/reversal, invoice/PO, payments, period close/reopen).
- `admin_test.py`             — 10 checks platform admin (tenants, subscriptions, audit, users).
- `mfa_test.py`               — 14 checks MFA flow.
- `change_pass_test.py`       — 9 checks change-password.
- `reset_test.py`             — 10 checks reset password (SMTP-aware; baca token dari `/tmp/smtp_emails.log`).
- `smtp_test.py`              — 8 checks pengiriman email reset lewat sink SMTP.
- `smtp_sink.py`              — aiosmtpd sink di 127.0.0.1:1025 → `/tmp/smtp_emails.log`.
- `integration_sync_test.py`  — 13 checks lifecycle integrasi (CRUD, sync batch, dedupe, error paths).
- `finance_test.py`           — 50+ checks manajemen keuangan: siklus tahun buku (buat/tutup/buka ulang, overlap, RBAC), rekening bank (PATCH/DELETE, guard transaksi), transaksi bank (hapus, external ID reusable), audit trail. Idempoten (purge FY uji sendiri).
- `reconcile.py`              — verifikasi subledger ↔ GL (ap/sales payable, stok, piutang); tanpa assert, print MATCH/CHECK.

Catatan `reconcile.py`: output akhir `ALL CHECKS PASS` menandakan buku seimbang.

Syarat untuk `smtp_test.py` / `reset_test.py`:

```sh
rtk docker exec kepin-backend pip install -q aiosmtpd
rtk docker cp backend/tests/regression/smtp_sink.py kepin-backend:/tmp/
rtk docker exec -d kepin-backend python /tmp/smtp_sink.py
```

Catatan: sink mati saat container di-recreate; jalankan ulang bila perlu.
