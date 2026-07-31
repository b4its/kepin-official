import sys

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=15)

ok = True


def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def post(path, payload, token=None):
    h = {"content-type": "application/json"}
    if token:
        h["authorization"] = f"Bearer {token}"
    r = C.post(path, json=payload, headers=h)
    return r.status_code, r.json()


def get(path, token):
    r = C.get(path, headers={"authorization": f"Bearer {token}"})
    return r.status_code, r.json()


def delete(path, token):
    r = C.delete(path, headers={"authorization": f"Bearer {token}"})
    return r.status_code, r.json() if r.content else {}


code, body = post("/auth/login", {"email": "admin@kepin.io", "password": "admin123"})
check("superadmin login", code == 200 and body.get("access_token"), f"({code})")
T = body["access_token"]

import time
ts = int(time.time())

code, body = post("/platform/tenants", {
    "name": f"E2E Admin {ts}", "slug": f"e2e-admin-{ts}", "sector": "Ritel",
    "timezone": "Asia/Jakarta", "currency": "IDR",
}, T)
check("create tenant works", code == 201 and body.get("id"), f"({code})")
tid = body.get("id", "")

code, body = post("/platform/tenants", {
    "name": "Dup", "slug": f"e2e-admin-{ts}", "sector": "Ritel",
}, T)
check("duplicate slug rejected", code == 409, f"({code})")

code, body = post(f"/platform/tenants/{tid}/suspend", {}, T)
check("suspend works", code == 200 and body.get("status") == "suspended", f"({code})")

code, body = post(f"/platform/tenants/{tid}/reactivate", {}, T)
check("reactivate works", code == 200 and body.get("status") == "active", f"({code})")

code, body = post("/platform/incidents", {"title": f"E2E Incident {ts}", "description": "test", "severity": "info"}, T)
check("create incident works", code == 201 and body.get("id"), f"({code})")
iid = body.get("id", "")
code, _ = delete(f"/platform/incidents/{iid}", T) if False else (0, {})
code, body = post(f"/platform/incidents/{iid}/close", {}, T) if False else (code, body)

code, body = post("/platform/users", {"name": f"E2E User {ts}", "email": f"e2e-{ts}@example.com", "password": "rahasia123"}, T)
check("create user works", code == 201 and body.get("id"), f"({code})")
uid = body.get("id", "")

code, body = delete(f"/platform/users/{uid}", T)
check("delete user works", code == 204, f"({code})")

code, body = delete(f"/platform/tenants/{tid}", T)
check("delete tenant works (full cascade)", code == 204, f"({code})")

code, body = get(f"/platform/tenants?search=e2e-admin-{ts}", T)
check("tenant really gone", code == 200 and len(body.get("items", [])) == 0, f"({code})")

print("\n" + ("ALL ADMIN CHECKS PASS" if ok else "SOME CHECKS FAILED"))
sys.exit(0 if ok else 1)
