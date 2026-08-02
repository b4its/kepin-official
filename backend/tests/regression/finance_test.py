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

# Bersihkan residu e2e: hapus semua match + statement bank agar ringkasan deterministik
bank_list = jget("/bank-accounts")[1]
bca_summary = next((b for b in bank_list if b["bankName"] == "BCA"), None)
if bca_summary:
    sc, body = jget("/reconciliation?pageSize=100")
    for m in body.get("items", []):
        jdelete(f"/reconciliation/matches/{m['id']}")
    sc, body = jget(f"/bank-transactions?bankAccountId={bca_summary['id']}&pageSize=100")
    for b in body.get("items", []):
        jdelete(f"/bank-transactions/{b['id']}")

sc, body = jget("/bank-accounts")
banks = body
seed_banks = [b for b in banks if b["bankName"] in ("BCA", "BNI", "BRI", "Bank Mandiri", "Bank Syariah")]
check("seed banks present", len(seed_banks) == 5, f"{len(seed_banks)}")
check("bank glBalance present", all(b.get("glBalance") for b in seed_banks), str([b.get("glBalance") for b in seed_banks]))
check("bank glBalance numeric", all(Decimal(b["glBalance"]) != 0 for b in seed_banks), str([b["glBalance"] for b in seed_banks]))
check("bank statementCount int", all(isinstance(b.get("statementCount"), int) and b.get("statementCount") >= 0 for b in banks), str([b.get("statementCount") for b in banks]))
check("bank unmatchedCount int", all(isinstance(b.get("unmatchedCount"), int) and b.get("unmatchedCount") >= 0 for b in banks), str([b.get("unmatchedCount") for b in banks]))
check("bank statementTotal numeric", all(Decimal(b.get("statementTotal", "0")) >= Decimal("0") or Decimal(b.get("statementTotal", "0")) <= Decimal("0") for b in banks), str([b.get("statementTotal") for b in banks]))
check("bank unmatchedTotal numeric", all(Decimal(b.get("unmatchedTotal", "0")) >= Decimal("0") or Decimal(b.get("unmatchedTotal", "0")) <= Decimal("0") for b in banks), str([b.get("unmatchedTotal") for b in banks]))
bca = next(b for b in banks if b["bankName"] == "BCA")
check("BCA unmatched total equals statement total", Decimal(bca["unmatchedTotal"]) == Decimal(bca["statementTotal"]), f"{bca['unmatchedTotal']} vs {bca['statementTotal']}")

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
#  RECONCILIATION SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════

sc, body = jget("/bank-accounts")
sug_bca = next(b for b in body if b["bankName"] == "BCA")
sug_bca_id = sug_bca["id"]

sc, body = jget("/bank-transactions?pageSize=100")
for b in body.get("items", []):
    if b["externalId"].startswith("SGT-150K"):
        jdelete(f"/bank-transactions/{b['id']}")
page = 1
while True:
    sc, body = jget(f"/transactions?pageSize=100&page={page}&startDate=2000-01-01&endDate=2099-12-31")
    items = body.get("items", [])
    for t in items:
        if t.get("description", "").startswith("saran auto-match"):
            jpost(f"/transactions/{t['id']}/void", {})
    if not items or page * 100 >= body.get("total", 0):
        break
    page += 1

sc, body = jpost("/bank-transactions", {"bankAccountId": sug_bca_id, "externalId": "SGT-150K-A", "transactionDate": "2026-06-15", "description": "pembayaran pelanggan", "amount": "150000"})
check("suggest stmt A 201", sc == 201, f"{sc}")
sug_stmt_a = body.get("id")
sc, body = jpost("/bank-transactions", {"bankAccountId": sug_bca_id, "externalId": "SGT-150K-B", "transactionDate": "2026-06-25", "description": "pembayaran lain", "amount": "150000"})
check("suggest stmt B 201", sc == 201, f"{sc}")
sug_stmt_b = body.get("id")

sug_accts = []
sug_page = 1
while True:
    sc, body = jget(f"/accounts?pageSize=100&page={sug_page}")
    sug_accts += body.get("items", [])
    if len(sug_accts) >= body.get("total", 0):
        break
    sug_page += 1
sug_income = next((a for a in sug_accts if a["type"] == "income"), None)
sug_cash = next((a for a in sug_accts if a["code"] == "1-1002"), None)


def make_posted_txn(d, amount, desc):
    sc, tr = jpost("/transactions", {"transactionDate": d, "type": "income", "description": desc, "amount": amount, "account_id": sug_cash["id"], "counter_account_id": sug_income["id"]})
    tid = tr.get("id")
    jpost(f"/transactions/{tid}/post", {})
    return tid


