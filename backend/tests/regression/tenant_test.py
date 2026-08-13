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


def login(email, pw):
    r = C.post("/auth/login", json={"email": email, "password": pw})
    return r.json().get("access_token", "")


T = login("budi@tokomaju.com", "budi123")
A = login("ani@tokomaju.com", "ani12345")
H = {"authorization": f"Bearer {T}"}
HA = {"authorization": f"Bearer {A}"}
S = "toko-maju"

import uuid

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
    return r.status_code, (r.json() if r.status_code != 204 else {})

def jdel(path, headers=H):
    r = C.delete(f"/tenants/{S}{path}", headers=headers)
    return r.status_code, (r.json() if r.content else {})

# ── read-only basics ──
c, b = jget("/context"); check("context", c == 200 and b.get("tenant") is not None, f"({c})")
c, b = jget("/organization"); check("organization", c == 200 and b.get("legalName") is not None, f"({c})")
c, b = jget("/sidebar-settings"); check("sidebar-settings", c == 200, f"({c})")
c, b = jput_sidebar if False else (None, None)
r = C.put(f"/tenants/{S}/sidebar-settings", json={"sections": []}, headers=H)
check("sidebar-settings PUT", r.status_code == 200, f"({r.status_code})")
c, b = jget("/roles"); check("roles", c == 200, f"({c})")
c, b = jget("/members"); check("members", c == 200 and len(b) >= 2, f"({c})")
c, b = jget("/billing"); check("billing", c == 200 and b.get("planCode") is not None, f"({c})")
c, b = jget("/billing-history"); check("billing-history", c == 200 and len(b) >= 1, f"({c})")
c, b = jget("/dashboard?period=30d"); check("dashboard", c == 200 and "metrics" in b, f"({c})")
c, b = jget("/notifications"); check("notifications", c == 200, f"({c})")
c, b = jget("/audit-events"); check("audit-events", c == 200 and "items" in b, f"({c})")
c, b = jget("/bank-accounts"); check("bank-accounts", c == 200 and isinstance(b, list), f"({c})")
c, b = jget("/bank-transactions"); check("bank-transactions", c == 200 and "items" in b, f"({c})")
c, b = jget("/integrations"); check("integrations", c == 200 and isinstance(b, list), f"({c})")
c, b = jget("/fiscal-years"); check("fiscal-years", c == 200, f"({c})")
c, b = jget("/inventory-locations"); check("inventory-locations", c == 200 and len(b) >= 1, f"({c})")
c, b = jget("/accounts"); check("accounts", c == 200 and len(b.get("items", [])) >= 5, f"({c})")
c, b = jget("/branches"); check("branches", c == 200 and len(b) >= 1, f"({c})")
c, b = jget("/customers"); check("customers", c == 200, f"({c})")
c, b = jget("/suppliers"); check("suppliers", c == 200, f"({c})")
c, b = jget("/products"); check("products", c == 200, f"({c})")
c, b = jget("/journals?page=1&pageSize=5"); check("journals", c == 200 and "items" in b, f"({c})")
c, b = jget("/transactions?page=1&pageSize=5"); check("transactions", c == 200 and "items" in b, f"({c})")
c, b = jget("/customers?pageSize=100"); cust_real = b["items"][0] if b.get("items") else None
c, b = jget("/suppliers?pageSize=100"); sup_real = b["items"][0] if b.get("items") else None
c, b = jget("/invoices?page=1&pageSize=5"); check("invoices", c == 200 and "items" in b, f"({c})")
c, b = jget("/purchase-orders?page=1&pageSize=5"); check("purchase-orders", c == 200 and "items" in b, f"({c})")
c, b = jget("/supplier-payments"); check("supplier-payments", c == 200 and "items" in b, f"({c})")
c, b = jget("/customer-payments"); check("customer-payments", c == 200 and "items" in b, f"({c})")
c, b = jget("/reconciliation"); check("reconciliation", c == 200, f"({c})")
c, b = jget("/stock-balances"); check("stock-balances", c == 200 and isinstance(b, list), f"({c})")
c, b = jget("/stock-movements"); check("stock-movements", c == 200 and "items" in b, f"({c})")

