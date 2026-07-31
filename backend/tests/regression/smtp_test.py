import httpx

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=15)
ok = True


def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


r = C.post("/auth/forgot-password", json={"email": "ani@tokomaju.com"})
body = r.json()
check("forgot-password 200", r.status_code == 200, f"({r.status_code})")
check("no dev_reset_token (SMTP configured)", body.get("dev_reset_token") is None, str(body)[:120])

import re
from email import policy
from email.parser import BytesParser

log = open("/tmp/smtp_emails.log", "rb").read()
chunks = re.split(rb"=== TO:", log)
raw = chunks[-1]
msg = BytesParser(policy=policy.default).parsebytes(b"TO:" + raw)
text = ""
for part in msg.walk():
    if part.get_content_type() in ("text/plain", "text/html"):
        text += part.get_content()
flat = re.sub(r"\s+", "", text)
m = re.search(r"reset-password\?token=([A-Za-z0-9_-]{43})", flat)
check("email captured by sink", bool(m), "check /tmp/smtp_emails.log")
token = m.group(1) if m else ""

r = C.post("/auth/reset-password", json={"token": token, "new_password": "aniSMTP99"})
check("reset-password with emailed token", r.status_code == 200, f"({r.status_code})")

r = C.post("/auth/login", json={"email": "ani@tokomaju.com", "password": "aniSMTP99"})
check("login with new password", r.status_code == 200, f"({r.status_code})")
login_tok = r.json()["access_token"] if r.status_code == 200 else ""

r = C.post("/auth/forgot-password", json={"email": "nonexistent@xyz.com"})
check("unknown email no token", r.status_code == 200 and r.json().get("dev_reset_token") is None)

r = C.post("/auth/change-password", json={"current_password": "aniSMTP99", "new_password": "ani12345"}, headers={"authorization": f"Bearer {login_tok}"})
check("change back to ani12345", r.status_code == 200, f"({r.status_code})")
r = C.post("/auth/login", json={"email": "ani@tokomaju.com", "password": "ani12345"})
check("restored ani12345", r.status_code == 200, f"({r.status_code})")

print("ALL SMTP CHECKS PASS" if ok else "FAILURES")