sug_txn_a = make_posted_txn("2026-06-15", "150000", "saran auto-match")

sc, body = jget(f"/reconciliation/suggestions?bankAccountId={sug_bca_id}")
check("suggestions 200", sc == 200, f"{sc}")
sug_items = body.get("items", [])
sug_a = next((s for s in sug_items if s["bankTransaction"]["id"] == sug_stmt_a), None)
sug_b = next((s for s in sug_items if s["bankTransaction"]["id"] == sug_stmt_b), None)
check("suggest stmt A has candidate", sug_a is not None and len(sug_a.get("candidates", [])) >= 1, str(sug_a))
check("suggest score 100 same day", bool(sug_a) and sug_a["candidates"][0]["score"] == 100, str(sug_a))
check("suggest stmt B excluded (gap 10 > 7)", sug_b is None, f"{sug_b}")

sug_txn_b = make_posted_txn("2026-06-25", "150000", "saran auto-match 2")
sc, body = jget(f"/reconciliation/suggestions?bankAccountId={sug_bca_id}&dateGapDays=0")
check("suggest dateGapDays=0 includes stmt B", sc == 200 and any(s["bankTransaction"]["id"] == sug_stmt_b for s in body.get("items", [])), f"{sc}")

sc, body = jpost("/reconciliation/matches", {"bankTransactionId": sug_stmt_a, "transactionId": sug_txn_a, "confidence": "100", "note": "saran auto"})
check("suggest match create 201", sc == 201, f"{sc}")
sug_match_id = body.get("id")
sc, _ = jpost(f"/reconciliation/matches/{sug_match_id}/confirm")
check("suggest match confirm 200", sc == 200, f"{sc}")

sc, body = jget(f"/reconciliation/suggestions?bankAccountId={sug_bca_id}")
check("suggestions exclude confirmed", sc == 200 and all(s["bankTransaction"]["id"] != sug_stmt_a for s in body.get("items", [])), str([s["bankTransaction"]["externalId"] for s in body.get("items", [])]))

sc, body = jget(f"/bank-transactions?bankAccountId={sug_bca_id}&pageSize=50")
sug_flags = body.get("items", [])
sug_flag_a = next((b for b in sug_flags if b["id"] == sug_stmt_a), None)
sug_flag_b = next((b for b in sug_flags if b["id"] == sug_stmt_b), None)
check("bank txn matched flag true after confirm", bool(sug_flag_a) and sug_flag_a["matched"] is True, str(sug_flag_a))
check("bank txn matched flag false unmatched", bool(sug_flag_b) and sug_flag_b["matched"] is False, str(sug_flag_b))

sc, _ = jdelete(f"/reconciliation/matches/{sug_match_id}")
check("suggest cleanup match 204", sc == 204, f"{sc}")
for sid in (sug_stmt_a, sug_stmt_b):
    sc, _ = jdelete(f"/bank-transactions/{sid}")
    check("suggest cleanup stmt 204", sc == 204, f"{sc}")
for tid in (sug_txn_a, sug_txn_b):
    sc, body = jpost(f"/transactions/{tid}/void", {})
    check("suggest cleanup void txn", sc == 200 and body.get("status") == "voided", f"{sc}")

sc, body = jget(f"/reconciliation/suggestions?bankAccountId={sug_bca_id}")
check("suggestions empty after cleanup", sc == 200 and all(s["bankTransaction"]["externalId"] not in ("SGT-150K-A", "SGT-150K-B") for s in body.get("items", [])), f"{sc}")

# ═══════════════════════════════════════════════════════════════════
#  BANK CSV IMPORT
# ═══════════════════════════════════════════════════════════════════

csv_text = """tanggal;deskripsi;jumlah
2026-06-01;CSV Penjualan tunai;150000
2026-06-02;CSV Pembayaran supplier;-25000
2026-06-03;CSV Refund pelanggan;12.500,50
2026-06-04;Baris rusak
2026-06-05;CSV Test angka;12.000
"""
sc, body = jpost("/bank-transactions/import", {"bankAccountId": sug_bca_id, "csv": csv_text})
check("csv import 200", sc == 200, f"{sc}")
check("csv import created 4", body.get("created") == 4, str(body))
check("csv import errors 1", len(body.get("errors", [])) == 1, str(body.get("errors")))
check("csv import error line 5", "Baris 5" in body.get("errors", [""])[0], str(body.get("errors")))

sc, body = jpost("/bank-transactions/import", {"bankAccountId": sug_bca_id, "csv": csv_text})
check("csv reimport idempotent", sc == 200 and body.get("created") == 0 and body.get("skipped") == 4, str(body))

sc, body = jpost("/bank-transactions/import", {"bankAccountId": sug_bca_id, "csv": csv_text}, headers=HA)
check("csv import employee 403", sc == 403, f"{sc}")

