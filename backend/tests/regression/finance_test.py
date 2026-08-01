import sys

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

sc, body = jget("/bank-accounts")
banks = body
seed_banks = [b for b in banks if b["bankName"] in ("BCA", "BNI", "BRI", "Bank Mandiri", "Bank Syariah")]
check("seed banks present", len(seed_banks) == 5, f"{len(seed_banks)}")
check("bank glBalance present", all(b.get("glBalance") for b in seed_banks), str([b.get("glBalance") for b in seed_banks]))
check("bank glBalance numeric", all(Decimal(b["glBalance"]) != 0 for b in seed_banks), str([b["glBalance"] for b in seed_banks]))
check("bank statementCount int", all(isinstance(b.get("statementCount"), int) and b.get("statementCount") >= 0 for b in banks), str([b.get("statementCount") for b in banks]))
check("bank unmatchedCount int", all(isinstance(b.get("unmatchedCount"), int) and b.get("unmatchedCount") >= 0 for b in banks), str([b.get("unmatchedCount") for b in banks]))

# ═══════════════════════════════════════════════════════════════════
#  CASH FLOW — bank accounts must be included
# ═══════════════════════════════════════════════════════════════════

def cash_flow_net():
    sc, body = jget("/reports/cash-flow?startDate=2020-01-01&endDate=2030-12-31")
    assert sc == 200, f"cash-flow {sc}"
    return Decimal(body["summary"]["netCashFlow"]), len(body.get("rows", []))


sc, body = jget("/reports/cash-flow?startDate=2026-01-01&endDate=2026-12-31")
check("cash-flow 200", sc == 200, f"{sc}")
check("cash-flow has rows", len(body.get("rows", [])) > 0, f"{len(body.get('rows', []))} rows")
check("cash-flow summary keys", set(body.get("summary", {})) == {"operating", "investing", "financing", "netCashFlow"}, str(body.get("summary", {})))

s = body.get("summary", {})
check("cash-flow categories sum to net", Decimal(s["operating"]) + Decimal(s["investing"]) + Decimal(s["financing"]) == Decimal(s["netCashFlow"]), str(s))
check("cash-flow rows have type", all(r.get("type") in ("operating", "investing", "financing") for r in body.get("rows", [])), "missing type")
check("cash-flow financing from supplier payments", Decimal(s["financing"]) < 0, str(s["financing"]))

before_net, before_rows = cash_flow_net()

accts = jget("/accounts?pageSize=100")[1]["items"]
bank_mandiri = next(a for a in accts if a["code"] == "1-1004")
expense_acct = next(a for a in accts if a["type"] == "expense")
years_list = jget("/fiscal-years")[1]
open_periods = [p for y in years_list if y.get("status") == "open" for p in y.get("periods", []) if p.get("status") == "open"]
open_periods.sort(key=lambda p: p["startDate"])
check("open period exists", len(open_periods) > 0, f"{len(open_periods)}")
journal_date = open_periods[0]["startDate"][:10] if open_periods else "2026-08-01"
jrn = jpost("/journals", {
    "journalDate": journal_date,
    "reference": "CASHFLOW-TEST",
    "description": "uji cash flow bank",
    "lines": [
        {"accountId": bank_mandiri["id"], "debit": "50000", "credit": "0", "description": "setoran uji"},
        {"accountId": expense_acct["id"], "debit": "0", "credit": "50000", "description": "setoran uji"},
    ],
})
check("journal create 201", jrn[0] == 201, f"{jrn[0]}")
jid = jrn[1].get("id")

sc, body = jpost(f"/journals/{jid}/post")
check("journal post 200", sc == 200, f"{sc}")

after_net, _ = cash_flow_net()
check("cash-flow net +50000 from bank journal", after_net == before_net + Decimal("50000"), f"{before_net} -> {after_net}")

sc, body = jpost(f"/journals/{jid}/reverse")
check("journal reverse 200", sc == 200, f"{sc}")

restored_net, _ = cash_flow_net()
check("cash-flow net restored after reversal", restored_net == before_net, f"{before_net} -> {restored_net}")

# ═══════════════════════════════════════════════════════════════════
#  PROFIT-LOSS MONTHLY
# ═══════════════════════════════════════════════════════════════════

sc, body = jget("/reports/profit-loss-monthly?startDate=2026-01-01&endDate=2026-12-31")
check("profit-loss-monthly 200", sc == 200, f"{sc}")
months = body.get("rows", [])
check("monthly has rows", len(months) > 0, f"{len(months)}")
check("monthly rows sorted asc", all(months[i]["month"] <= months[i + 1]["month"] for i in range(len(months) - 1)), str([m["month"] for m in months]))
monthly_profit = sum(Decimal(m["profit"]) for m in months)
sc, body = jget("/reports/profit-loss?startDate=2026-01-01&endDate=2026-12-31")
annual_profit = Decimal(body["summary"]["netProfit"])
check("monthly profit sums to annual", monthly_profit == annual_profit, f"{monthly_profit} vs {annual_profit}")
sc, body = jget("/reports/profit-loss-monthly?startDate=2026-01-01&endDate=2026-06-01")
check("monthly range respected", all(m["month"] <= "2026-06" for m in body.get("rows", [])), str([m["month"] for m in body.get("rows", [])]))

