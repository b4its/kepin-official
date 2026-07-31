import os
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


def post(path, payload):
    r = C.post(path, json=payload, headers={"content-type": "application/json"})
    return r.status_code, r.json()


EMAIL = "ani@tokomaju.com"

SMTP_ENV = bool(os.environ.get("SMTP_HOST"))


def latest_emailed_token():
    import re
    from email import policy
    from email.parser import BytesParser

    log = open("/tmp/smtp_emails.log", "rb").read()
    chunks = re.split(rb"=== TO:", log)
    msg = BytesParser(policy=policy.default).parsebytes(b"TO:" + chunks[-1])
    text = "".join(
        p.get_content()
        for p in msg.walk()
        if p.get_content_type() in ("text/plain", "text/html")
    )
    m = re.search(r"reset-password\?token=([A-Za-z0-9_-]{43})", re.sub(r"\s+", "", text))
    return m.group(1) if m else ""


code, body = post("/auth/forgot-password", {"email": EMAIL})
check(
    "forgot returns dev token" if not SMTP_ENV else "forgot returns no dev token (smtp)",
    code == 200 and (body.get("dev_reset_token") if not SMTP_ENV else body.get("dev_reset_token") is None),
    f"({code})",
)
token = latest_emailed_token() if SMTP_ENV else body["dev_reset_token"]

code, body = post("/auth/forgot-password", {"email": "tidak-ada@example.com"})
check("unknown email same response, no token", code == 200 and not body.get("dev_reset_token"), f"({code})")

code, body = post("/auth/reset-password", {"token": "bogus", "new_password": "baru12345"})
check("invalid token rejected", code == 401, f"({code})")

code, body = post("/auth/reset-password", {"token": token, "new_password": "12345"})
check("short password rejected", code == 400, f"({code})")

code, body = post("/auth/reset-password", {"token": token, "new_password": "baru12345"})
check("reset with valid token", code == 200, f"({code})")

code, body = post("/auth/login", {"email": EMAIL, "password": "ani123"})
check("old password fails", code == 401, f"({code})")

code, body = post("/auth/login", {"email": EMAIL, "password": "baru12345"})
check("new password logs in", code == 200 and body.get("access_token"), f"({code})")

code, body = post("/auth/reset-password", {"token": token, "new_password": "baru54321"})
check("token is one-time", code == 401, f"({code})")

code, body = post("/auth/forgot-password", {"email": EMAIL})
token2 = latest_emailed_token() if SMTP_ENV else body.get("dev_reset_token", "")
code, body = post("/auth/reset-password", {"token": token2, "new_password": "ani12345"})
check("restore with valid 8+ char password", code == 200, f"({code})")

code, body = post("/auth/login", {"email": EMAIL, "password": "ani12345"})
check("restored password works (ani12345)", code == 200 and body.get("access_token"), f"({code})")

print("\n" + ("ALL RESET CHECKS PASS" if ok else "SOME CHECKS FAILED"))
sys.exit(0 if ok else 1)