for rep in ["summary", "profit-loss", "balance-sheet", "cash-flow", "trial-balance", "general-ledger", "receivable-aging", "payable-aging", "stock-valuation", "investor"]:
    c, b = jget(f"/reports/{rep}?preset=30d")
    check(f"report {rep}", c == 200 and (b.get("status") in (None, "ok") or "items" in b or isinstance(b, dict)), f"({c})")

# ── employee RBAC negatives ──
r = C.post(f"/tenants/{S}/journals", json={"journal_date": "2026-07-01", "description": "x", "lines": []}, headers=HA)
check("employee cannot create journal", r.status_code in (403, 422), f"({r.status_code})")

# ── customer CRUD (tmp) ──
rid = str(uuid.uuid4())[:8]
c, b = jpost("/customers", {"code": f"TMPC-{rid}", "name": f"Tmp Cust {rid}", "email": f"tmp{rid}@x.com", "address": "Jkt", "phone": "0812"})
cust_id = b.get("id", "")
check("customer create", c == 201 and cust_id, f"({c})")
c, b = jpatch(f"/customers/{cust_id}", {"name": f"Tmp Cust {rid} U"})
check("customer patch", c == 200 and b.get("name", "").endswith("U"), f"({c})")
c, b = jdel(f"/customers/{cust_id}")
check("customer delete", c == 204, f"({c})")

# ── supplier CRUD (tmp) ──
c, b = jpost("/suppliers", {"code": f"TMPS-{rid}", "name": f"Tmp Sup {rid}", "contact_person": "A", "phone": "0813", "email": f"sup{rid}@x.com", "address": "Jkt"})
sup_id = b.get("id", "")
check("supplier create", c == 201 and sup_id, f"({c})")
c, b = jpatch(f"/suppliers/{sup_id}", {"name": f"Tmp Sup {rid} U"})
check("supplier patch", c == 200, f"({c})")
c, b = jdel(f"/suppliers/{sup_id}")
check("supplier delete", c == 204, f"({c})")

# ── product CRUD (tmp) ──
c, b = jpost("/products", {"sku": f"TMPSKU-{rid}", "name": f"Tmp Prod {rid}", "unit": "pcs", "category": "TMP", "price": 10000, "cost": 5000})
prod_id = b.get("id", "")
check("product create", c == 201 and prod_id, f"({c})")
c, b = jpatch(f"/products/{prod_id}", {"name": f"Tmp Prod {rid} U"})
check("product patch", c == 200, f"({c})")
c, b = jdel(f"/products/{prod_id}")
check("product delete", c == 204, f"({c})")

# ── branch CRUD (tmp) ──
c, b = jpost("/branches", {"name": f"Tmp Cabang {rid}", "code": f"TMPB-{rid}", "address": "Bekasi"})
branch_id = b.get("id", "")
check("branch create", c == 201 and branch_id, f"({c})")
c, b = jpatch(f"/branches/{branch_id}", {"name": f"Tmp Cabang {rid} U"})
check("branch patch", c == 200, f"({c})")
c, b = jdel(f"/branches/{branch_id}")
check("branch delete", c == 204, f"({c})")

# ── bank account (tmp, cleaned up) ──
def acct(code):
    return jget(f"/accounts?search={code}&pageSize=100")[1]["items"][0]

asset_acct = acct("1-1002")
c, b = jpost("/bank-accounts", {"account_id": asset_acct["id"], "bank_name": f"TMP Bank {rid}", "masked_number": f"****{rid[-4:]}", "account_holder": "Budi"})
check("bank-account create", c == 201, f"({c})")
c, _ = jdelete(f"/bank-accounts/{b['id']}")
check("bank-account delete cleanup", c == 204, f"({c})")

# ── journal draft → post → reverse (tmp, GL-true) ──
cash = acct("1-1002")
revenue = acct("4-1001")
today = "2026-08-01"
c, b = jpost("/journals", {"journal_date": today, "reference": f"TMPJ-{rid}", "description": "tmp sweep", "lines": [
    {"account_id": cash["id"], "debit": "1000", "credit": "0"},
    {"account_id": revenue["id"], "debit": "0", "credit": "1000"},
]})
j_id = b.get("id", "")
check("journal create", c == 201 and j_id, f"({c}) {b.get('message') if isinstance(b, dict) else ''}")
c, b = jpost(f"/journals/{j_id}/post")
check("journal post", c == 200, f"({c}) {b.get('message') if isinstance(b, dict) else ''}")
c, b = jget(f"/journals/{j_id}")
check("journal posted status", c == 200 and b.get("status") == "posted", f"({c}) {b.get('status')}")
c, b = jpost(f"/journals/{j_id}/reverse")
check("journal reverse", c == 200, f"({c}) {b.get('message') if isinstance(b, dict) else ''}")
c, b = jget(f"/journals/{j_id}")
check("journal reversed status", c == 200 and b.get("status") == "reversed", f"({c}) {b.get('status')}")