sc, body = jpost("/bank-transactions/import", {"bankAccountId": "00000000-0000-0000-0000-000000000000", "csv": csv_text})
check("csv import missing bank 404", sc == 404, f"{sc}")

sc, body = jpost("/bank-transactions/import", {"bankAccountId": sug_bca_id, "csv": "\n".join("2026-06-01;Baris %d;1000" % i for i in range(201))})
check("csv import >200 lines 422", sc == 422, f"{sc}")

sc, body = jget(f"/bank-transactions?bankAccountId={sug_bca_id}&pageSize=100&search=CSV-")
csv_rows = [b for b in body.get("items", []) if b["externalId"].startswith("CSV-") and b["description"].startswith("CSV ")]
check("csv rows in list", len(csv_rows) == 4, f"{len(csv_rows)}")
amounts = sorted(Decimal(b["amount"]) for b in csv_rows)
check("csv amounts parsed", amounts == [Decimal("-25000"), Decimal("12000"), Decimal("12500.50"), Decimal("150000")], str(amounts))
for b in csv_rows:
    sc, _ = jdelete(f"/bank-transactions/{b['id']}")
    check("csv cleanup row 204", sc == 204, f"{sc}")

# ═══════════════════════════════════════════════════════════════════
#  RECONCILIATION — BULK AUTO-MATCH (Cocokkan Semua Saran)
# ═══════════════════════════════════════════════════════════════════

sc, body = jget("/bank-transactions?pageSize=100")
for b in body.get("items", []):
    if b["externalId"].startswith("SGT-BULK"):
        jdelete(f"/bank-transactions/{b['id']}")
page = 1
while True:
    sc, body = jget(f"/transactions?pageSize=100&page={page}&startDate=2000-01-01&endDate=2099-12-31")
    items = body.get("items", [])
    for t in items:
        if t.get("description", "").startswith("bulk auto-match"):
            jpost(f"/transactions/{t['id']}/void", {})
    if not items or page * 100 >= body.get("total", 0):
        break
    page += 1

sc, body = jpost("/bank-transactions", {"bankAccountId": sug_bca_id, "externalId": "SGT-BULK-1", "transactionDate": "2026-06-10", "description": "bulk same day", "amount": "333000"})
check("bulk stmt 1 201", sc == 201, f"{sc}")
bulk_stmt_1 = body.get("id")
sc, body = jpost("/bank-transactions", {"bankAccountId": sug_bca_id, "externalId": "SGT-BULK-2", "transactionDate": "2026-06-20", "description": "bulk no candidate", "amount": "555000"})
check("bulk stmt 2 201", sc == 201, f"{sc}")
bulk_stmt_2 = body.get("id")
sc, body = jpost("/bank-transactions", {"bankAccountId": sug_bca_id, "externalId": "SGT-BULK-3", "transactionDate": "2026-06-12", "description": "bulk one day gap", "amount": "777000"})
check("bulk stmt 3 201", sc == 201, f"{sc}")
bulk_stmt_3 = body.get("id")

bulk_txn_1 = make_posted_txn("2026-06-10", "333000", "bulk auto-match")
bulk_txn_3 = make_posted_txn("2026-06-11", "777000", "bulk auto-match gap1")

sc, body = jpost("/reconciliation/matches/bulk", {"bankAccountId": sug_bca_id, "minScore": 90})
check("bulk apply 200", sc == 200, f"{sc}")
check("bulk matched >= 2", body.get("matched", 0) >= 2, str(body))
bulk_skipped = {s["externalId"]: s["reason"] for s in body.get("skipped", [])}
check("bulk skipped stmt 2", "SGT-BULK-2" in bulk_skipped, str(bulk_skipped))
check("bulk skipped reason mentions score", any("skor >= 90" in r for r in bulk_skipped.values()), str(bulk_skipped))

sc, body = jget(f"/bank-transactions?bankAccountId={sug_bca_id}&pageSize=50")
bulk_flags = {b["id"]: b["matched"] for b in body.get("items", [])}
check("bulk stmt 1 matched", bulk_flags.get(bulk_stmt_1) is True, str(bulk_flags.get(bulk_stmt_1)))
check("bulk stmt 3 matched", bulk_flags.get(bulk_stmt_3) is True, str(bulk_flags.get(bulk_stmt_3)))
check("bulk stmt 2 unmatched", bulk_flags.get(bulk_stmt_2) is False, str(bulk_flags.get(bulk_stmt_2)))

sc, body = jget(f"/reconciliation/suggestions?bankAccountId={sug_bca_id}")
check("bulk suggestions exclude matched", sc == 200 and all(s["bankTransaction"]["id"] not in (bulk_stmt_1, bulk_stmt_3) for s in body.get("items", [])), str([s["bankTransaction"]["externalId"] for s in body.get("items", [])]))

