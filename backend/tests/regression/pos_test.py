import sys
import time

from decimal import Decimal

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=30)

ok = True


def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def login(email, pw):
    r = C.post("/auth/login", json={"email": email, "password": pw})
    return r.json().get("access_token", "")


T = login("budi@tokomaju.com", "budi123")
H = {"authorization": f"Bearer {T}"}
S = "toko-maju"


def jget(path, headers=H):
    r = C.get(f"/tenants/{S}{path}", headers=headers)
    try:
        b = r.json()
    except Exception:
        b = {}
    return r.status_code, b


def jpost(path, payload=None, headers=H):
    r = C.post(f"/tenants/{S}{path}", json=payload or {}, headers=headers)
    try:
        b = r.json()
    except Exception:
        b = {}
    return r.status_code, b


def okv(body, snake, camel):
    if snake in body:
        return body.get(snake)
    return body.get(camel)


PROD_PREFIX = "SKU-POS-"


def purge_pos_fixtures():
    import asyncio

    from sqlalchemy import delete, select

    from kepin.db.session import get_session
    from kepin.db.models import Product, StockBalance, StockMovement, Tenant

    async def _purge():
        async for s in get_session():
            tenant = (
                await s.execute(select(Tenant).where(Tenant.slug == "toko-maju"))
            ).scalar_one()
            pids = (
                await s.execute(
                    select(Product.id).where(
                        Product.tenant_id == str(tenant.id),
                        Product.sku.like(f"{PROD_PREFIX}%"),
                    )
                )
            ).scalars().all()
            for pid in pids:
                await s.execute(
                    delete(StockMovement).where(StockMovement.product_id == pid)
                )
                await s.execute(
                    delete(StockBalance).where(StockBalance.product_id == pid)
                )
                await s.execute(delete(Product).where(Product.id == pid))
            await s.commit()

    asyncio.run(_purge())


purge_pos_fixtures()

ts = str(int(time.time() * 1000))[-8:]
sc, body = jpost("/products", {
    "sku": f"{PROD_PREFIX}{ts}",
    "name": f"POS Barang {ts}",
    "unit": "pcs",
    "sale_price": "25000",
    "cost_price": "15000",
    "minimum_stock": "2",
})
check("POS product create 201", sc == 201, f"{sc}")
pid = okv(body, "id", "id")
check("POS product id present", bool(pid))

sc, body = jget("/inventory-locations")
check("POS locations 200", sc == 200 and len(body) > 0, f"{sc} {len(body)}")
loc_id = okv(body[0], "id", "id") if body else None
check("POS location id present", bool(loc_id))

# ── Stok masuk (tambah stok via receipt) ─────────────────────────────
sc, body = jpost("/stock-movements/receipts", {
    "product_id": pid,
    "location_id": loc_id,
    "quantity": "10",
    "unit_cost": "15000",
    "reason": "Penerimaan awal POS test",
})
check("POS receipt 201", sc == 201, f"{sc}")
check("POS receipt type in", okv(body, "type", "type") == "in", str(body.get("type")))
check("POS receipt before/after", okv(body, "before_stock", "beforeStock") == "0.00" and okv(body, "after_stock", "afterStock") == "10.00", f"{body.get('before_stock')} → {body.get('after_stock')}")

sc, body = jget("/stock-balances")
row = next((r for r in body if okv(r, "product_id", "productId") == pid), None)
check("POS balance after receipt", row is not None and Decimal(okv(row, "quantity", "quantity") or "0") == Decimal("10"), str(row))

# ── Stok kurang dari yang diminta → ditolak ──────────────────────────
sc, body = jpost("/pos/checkout", {
    "items": [{"product_id": pid, "quantity": "99"}],
})
check("POS checkout insufficient stock 422", sc == 422, f"{sc} {body}")

# ── Stok keluar manual (kurangi stok via issue) ──────────────────────
sc, body = jpost("/stock-movements/issues", {
    "product_id": pid,
    "location_id": loc_id,
    "quantity": "4",
    "reason": "Pengurangan manual POS test",
})
check("POS issue 201", sc == 201, f"{sc}")
check("POS issue type out", okv(body, "type", "type") == "out", str(body.get("type")))
check("POS issue before/after", okv(body, "before_stock", "beforeStock") == "10.00" and okv(body, "after_stock", "afterStock") == "6.00", f"{body.get('before_stock')} → {body.get('after_stock')}")

sc, body = jget("/stock-balances")
row = next((r for r in body if okv(r, "product_id", "productId") == pid), None)
check("POS balance after issue", row is not None and Decimal(okv(row, "quantity", "quantity") or "0") == Decimal("6"), str(row))