# ── transaction create → post → void (tmp) ──
c, b = jpost("/transactions", {"transaction_date": today, "reference": f"TMPT-{rid}", "description": "tmp sweep", "type": "expense", "amount": "500", "account_id": cash["id"], "counter_account_id": revenue["id"]})
tx_id = b.get("id", "")
check("transaction create", c == 201 and tx_id, f"({c})")
c, b = jpost(f"/transactions/{tx_id}/post")
check("transaction post", c == 200, f"({c}) {b.get('message') if isinstance(b, dict) else ''}")
c, b = jpost(f"/transactions/{tx_id}/void")
check("transaction void", c == 200, f"({c}) {b.get('message') if isinstance(b, dict) else ''}")

# ── invoice draft → send → cancel (no post → no GL) ──
c, b = jpost("/invoices", {"invoice_date": today, "due_date": "2026-08-15", "customer_id": cust_real["id"] if cust_real else "", "notes": "tmp", "lines": [{"item_name": "Tmp item", "quantity": "1", "unit_price": "1000", "tax_rate": "0", "discount_amount": "0"}]})
inv_id = b.get("id", "")
check("invoice create", c == 201 and inv_id, f"({c}) {str(b)[:150]}")
c, b = jpost(f"/invoices/{inv_id}/send")
check("invoice send", c == 200, f"({c}) {str(b)[:120]}")
c, b = jpost(f"/invoices/{inv_id}/cancel")
check("invoice cancel", c == 200, f"({c}) {str(b)[:120]}")

# ── purchase order create → send → cancel (no receive → no stock/GL) ──
c, b = jpost("/purchase-orders", {"order_date": today, "expected_date": "2026-08-20", "supplier_id": sup_real["id"] if sup_real else "", "notes": "tmp", "lines": [{"item_name": "Tmp po item", "quantity": "1", "unit_price": "1000", "tax_rate": "0", "discount_amount": "0"}]})
po_id = b.get("id", "")
check("po create", c == 201 and po_id, f"({c}) {str(b)[:150]}")
c, b = jpost(f"/purchase-orders/{po_id}/send")
check("po send", c == 200, f"({c}) {str(b)[:120]}")
c, b = jpost(f"/purchase-orders/{po_id}/cancel")
check("po cancel", c == 200, f"({c}) {str(b)[:120]}")

# ── supplier payment: create from tmp po? use direct create → post → void ──
c, b = jpost("/supplier-payments", {"payment_date": today, "reference": f"TMPP-{rid}", "supplier_id": sup_real["id"] if sup_real else "", "amount": "1000", "method": "transfer_bank"})
sp_id = b.get("id", "")
check("supplier-payment create", c == 201 and sp_id, f"({c}) {str(b)[:150]}")
c, b = jpost(f"/supplier-payments/{sp_id}/post")
check("supplier-payment post", c == 200, f"({c}) {str(b)[:150]}")
c, b = jpost(f"/supplier-payments/{sp_id}/void")
check("supplier-payment void", c == 200, f"({c}) {str(b)[:150]}")

# ── customer payment: create → post → void ──
c, b = jpost("/customer-payments", {"payment_date": today, "reference": f"TMPCP-{rid}", "customer_id": cust_real["id"] if cust_real else "", "amount": "1000", "method": "cash"})
cp_id = b.get("id", "")
check("customer-payment create", c == 201 and cp_id, f"({c}) {str(b)[:150]}")
c, b = jpost(f"/customer-payments/{cp_id}/post")
check("customer-payment post", c == 200, f"({c}) {str(b)[:150]}")
c, b = jpost(f"/customer-payments/{cp_id}/void")
check("customer-payment void", c == 200, f"({c}) {str(b)[:150]}")

# ── reconciliation matches ──
c, b = jget("/reconciliation")
matches = b.get("matches", []) if isinstance(b, dict) else []
check("reconciliation matches listable", c == 200 and isinstance(matches, list), f"({c})")
if matches:
    m0 = matches[0]
    c, b = jpost(f"/reconciliation/matches/{m0['id']}/confirm")
    check("match confirm", c in (200, 409, 422), f"({c})")

