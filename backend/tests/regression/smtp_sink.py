import asyncio
import logging
import os

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP


class FileHandler:
    def __init__(self, path: str):
        self.path = path

    async def handle_DATA(self, server, session, envelope):
        with open(self.path, "a") as f:
            f.write(f"=== TO: {', '.join(envelope.rcpt_tos)} ===\n")
            f.write(envelope.content.decode("utf-8", errors="replace"))
            f.write("\n")
        return "250 OK"


async def amain():
    path = "/tmp/smtp_emails.log"
    if os.path.exists(path):
        os.remove(path)
    handler = FileHandler(path)
    controller = Controller(handler, hostname="0.0.0.0", port=1025)
    controller.start()
    print("SMTP sink on 0.0.0.0:1025 -> /tmp/smtp_emails.log", flush=True)
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        controller.stop()


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
