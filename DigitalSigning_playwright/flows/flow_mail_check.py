import base64
import html
import json
import os
import quopri
import re
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

from flows.flow_signup import _focus_terminal, _focus_browser


def _mailhog_cfg():
    """Return (base_url, auth_headers), or (None, None) if MailHog is unconfigured."""
    base = os.getenv("MAILHOG_API_URL", "http://61.31.169.97:8025")
    if not base:
        return None, None
    user = os.getenv("MAILHOG_USER", "admin")
    pwd = os.getenv("MAILHOG_PASS", "admin123")
    auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return base, {"Authorization": f"Basic {auth}"}


def _mailhog_search(query: str, kind: str = "to"):
    """Search MailHog (kind=to|from|containing). Returns a list of message dicts,
    or None if MailHog is unconfigured/unreachable (raises on transport error)."""
    base, headers = _mailhog_cfg()
    if not base:
        return None
    url = f"{base}/api/v2/search?kind={kind}&query={quote(query)}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("items", [])


def _b64_decode(s: str) -> str:
    s = "".join(s.split())
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s).decode("utf-8", "ignore")


def _decode_mail_chunks(msg: dict) -> str:
    """Decode every layer of a MailHog message body (top-level base64 /
    quoted-printable plus nested base64 MIME parts) and join them, WITHOUT
    stripping HTML tags. Tag-aware callers (URL extraction) need the markup."""
    content = msg.get("Content", {})
    body = content.get("Body", "")
    cte = content.get("Headers", {}).get("Content-Transfer-Encoding", [""])
    enc = (cte[0] if cte else "").lower()

    chunks = [body]  # always keep the raw body (covers 7bit / plain text)
    try:
        if enc == "base64":
            chunks.append(_b64_decode(body))
        elif enc in ("quoted-printable", "quoted_printable"):
            chunks.append(quopri.decodestring(body.encode("utf-8", "ignore")).decode("utf-8", "ignore"))
    except Exception:
        pass
    # Nested base64 MIME parts (multipart messages).
    for blob in re.findall(
        r"Content-Transfer-Encoding:\s*base64\s*\r?\n\r?\n([A-Za-z0-9+/=\r\n ]+)",
        body, re.IGNORECASE,
    ):
        try:
            chunks.append(_b64_decode(blob))
        except Exception:
            pass
    return " ".join(chunks)


def _decode_mail_text(msg: dict) -> str:
    """Decoded message body as plain text (tags stripped) for subject/title
    matching."""
    text = re.sub(r"<[^>]+>", " ", _decode_mail_chunks(msg))
    return re.sub(r"\s+", " ", text).strip()


# A signing/activation link: .../#/verify-otp?token=<JWT>. In the HTML the token
# sits in a styling <span> right after "?", so allow tag(s) between "?" and
# "token="; the JWT charset then stops the match at the closing </span> (the next
# "<"), which keeps footer text from being glued onto the token.
_VERIFY_URL_RE = re.compile(
    r"https?://[^\s\"'<>]*?/#/verify-otp\?(?:<[^>]+>)*token=[A-Za-z0-9._-]+",
    re.IGNORECASE,
)


def fetch_verify_url_from_mailhog(recipient: str, timeout_seconds: int = None) -> str:
    """Poll MailHog for the signing-task email to `recipient` and return its
    verify-otp activation URL, or '' if not found / MailHog unreachable. The
    recipient is unique per run, so no freshness baseline is needed."""
    timeout_seconds = timeout_seconds or int(os.getenv("MAIL_POLL_TIMEOUT", "60"))
    interval = int(os.getenv("MAIL_POLL_INTERVAL", "5"))
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            items = _mailhog_search(recipient, kind="to")
            if items is None:
                return ""
            for msg in items:
                markup = html.unescape(_decode_mail_chunks(msg))
                match = _VERIFY_URL_RE.search(markup)
                if match:
                    # Drop the inline <span> tag(s) sitting between "?" and "token=".
                    url = re.sub(r"<[^>]+>", "", match.group(0))
                    print(f"[Mail OK] verify URL for {recipient}: {url[:55]}...")
                    return url
        except Exception:
            pass
        time.sleep(interval)
    return ""


