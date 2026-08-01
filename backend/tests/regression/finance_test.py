import sys

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=30)

ok = True


def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


FY_NAME = "Tahun Buku 2032"


def purge_fiscal_year():
    import asyncio

    from sqlalchemy import delete, select

    from kepin.db.session import get_session
    from kepin.db.models import AccountingPeriod, FiscalYear, Tenant

    async def _purge():
        async for s in get_session():
            tenant = (
                await s.execute(select(Tenant).where(Tenant.slug == "toko-maju"))
            ).scalar_one()
            fids = (
                await s.execute(
                    select(FiscalYear.id).where(
                        FiscalYear.tenant_id == str(tenant.id),
                        FiscalYear.name == FY_NAME,
                    )
                )
            ).scalars().all()
            for fid in fids:
                await s.execute(
                    delete(AccountingPeriod).where(AccountingPeriod.fiscal_year_id == fid)
                )
                await s.execute(delete(FiscalYear).where(FiscalYear.id == fid))
            await s.commit()

    asyncio.run(_purge())


purge_fiscal_year()


def login(email, pw):
    r = C.post("/auth/login", json={"email": email, "password": pw})
    return r.json().get("access_token", "")


T = login("budi@tokomaju.com", "budi123")
A = login("ani@tokomaju.com", "ani12345")
H = {"authorization": f"Bearer {T}"}
HA = {"authorization": f"Bearer {A}"}
S = "toko-maju"


def jget(path, headers=H):
    r = C.get(f"/tenants/{S}{path}", headers=headers)
    return r.status_code, r.json()


def jpost(path, payload=None, headers=H):
    r = C.post(f"/tenants/{S}{path}", json=payload or {}, headers=headers)
    try:
        b = r.json()
    except Exception:
        b = {}
    return r.status_code, b


def jpatch(path, payload, headers=H):
    r = C.patch(f"/tenants/{S}{path}", json=payload, headers=headers)
    try:
        b = r.json()
    except Exception:
        b = {}
    return r.status_code, b


def jdelete(path, headers=H):
    r = C.delete(f"/tenants/{S}{path}", headers=headers)
    return r.status_code, r.text


# ═══════════════════════════════════════════════════════════════════
#  FISCAL YEAR LIFECYCLE
# ═══════════════════════════════════════════════════════════════════

Y = "fiscal-years"

sc, body = jget(f"/{Y}")
check("fiscal-years list 200", sc == 200, f"{sc}")
before = len(body)

sc, body = jpost(f"/{Y}", {"start_date": "2032-01-01", "end_date": "2032-12-31"})
check("create FY 2032 201", sc == 201, f"{sc}")
check("FY auto name", body.get("name") == FY_NAME, body.get("name"))
check("FY has 12 periods", len(body.get("periods", [])) == 12)
check("first period Periode 2032-01", body.get("periods", [{}])[0].get("name") == "Periode 2032-01")
check("last period ends 2032-12-31", body.get("periods", [{}])[-1].get("endDate") == "2032-12-31")
check("all periods open", all(p.get("status") == "open" for p in body.get("periods", [])))
fy_id = body.get("id")
check("FY id present", bool(fy_id))

sc, body = jpost(f"/{Y}", {"start_date": "2032-06-01", "end_date": "2033-05-31"})
check("overlap rejected 409", sc == 409, f"{sc}")

sc, body = jpost(f"/{Y}", {"start_date": "2033-01-01", "end_date": "2033-12-31", "name": "Tahun Buku 2032"})
check("duplicate name rejected 409", sc == 409, f"{sc}")

sc, body = jpost(f"/{Y}", {"start_date": "2034-12-31", "end_date": "2034-01-01"})
check("start>end rejected 422", sc == 422, f"{sc}")

sc, body = jpost(f"/{Y}", {"start_date": "2032-01-01", "end_date": "2032-12-31"}, headers=HA)
check("create FY as employee 403", sc == 403, f"{sc}")

sc, body = jpost(f"/{Y}/{fy_id}/close")
check("close FY with open periods 422", sc == 422, f"{sc}")
check("close msg lists periods", "Periode 2032-01" in body.get("message", ""), body.get("message"))

sc, body = jpost(f"/{Y}/{fy_id}/reopen")
check("reopen open FY 422", sc == 422, f"{sc}")

# tutup semua periode dulu, lalu tutup FY
periods = jget(f"/{Y}")[1]
periods = next(y for y in periods if y.get("id") == fy_id)["periods"]
for p in periods:
    sc, _ = jpost(f"/periods/{p['id']}/close")
    assert sc in (200, 422), f"close period {p['name']} -> {sc}"

sc, body = jpost(f"/{Y}/{fy_id}/close")
check("close FY after all periods closed 200", sc == 200, f"{sc}")
check("FY status closed", body.get("status") == "closed")

sc, body = jpost(f"/{Y}/{fy_id}/close")
check("close closed FY 422", sc == 422, f"{sc}")

sc, body = jpost(f"/{Y}/{fy_id}/reopen")
check("reopen closed FY 200", sc == 200, f"{sc}")
check("FY status open again", body.get("status") == "open")

