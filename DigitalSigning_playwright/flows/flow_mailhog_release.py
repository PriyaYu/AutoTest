"""MailHog helpers: read the latest caught message and release it upstream.

Pattern: SIT mail is caught by MailHog (so it never hits real inboxes). After a
test validates the email, `release_message` re-delivers it to the real recipient
via an upstream SMTP, so the rest of the flow (e.g. the actual signer) proceeds.

Config via env (defaults match flows/flow_signup.py so one MAILHOG_API_URL
override covers both):
  MAILHOG_API_URL   MailHog base URL (default http://61.31.169.97:8025)
  MAILHOG_USER/PASS basic-auth credentials (default admin/admin123)
  MAILHOG_RELEASE_HOST/PORT  upstream SMTP to deliver released mail through
"""
import base64
import json
import os
from urllib.request import Request, urlopen

MAILHOG_API = os.getenv("MAILHOG_API_URL", "http://61.31.169.97:8025")
MAILHOG_USER = os.getenv("MAILHOG_USER", "admin")
MAILHOG_PASS = os.getenv("MAILHOG_PASS", "admin123")
# Upstream SMTP the released mail is delivered through (the "real" mail server).
RELEASE_HOST = os.getenv("MAILHOG_RELEASE_HOST", "")
RELEASE_PORT = os.getenv("MAILHOG_RELEASE_PORT", "25")
# Optional SMTP auth (Gmail and most relays require it).
RELEASE_USER = os.getenv("MAILHOG_RELEASE_USER", "")
RELEASE_PASS = os.getenv("MAILHOG_RELEASE_PASS", "")
RELEASE_MECHANISM = os.getenv("MAILHOG_RELEASE_MECHANISM", "PLAIN")


def _auth_headers(extra=None):
    token = base64.b64encode(f"{MAILHOG_USER}:{MAILHOG_PASS}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    if extra:
        headers.update(extra)
    return headers


def get_latest_message():
    """Step 1 + 2: fetch the message list and return the latest message's
    (message_id, recipient_email). The recipient is read dynamically from the
    To field, never hardcoded."""
    url = f"{MAILHOG_API}/api/v2/messages?limit=1"
    req = Request(url, headers=_auth_headers())
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    items = data.get("items", [])
    if not items:
        raise RuntimeError("MailHog has no messages")
    latest = items[0]  # MailHog returns newest first

    message_id = latest.get("ID")

    # Prefer the structured To (Mailbox@Domain); fall back to the To header.
    recipient = None
    to_list = latest.get("To") or []
    if to_list:
        recipient = f"{to_list[0].get('Mailbox')}@{to_list[0].get('Domain')}"
    if not recipient:
        header_to = latest.get("Content", {}).get("Headers", {}).get("To", [])
        recipient = header_to[0] if header_to else None

    return message_id, recipient


def release_message(message_id, recipient):
    """Step 3: release (re-deliver) the caught message to the real recipient via
    the upstream SMTP. Returns the HTTP status code."""
    url = f"{MAILHOG_API}/api/v1/messages/{message_id}/release"
    body = {"Host": RELEASE_HOST, "Port": RELEASE_PORT, "Email": recipient}
    if RELEASE_USER:
        body.update({
            "Username": RELEASE_USER,
            "Password": RELEASE_PASS,
            "Mechanism": RELEASE_MECHANISM,
        })
    payload = json.dumps(body).encode("utf-8")
    req = Request(
        url, data=payload,
        headers=_auth_headers({"Content-Type": "application/json"}),
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        return resp.status


if __name__ == "__main__":
    msg_id, to_email = get_latest_message()
    print(f"Latest message: ID={msg_id}  To={to_email}")

    # === your validation logic here (e.g. extract code, check subject/body) ===

    status = release_message(msg_id, to_email)
    print(f"Released {msg_id} -> {to_email}  (HTTP {status})")
