import httpx

BASE = "http://127.0.0.1:8000/api/v1"
C = httpx.Client(base_url=BASE, timeout=30)

ok = True


def check(name, cond, detail=""):
    global ok
    if cond:
        print(f"  PASS  {name}")
    else:
        ok = False
        print(f"  FAIL  {name}  {detail}")


def login(email, pw):
    r = C.post("auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def main():
    H = login("budi@tokomaju.com", "budi123")
    tenant = "toko-maju"

    ints = C.get(f"tenants/{tenant}/integrations", headers=H).json()
    check("integrations list", isinstance(ints, list) and all("provider" in i for i in ints))

    integ = next((i for i in ints if i.get("provider") == "bca"), None)
    if not integ:
        r = C.post(
            f"tenants/{tenant}/integrations",
            headers=H,
            json={"provider": "bca", "display_name": "BCA Rekening Utama"},
        )
        check("create integration", r.status_code == 201, r.text[:200])
        integ = r.json()
    iid = integ["id"]

    if integ.get("status") != "active":
        r = C.patch(f"tenants/{tenant}/integrations/{iid}", headers=H, json={"status": "active"})
        check("activate integration", r.status_code == 200, r.text[:200])

    banks = C.get(f"tenants/{tenant}/bank-accounts", headers=H).json()
    check("bank-accounts available", isinstance(banks, list) and len(banks) > 0)
    bid = banks[0]["id"]

    import uuid
    run = uuid.uuid4().hex[:8]
    payload = {
        "bank_account_id": bid,
        "transactions": [
            {"external_id": f"SYNCTEST-{run}-1", "transaction_date": "2026-07-30", "description": "Transfer masuk", "amount": "150000"},
            {"external_id": f"SYNCTEST-{run}-2", "transaction_date": "2026-07-31", "description": "Pembayaran vendor", "amount": "-75000"},
            {"external_id": f"SYNCTEST-{run}-3", "transaction_date": "2026-07-31", "description": "Topup", "amount": "50000"},
            {"external_id": f"SYNCTEST-{run}-1", "transaction_date": "2026-07-30", "description": "dup", "amount": "150000"},
        ],
    }

    r = C.post(f"tenants/{tenant}/integrations/{iid}/sync", headers=H, json=payload)
    check("sync imports batch", r.status_code == 200, r.text[:200])
    if r.status_code == 200:
        body = r.json()
        check("sync imported=3 skipped=1", body.get("imported") == 3 and body.get("skipped") == 1, str(body))
        check("sync sets lastSyncedAt", bool(body["integration"].get("lastSyncedAt")), str(body))
        check("sync clears errorMessage", body["integration"].get("errorMessage") is None, str(body))

    r = C.post(f"tenants/{tenant}/integrations/{iid}/sync", headers=H, json=payload)
    check("resync all skipped", r.status_code == 200 and r.json().get("imported") == 0 and r.json().get("skipped") == 4, r.text[:200])

    zero = {
        "bank_account_id": bid,
        "transactions": [
            {"external_id": f"SYNCTEST-{run}-zero", "transaction_date": "2026-07-31", "description": "zero", "amount": "0"},
        ],
    }
    r = C.post(f"tenants/{tenant}/integrations/{iid}/sync", headers=H, json=zero)
    check("sync rejects zero amount", r.status_code == 422, r.text[:200])

    r = C.post(
        f"tenants/{tenant}/integrations",
        headers=H,
        json={"provider": "syncdis", "display_name": "Sync Disconnected Test"},
    )
    check("create disconnected integration", r.status_code == 201, r.text[:200])
    iid2 = r.json()["id"]
    r = C.post(f"tenants/{tenant}/integrations/{iid2}/sync", headers=H, json={"bank_account_id": bid, "transactions": []})
    check("sync rejects disconnected", r.status_code == 422, r.text[:200])
    C.delete(f"tenants/{tenant}/integrations/{iid2}", headers=H)

    bt = C.get(f"tenants/{tenant}/bank-transactions?pageSize=100&search=SYNCTEST", headers=H)
    if bt.status_code == 200:
        check("synced rows visible in bank-transactions", len(bt.json().get("items", [])) == 3)

    print(f"\n{'ALL CHECKS PASS' if ok else 'SOME CHECKS FAILED'} ({'pass' if ok else 'fail'})")
    exit(0 if ok else 1)


if __name__ == "__main__":
    main()