def _to_addresses(msg: dict):
    return {f"{t.get('Mailbox')}@{t.get('Domain')}" for t in (msg.get("To") or [])}


def confirm_mail_received(subject: str, recipient: str = "", title: str = "",
                          timeout_seconds: int = None) -> None:
    """Assert (via MailHog) that an email reached the recipient.

    Matches a message whose Subject contains `subject`, addressed to `recipient`
    (when that is a real email), and whose body contains the run-unique `title`
    (so a stale email from a previous run can't satisfy the check). Polls until
    `timeout_seconds` then raises. Falls back to the manual/auto prompt only when
    MailHog itself is unreachable."""
    if not subject:
        raise ValueError("subject is required but not set")
    timeout_seconds = timeout_seconds or int(os.getenv("MAIL_POLL_TIMEOUT", "60"))
    interval = int(os.getenv("MAIL_POLL_INTERVAL", "5"))
    recipient_is_email = "@" in recipient

    # MailHog's "containing" search matches the RAW stored body, which is
    # base64/quoted-printable encoded, so the plain `title` is not searchable that
    # way. Search by recipient (or the plain-text subject header) and filter on the
    # decoded body in code instead.
    if recipient_is_email:
        kind, query = "to", recipient
    else:
        kind, query = "containing", subject

    deadline = time.time() + timeout_seconds
    reached = False
    last_error = ""
    while time.time() < deadline:
        try:
            items = _mailhog_search(query, kind=kind)
            if items is None:
                break  # MailHog not configured -> fall back below
            reached = True
            for msg in items:
                subj = " ".join(msg.get("Content", {}).get("Headers", {}).get("Subject", []))
                if subject.lower() not in subj.lower():
                    continue
                if recipient_is_email and recipient not in _to_addresses(msg):
                    continue
                if title and title not in _decode_mail_text(msg):
                    continue
                print(f'[Mail OK] subject="{subject}" recipient="{recipient or "-"}" '
                      f'title="{title or "-"}"')
                return
        except Exception as exc:
            last_error = str(exc)
        time.sleep(interval)

    if reached:
        raise AssertionError(
            f'Email not found in MailHog within {timeout_seconds}s: '
            f'subject="{subject}" recipient="{recipient or "-"}" title="{title or "-"}"'
        )

    # MailHog unreachable/unconfigured: degrade gracefully to the old behaviour.
    print(f"[Mail Notification] MailHog unreachable ({last_error or 'no API'}); falling back.")
    _fallback_confirm(subject, recipient)


def _fallback_confirm(subject: str, recipient: str = "") -> None:
    recipient_part = recipient if recipient else "-"
    auto_confirm = os.getenv("AUTO_CONFIRM_MAIL", "0").lower() in {"1", "true", "yes"}
    if auto_confirm:
        print(f'[Mail Notification] Auto-confirmed subject="{subject}" recipient="{recipient_part}"')
        return
    prompt = (
        f'[Mail Notification] Confirm subject="{subject}" recipient="{recipient_part}" (Y/N): '
    )
    _focus_terminal()
    mail_ready = input(prompt).strip()
    _focus_browser()
    if mail_ready.lower() not in {"y", "yes"}:
        print("[Mail Notification] Email not received yet; continuing as requested.")


def prompt_verify_url(recipient: str = "") -> str:
    if recipient:
        url = fetch_verify_url_from_mailhog(recipient)
        if url:
            return url
    _focus_terminal()
    verify_url = input("[Mail Notification] Paste verify URL from email (run pytest -s): ").strip()
    _focus_browser()
    if not verify_url:
        raise ValueError("verify URL is required but not set")
    return verify_url