# ═══════════════════════════════════════════════════════════════════
#  BALANCE-SHEET MONTHLY
# ═══════════════════════════════════════════════════════════════════

sc, body = jget("/reports/balance-sheet-monthly?startDate=2026-01-01&endDate=2026-12-31")
check("balance-sheet-monthly 200", sc == 200, f"{sc}")
bs_months = body.get("rows", [])
check("balance monthly has 12 rows", len(bs_months) == 12, f"{len(bs_months)}")
check("balance monthly sorted asc", all(bs_months[i]["month"] <= bs_months[i + 1]["month"] for i in range(len(bs_months) - 1)), str([m["month"] for m in bs_months]))
last_bs = bs_months[-1]
sc, body = jget("/reports/balance-sheet?startDate=2026-12-31&endDate=2026-12-31")
bs_summary = body["summary"]
check("balance monthly final assets match as-of", Decimal(last_bs["assets"]) == Decimal(bs_summary["totalAssets"]), f"{last_bs['assets']} vs {bs_summary['totalAssets']}")
check("balance monthly final L+E match as-of", Decimal(last_bs["liabilitiesPlusEquity"]) == Decimal(bs_summary["liabilitiesPlusEquity"]), f"{last_bs['liabilitiesPlusEquity']} vs {bs_summary['liabilitiesPlusEquity']}")
sc, body = jget("/reports/balance-sheet-monthly?startDate=2026-07-01&endDate=2026-07-31")
july_rows = body.get("rows", [])
sc, july_asof = jget("/reports/balance-sheet?startDate=2026-07-31&endDate=2026-07-31")
check("balance monthly carries opening balance", len(july_rows) == 1 and Decimal(july_rows[0]["assets"]) == Decimal(july_asof["summary"]["totalAssets"]), str(july_rows))

# ═══════════════════════════════════════════════════════════════════
#  CASH-FLOW MONTHLY
# ═══════════════════════════════════════════════════════════════════

sc, body = jget("/reports/cash-flow-monthly?startDate=2026-01-01&endDate=2026-12-31")
check("cash-flow-monthly 200", sc == 200, f"{sc}")
cf_months = body.get("rows", [])
check("cash-flow monthly has 12 rows", len(cf_months) == 12, f"{len(cf_months)}")
check("cash-flow monthly sorted asc", all(cf_months[i]["month"] <= cf_months[i + 1]["month"] for i in range(len(cf_months) - 1)), str([m["month"] for m in cf_months]))
cf_totals = {
    "operating": sum(Decimal(m["operating"]) for m in cf_months),
    "investing": sum(Decimal(m["investing"]) for m in cf_months),
    "financing": sum(Decimal(m["financing"]) for m in cf_months),
    "net": sum(Decimal(m["net"]) for m in cf_months),
}
sc, body = jget("/reports/cash-flow?startDate=2026-01-01&endDate=2026-12-31")
cf_summary = body["summary"]
check("cash-flow monthly operating sums to annual", cf_totals["operating"] == Decimal(cf_summary["operating"]), f"{cf_totals['operating']} vs {cf_summary['operating']}")
check("cash-flow monthly financing sums to annual", cf_totals["financing"] == Decimal(cf_summary["financing"]), f"{cf_totals['financing']} vs {cf_summary['financing']}")
check("cash-flow monthly net sums to annual", cf_totals["net"] == Decimal(cf_summary["netCashFlow"]), f"{cf_totals['net']} vs {cf_summary['netCashFlow']}")
sc, body = jget("/reports/cash-flow-monthly?startDate=2026-06-01&endDate=2026-06-30")
check("cash-flow monthly range respected", len(body.get("rows", [])) == 1 and body["rows"][0]["month"] == "2026-06", str(body.get("rows", [])))

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

sc, body = jget("/audit-events?objectType=bank_account&pageSize=100")
check("audit filter objectType 200", sc == 200, f"{sc}")
check("audit filter only bank_account", len(body.get("items", [])) > 0 and all(i.get("objectType") == "bank_account" for i in body.get("items", [])), str(set(i.get("objectType") for i in body.get("items", []))))
sc, body = jget("/audit-events?action=fiscal_year.close")
check("audit filter action 200", sc == 200, f"{sc}")
check("audit filter action fiscal_year.close", body.get("total", 0) > 0 and all(i.get("action") == "fiscal_year.close" for i in body.get("items", [])), str(body.get("total")))

purge_fiscal_year()

sc, body = jget(f"/{Y}")
check("FY 2032 purged from list", all(y.get("name") != FY_NAME for y in body))

print()
print("ALL FINANCE CHECKS PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