# ── Checkout POS (multi-item, stok terpotong otomatis) ───────────────
sc, body = jpost("/pos/checkout", {
    "items": [{"product_id": pid, "quantity": "2"}, {"product_id": pid, "quantity": "1"}],
    "reason": "Checkout test",
})
check("POS checkout 201", sc == 201, f"{sc} {body}")
check("POS checkout number", (okv(body, "checkout_number", "checkoutNumber") or "").startswith("POS-"), str(body.get("checkout_number")))
check("POS checkout total qty", Decimal(okv(body, "total_quantity", "totalQuantity") or "0") == Decimal("3"), str(body.get("total_quantity")))
mvs = okv(body, "movements", "movements") or []
check("POS checkout movements single", len(mvs) == 1, f"{len(mvs)}")
check("POS checkout movement type out", okv(mvs[0], "type", "type") == "out", str(mvs))
check("POS checkout movement before/after", okv(mvs[0], "before_stock", "beforeStock") == "6.00" and okv(mvs[0], "after_stock", "afterStock") == "3.00", f"{mvs[0]}")
check("POS checkout movement product", okv(mvs[0], "product_id", "productId") == pid and okv(mvs[0], "product_name", "productName").startswith("POS Barang"), str(mvs[0]))

sc, body = jget("/stock-balances")
row = next((r for r in body if okv(r, "product_id", "productId") == pid), None)
check("POS balance after checkout", row is not None and Decimal(okv(row, "quantity", "quantity") or "0") == Decimal("3"), str(row))

# ── Pergerakan stok tercatat & terkalkulasi ───────────────────────────
sc, body = jget("/stock-movements?pageSize=100")
items = body.get("items", [])
pos_mvs = [m for m in items if okv(m, "product_id", "productId") == pid]
chk_mv = next((m for m in pos_mvs if okv(m, "reference_type", "referenceType") == "pos"), None)
check("POS movements tracked", len(pos_mvs) == 3, f"{len(pos_mvs)}")
check("POS movement types", sorted(okv(m, "type", "type") for m in pos_mvs) == ["in", "out", "out"], str([okv(m, "type", "type") for m in pos_mvs]))
check("POS movement reason", (okv(chk_mv, "reason", "reason") or "").startswith("Penjualan POS (POS-"), str(chk_mv))
check("POS movement reference_type", okv(chk_mv, "reference_type", "referenceType") == "pos", str(okv(chk_mv, "reference_type", "referenceType")))

# Jumlah tercatat berurutan (terbaru di depan): checkout(6→3), issue(10→6), receipt(0→10)
seq_ok = True
expected = [("out", "6.00", "3.00"), ("out", "10.00", "6.00"), ("in", "0.00", "10.00")]
for i, (t, bef, aft) in enumerate(expected):
    if not (okv(pos_mvs[i], "type", "type") == t and okv(pos_mvs[i], "before_stock", "beforeStock") == bef and okv(pos_mvs[i], "after_stock", "afterStock") == aft):
        seq_ok = False
        break
check("POS movement chain before/after consistent", seq_ok, str([(okv(m, "type", "type"), okv(m, "before_stock", "beforeStock"), okv(m, "after_stock", "afterStock")) for m in pos_mvs]))

# ── Checkout oleh employee (akses panel workspace/employee) ───────────
TE = login("ani@tokomaju.com", "ani12345")
HE = {"authorization": f"Bearer {TE}"}
sc, body = jpost("/pos/checkout", {
    "items": [{"product_id": pid, "quantity": "1"}],
}, headers=HE)
check("POS checkout by employee 201", sc == 201, f"{sc} {body}")
sc, body = jget("/stock-balances", headers=HE)
row = next((r for r in body if okv(r, "product_id", "productId") == pid), None)
check("POS balance after employee checkout", row is not None and Decimal(okv(row, "quantity", "quantity") or "0") == Decimal("2"), str(row))

# ── Isolasi tenant: produk tenant lain ditolak ────────────────────────
sc, body = jpost("/pos/checkout", {
    "items": [{"product_id": "00000000-0000-0000-0000-000000000000", "quantity": "1"}],
})
check("POS checkout unknown product 404", sc == 404, f"{sc} {body}")

# ── Keranjang kosong / qty nol ditolak ────────────────────────────────
sc, body = jpost("/pos/checkout", {"items": []})
check("POS checkout empty cart 422", sc == 422, f"{sc} {body}")
sc, body = jpost("/pos/checkout", {"items": [{"product_id": pid, "quantity": "0"}]})
check("POS checkout zero qty 422", sc == 422, f"{sc} {body}")

purge_pos_fixtures()

print()
print("ALL POS CHECKS PASS" if ok else "SOME POS CHECKS FAILED")
sys.exit(0 if ok else 1)