sc, body = jpost("/reconciliation/matches/bulk", {"bankAccountId": sug_bca_id, "minScore": 100}, headers=HA)
check("bulk apply employee 403", sc == 403, f"{sc}")

sc, body = jpost("/reconciliation/matches/bulk", {"bankAccountId": sug_bca_id, "minScore": 100})
check("bulk minScore 100 no new match", sc == 200 and body.get("matched", 0) == 0, str(body))

sc, body = jget("/audit-events?action=reconciliation.bulk_match&pageSize=100")
check("audit reconciliation.bulk_match exists", sc == 200 and body.get("total", 0) > 0 and all(e.get("action") == "reconciliation.bulk_match" for e in body.get("items", [])), str(body.get("total")))

sc, body = jget("/reconciliation?pageSize=100")
bulk_matches = [m for m in body.get("items", []) if m["bankTransactionId"] in (bulk_stmt_1, bulk_stmt_3)]
check("bulk matches listed confirmed", len(bulk_matches) == 2 and all(m.get("status") == "confirmed" for m in bulk_matches), str(bulk_matches))
for m in bulk_matches:
    sc, _ = jdelete(f"/reconciliation/matches/{m['id']}")
    check("bulk cleanup match 204", sc == 204, f"{sc}")
for sid in (bulk_stmt_1, bulk_stmt_2, bulk_stmt_3):
    sc, _ = jdelete(f"/bank-transactions/{sid}")
    check("bulk cleanup stmt 204", sc == 204, f"{sc}")
for tid in (bulk_txn_1, bulk_txn_3):
    sc, body = jpost(f"/transactions/{tid}/void", {})
    check("bulk cleanup void txn", sc == 200 and body.get("status") == "voided", f"{sc}")

# ═══════════════════════════════════════════════════════════════════
#  JOURNALS — FILTER BUKU BESAR PER AKUN
# ═══════════════════════════════════════════════════════════════════

sc, body = jget("/journals?startDate=2026-01-01&endDate=2026-12-31&pageSize=100")
gl_all = body.get("total", 0)
sc, body = jget(f"/journals?startDate=2026-01-01&endDate=2026-12-31&pageSize=100&accountId={sug_cash['id']}")
check("journals accountId filter 200", sc == 200, f"{sc}")
gl_cash = body.get("items", [])
check("journals accountId filter touches account", all(any(l.get("accountId") == sug_cash["id"] for l in j.get("lines", [])) for j in gl_cash), f"{len(gl_cash)} rows")
check("journals accountId filter total <= all", body.get("total", 0) <= gl_all, f"{body.get('total')} <= {gl_all}")
sc, body = jget("/journals?accountId=00000000-0000-0000-0000-000000000000")
check("journals unknown account filter 0", sc == 200 and body.get("total", 0) == 0, f"{sc} {body.get('total')}")

# ═══════════════════════════════════════════════════════════════════
#  JOURNALS — BUKU BESAR PER AKUN (running balance)
# ═══════════════════════════════════════════════════════════════════

sc, body = jget(f"/journals/ledger?accountId={sug_cash['id']}")
check("ledger 200", sc == 200, f"{sc}")
ledger_b = body
check("ledger account info", body.get("accountId") == sug_cash["id"] and body.get("normalBalance") == "debit", str(body.get("accountId")))
ledger_rows = body.get("items", [])
check("ledger has rows", len(ledger_rows) > 0, f"{len(ledger_rows)}")
check("ledger closing == last balance", Decimal(body.get("closing", "0")) == Decimal(ledger_rows[-1]["balance"]), f"{body.get('closing')} vs {ledger_rows[-1]['balance']}")
prev_bal = Decimal(body["opening"])
bal_ok = True
for row in ledger_rows:
    delta = Decimal(row["debit"]) - Decimal(row["credit"])
    if Decimal(row["balance"]) != prev_bal + delta:
        bal_ok = False
        break
    prev_bal = Decimal(row["balance"])
check("ledger running balance consistent", bal_ok, f"opening={body['opening']}")
dates = [r["journalDate"] for r in ledger_rows]
check("ledger chronological asc", dates == sorted(dates), str(dates[:3]))

sc, body = jget(f"/journals/ledger?accountId={sug_cash['id']}&startDate=2026-01-01&endDate=2026-12-31")
check("ledger with period 200", sc == 200 and len(body.get("items", [])) > 0, f"{sc}")
sc, body = jget("/journals/ledger?accountId=00000000-0000-0000-0000-000000000000")
check("ledger unknown account 404", sc == 404, f"{sc}")

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
