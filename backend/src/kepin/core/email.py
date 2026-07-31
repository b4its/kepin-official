from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from kepin.core.config import get_settings

log = logging.getLogger(__name__)


def send_reset_email(to_email: str, reset_token: str) -> bool:
    """Mengirim email reset password. Return False jika SMTP tak dikonfigurasi
    atau pengiriman gagal (pemanggil dapat memakai fallback dev token)."""
    settings = get_settings()
    if not settings.smtp_configured:
        return False

    reset_url = f"{settings.public_app_url.rstrip('/')}/auth/reset-password?token={reset_token}"

    text = f"""
KePin — Atur Ulang Kata Sandi

Anda meminta pengaturan ulang kata sandi. Buka tautan berikut dalam 30 menit:

{reset_url}

Jika Anda tidak meminta ini, abaikan email ini.
"""
    html = f"""
<html><body style="font-family:Arial,sans-serif;color:#1f2937">
  <h2 style="color:#2563eb">KePin</h2>
  <p>Anda meminta pengaturan ulang kata sandi. Tautan berlaku <strong>30 menit</strong>:</p>
  <p><a href="{reset_url}" style="display:inline-block;padding:10px 18px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px">Atur Ulang Kata Sandi</a></p>
  <p style="color:#6b7280;font-size:12px">Jika Anda tidak meminta ini, abaikan email ini.</p>
</body></html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "KePin — Atur Ulang Kata Sandi"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_tls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password or "")
            server.sendmail(settings.smtp_from, [to_email], msg.as_string())
        log.info("Reset email sent to %s", to_email)
        return True
    except Exception:
        log.warning("SMTP send to %s failed", to_email, exc_info=True)
        return False