sc, body = jget(f"/{Y}")
check("list count incremented", len(body) == before + 1, f"{before} -> {len(body)}")

# ═══════════════════════════════════════════════════════════════════
#  BANK ACCOUNT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

accts = jget("/accounts")[1]["items"]
cash = next(a for a in accts if a["code"] == "1-1002")
bank_count = len(jget("/bank-accounts")[1])

sc, body = jpost("/bank-accounts", {"accountId": cash["id"], "bankName": "Bank Uji Finance", "maskedNumber": "**** 7001"}, headers=HA)
check("create bank as employee 403", sc == 403, f"{sc}")

sc, body = jpost("/bank-accounts", {"accountId": cash["id"], "bankName": "Bank Uji Finance"})
check("create bank 201", sc == 201, f"{sc}")
bid = body.get("id")
check("bank id present", bool(bid))

sc, body = jpatch(f"/bank-accounts/{bid}", {"bankName": "Bank Uji Finance 2", "status": "inactive"})
check("patch bank 200", sc == 200, f"{sc}")
check("patched name", body.get("bankName") == "Bank Uji Finance 2")
check("patched status", body.get("status") == "inactive")

sc, body = jpatch(f"/bank-accounts/{bid}", {"bankName": "  "})
check("patch empty name 422", sc == 422, f"{sc}")

sc, body = jpatch(f"/bank-accounts/{bid}", {"status": "bogus"})
check("patch bad status 422", sc == 422, f"{sc}")

sc, body = jpatch(f"/bank-accounts/{bid}", {"bankName": "Bank Uji Finance 2", "status": "active"}, headers=HA)
check("patch bank as employee 403", sc == 403, f"{sc}")

sc, body = jpatch(f"/bank-accounts/{bid}", {"status": "active"})
check("re-activate bank as owner 200", sc == 200, f"{sc}")

sc, body = jpost("/bank-transactions", {"bankAccountId": bid, "externalId": "FINUJI-1", "transactionDate": "2032-02-03", "description": "uji finance", "amount": "75000"})
check("create bank txn 201", sc == 201, f"{sc}")
txn1_id = body.get("id")

sc, _ = jdelete(f"/bank-accounts/{bid}")
check("delete bank with txn 409", sc == 409, f"{sc}")

sc, _ = jdelete(f"/bank-transactions/{txn1_id}")
check("delete first bank txn 204", sc == 204, f"{sc}")

sc, body = jpost("/bank-transactions", {"bankAccountId": bid, "externalId": "FINUJI-DEL", "transactionDate": "2032-02-03", "description": "hapus", "amount": "10000"})
check("second bank txn 201", sc == 201, f"{sc}")
txn_id = body.get("id")

sc, _ = jdelete(f"/bank-transactions/{txn_id}")
check("delete bank txn 204", sc == 204, f"{sc}")

sc, body = jpost("/bank-transactions", {"bankAccountId": bid, "externalId": "FINUJI-DEL", "transactionDate": "2032-02-03", "description": "hapus", "amount": "10000"})
check("external id reusable after delete 201", sc == 201, f"{sc}")
txn_id = body.get("id")
sc, _ = jdelete(f"/bank-transactions/{txn_id}")
check("cleanup second txn 204", sc == 204, f"{sc}")

sc, _ = jdelete(f"/bank-accounts/{bid}")
check("delete bank after txns removed 204", sc == 204, f"{sc}")

sc, body = jdelete("/bank-accounts/00000000-0000-0000-0000-000000000000")
check("delete missing bank 404", sc == 404, f"{sc}")

check("bank count restored", len(jget("/bank-accounts")[1]) == bank_count, f"{bank_count}")

# ═══════════════════════════════════════════════════════════════════
#  CLEANUP: FY 2032 + audit trail
# ═══════════════════════════════════════════════════════════════════

sc, body = jget(f"/{Y}")
fy2032 = next((y for y in body if y.get("id") == fy_id), None)
check("FY 2032 still listed", fy2032 is not None)
for p in fy2032["periods"]:
    sc, _ = jpost(f"/periods/{p['id']}/close")

sc, body = jpost(f"/{Y}/{fy_id}/close")
check("re-close FY 2032 200", sc == 200, f"{sc}")

sc, body = jget("/audit-events?pageSize=100")
evts = body.get("items", [])
fy_events = [e for e in evts if e.get("objectType") == "fiscal_year" and e.get("objectId") == fy_id]
actions = sorted(e.get("action") for e in fy_events)
check("audit fiscal_year.create", "fiscal_year.create" in actions, str(actions))
check("audit fiscal_year.close", "fiscal_year.close" in actions, str(actions))
check("audit fiscal_year.reopen", "fiscal_year.reopen" in actions, str(actions))
bank_events = [e for e in evts if e.get("objectType") == "bank_account"]
bactions = sorted(e.get("action") for e in bank_events)
check("audit bank_account.update", "bank_account.update" in bactions, str(bactions))
check("audit bank_account.delete", "bank_account.delete" in bactions, str(bactions))

purge_fiscal_year()

sc, body = jget(f"/{Y}")
check("FY 2032 purged from list", all(y.get("name") != FY_NAME for y in body))

print()
print("ALL FINANCE CHECKS PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
