import sys

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=10)

ok = True


def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def post(path, payload, token=None):
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    r = C.post(path, json=payload, headers=headers)
    return r.status_code, r.json()


EMAIL = "ani@tokomaju.com"
CURRENT = "ani12345"

code, body = post("/auth/login", {"email": EMAIL, "password": CURRENT})
check("login with current password", code == 200 and body.get("access_token"), f"({code})")
token = body["access_token"]

code, body = post("/auth/change-password", {"current_password": "salah", "new_password": "baru12345"}, token)
check("wrong current password rejected", code == 401, f"({code})")

code, body = post("/auth/change-password", {"current_password": CURRENT, "new_password": "12345"}, token)
check("short new password rejected", code == 400, f"({code})")

code, body = post("/auth/change-password", {"current_password": CURRENT, "new_password": CURRENT}, token)
check("same password rejected", code == 400, f"({code})")

code, body = post("/auth/change-password", {"current_password": CURRENT, "new_password": "baru12345"}, token)
check("change with valid current password", code == 200, f"({code})")

code, body = post("/auth/login", {"email": EMAIL, "password": CURRENT})
check("old password fails after change", code == 401, f"({code})")

code, body = post("/auth/login", {"email": EMAIL, "password": "baru12345"})
check("new password logs in", code == 200 and body.get("access_token"), f"({code})")
token2 = body["access_token"]

code, body = post("/auth/change-password", {"current_password": "baru12345", "new_password": CURRENT}, token2)
check("restore original password", code == 200, f"({code})")

code, body = post("/auth/login", {"email": EMAIL, "password": CURRENT})
check("original password works again", code == 200 and body.get("access_token"), f"({code})")

print("\n" + ("ALL CHANGE-PASSWORD CHECKS PASS" if ok else "SOME CHECKS FAILED"))
sys.exit(0 if ok else 1)
