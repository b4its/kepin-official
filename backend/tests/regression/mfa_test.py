import json
import sys

import httpx

from kepin.core.totp import totp_code

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=10)


def post(path, payload, token=None):
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    r = C.post(path, json=payload, headers=headers)
    return r.status_code, r.json()


def get(path, token):
    r = C.get(path, headers={"authorization": f"Bearer {token}"})
    return r.status_code, r.json()


ok = True


def check(name, cond, detail=""):
    global ok
    status = "PASS" if cond else "FAIL"
    if not cond:
        ok = False
    print(f"[{status}] {name} {detail}")


code, body = post("/auth/login", {"email": "budi@tokomaju.com", "password": "budi123"})
check("login before MFA gives access token", code == 200 and body.get("access_token"), f"({code})")
token = body["access_token"]

code, body = get("/auth/mfa/status", token)
check("mfa status disabled", code == 200 and body.get("enabled") is False)

code, body = post("/auth/mfa/setup", {}, token)
check("setup returns secret+uri", code == 200 and body.get("secret") and body["otpauth_uri"].startswith("otpauth://totp/"), f"({code})")
secret = body["secret"]

good_code = totp_code(secret)
code, body = post("/auth/mfa/enable", {"code": "000000"}, token)
check("enable rejects wrong code", code == 401, f"({code})")

code, body = post("/auth/mfa/enable", {"code": good_code}, token)
check("enable accepts valid code", code == 200 and len(body.get("recovery_codes", [])) == 8, f"({code})")
recovery_codes = body.get("recovery_codes", [])

code, body = post("/auth/mfa/setup", {}, token)
check("second setup blocked when enabled", code == 409, f"({code})")

code, body = post("/auth/login", {"email": "budi@tokomaju.com", "password": "budi123"})
check("login now requires MFA", code == 200 and body.get("mfa_required") is True and body.get("mfa_token") and not body.get("access_token"), f"({code})")
mfa_token = body["mfa_token"]

code, body = post("/auth/mfa/verify", {"mfa_token": mfa_token, "code": "111111"})
check("verify rejects wrong code", code == 401, f"({code})")

code, body = post("/auth/mfa/verify", {"mfa_token": mfa_token, "code": totp_code(secret)})
check("verify accepts valid TOTP", code == 200 and body.get("access_token"), f"({code})")

code, body = post("/auth/login", {"email": "budi@tokomaju.com", "password": "budi123"})
mfa_token2 = body["mfa_token"]
code, body = post("/auth/mfa/verify", {"mfa_token": mfa_token2, "code": recovery_codes[0]})
check("recovery code logs in", code == 200 and body.get("access_token"), f"({code})")

code, body = post("/auth/login", {"email": "budi@tokomaju.com", "password": "budi123"})
mfa_token3 = body["mfa_token"]
code, body = post("/auth/mfa/verify", {"mfa_token": mfa_token3, "code": recovery_codes[0]})
check("recovery code is one-time", code == 401, f"({code})")

code, body = post("/auth/login", {"email": "budi@tokomaju.com", "password": "budi123"})
mfa_token4 = body["mfa_token"]
code, body = post("/auth/mfa/verify", {"mfa_token": mfa_token4, "code": totp_code(secret)})
token2 = body.get("access_token", "")
code, body = post("/auth/mfa/disable", {"code": "000000"}, token2)
check("disable rejects wrong code", code == 401, f"({code})")

code, body = post("/auth/mfa/disable", {"code": totp_code(secret)}, token2)
check("disable with valid code", code == 200, f"({code})")

code, body = post("/auth/login", {"email": "budi@tokomaju.com", "password": "budi123"})
check("login back to direct after disable", code == 200 and body.get("access_token") and not body.get("mfa_required"), f"({code})")

print("\n" + ("ALL MFA CHECKS PASS" if ok else "SOME CHECKS FAILED"))
sys.exit(0 if ok else 1)