# ── periods close/reopen on an OPEN period ──
c, b = jget("/fiscal-years")
fys = b if isinstance(b, list) else []
open_period = None
for fy in fys:
    for p in fy.get("periods", []):
        if p.get("status") == "open":
            open_period = p
            break
    if open_period:
        break
if open_period:
    c, b = jpost(f"/periods/{open_period['id']}/close")
    check("period close", c == 200, f"({c}) {str(b)[:120]}")
    c, b = jpost(f"/periods/{open_period['id']}/reopen")
    check("period reopen", c == 200, f"({c}) {str(b)[:120]}")
else:
    check("period close/reopen", False, "no open period found")

# ── employee read-only ok ──
c, b = jget("/context", headers=HA)
check("employee context ok", c == 200, f"({c})")

# ── join code: tenant-scoped, owner/admin only ──
c, b = jget("/join-code")
code = b.get("joinCode", "") if isinstance(b, dict) else ""
check("join-code owner GET", c == 200 and len(code) >= 8, f"({c}) code={code!r}")
c, b = jpost("/join-code/regenerate")
new_code = b.get("joinCode", "") if isinstance(b, dict) else ""
check("join-code owner regenerate", c == 200 and len(new_code) >= 8, f"({c})")
check("join-code regenerated differs", bool(new_code) and new_code != code, f"({new_code!r})")
r = C.get(f"/auth/join-info?code={new_code}")
check("join-info accepts new code", r.status_code == 200 and r.json().get("tenant", {}).get("slug") == S, f"({r.status_code})")
c, b = jget("/join-code", headers=HA)
check("join-code employee forbidden", c == 403, f"({c})")
c, b = jpost("/join-code/regenerate", headers=HA)
check("join-code regenerate employee forbidden", c == 403, f"({c})")

# ── single-company: anggota satu perusahaan tidak bisa bergabung ke yang lain ──
siti_login = C.post("/auth/login", json={"email": "siti@warungsegar.com", "password": "siti123"}).json()
warung_code = siti_login["tenants"][0]["joinCode"]
r = C.post("/auth/join-by-code", json={"join_code": warung_code}, headers=HA)
check("member cannot join other company", r.status_code == 409 and r.json().get("code") == "ALREADY_IN_COMPANY", f"({r.status_code})")

# ── leave company (non-owner) dengan user throwaway ──
r = C.post(f"/tenants/{S}/membership/leave", headers=H)
check("owner cannot leave company", r.status_code == 400, f"({r.status_code})")
rid2 = str(uuid.uuid4())[:8]
email2 = f"leavetest{rid2}@x.com"
C.post("/auth/register", json={"name": "Leave Test", "email": email2, "password": "leavetest123"})
LE = login(email2, "leavetest123")
HLE = {"authorization": f"Bearer {LE}"}
budi_login = C.post("/auth/login", json={"email": "budi@tokomaju.com", "password": "budi123"}).json()
toko_code = budi_login["tenants"][0]["joinCode"]
r = C.post("/auth/join-by-code", json={"join_code": toko_code}, headers=HLE)
check("throwaway joins toko-maju", r.status_code == 200, f"({r.status_code})")
r = C.post("/auth/join-by-code", json={"join_code": warung_code}, headers=HLE)
check("throwaway blocked from second company", r.status_code == 409, f"({r.status_code})")
r = C.post(f"/tenants/{S}/membership/leave", headers=HLE)
check("throwaway leaves company", r.status_code == 200, f"({r.status_code})")
r = C.get(f"/tenants/{S}/context", headers=HLE)
check("throwaway context forbidden after leave", r.status_code == 403, f"({r.status_code})")
r = C.post("/auth/join-by-code", json={"join_code": warung_code}, headers=HLE)
check("throwaway can join other company after leave", r.status_code == 200, f"({r.status_code})")
r = C.post("/tenants/warung-segar/membership/leave", headers=HLE)
check("throwaway leaves warung-segar (cleanup)", r.status_code == 200, f"({r.status_code})")

print("\n" + ("ALL TENANT CHECKS PASS" if ok else "SOME CHECKS FAILED"))
sys.exit(0 if ok else 1)
