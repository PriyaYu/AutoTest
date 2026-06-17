"""Real-inbox mail verification over IMAP — the alternative backend to MailHog.

MailHog centrally intercepts every outgoing mail; a real IMAP inbox can only read
ONE mailbox. The tests already use Gmail plus-addressing (zihsyuan0603+001@...),
which all land in the single zihsyuan0603@gmail.com inbox, so one IMAP login plus
an IMAP `TO "+001"` filter resolves the right message.

Selected via env `MAIL_BACKEND=imap` (default `mailhog`). The four read entry
points in flow_mail_check.py / flow_signup.py / flow_activate_account.py dispatch
here when `imap_enabled()` is true; the MailHog code path is left untouched.

Config via env:
  MAIL_BACKEND      mailhog | imap   (default mailhog)
  IMAP_HOST/PORT    default imap.gmail.com:993
  IMAP_USER/PASS    mailbox login (Gmail needs an App Password, IMAP enabled)
  IMAP_FOLDER       default INBOX
  IMAP_SINCE_DAYS   only consider mail newer than N days (default 1) so a stale
                    email from a previous run can't satisfy a check
  MAIL_POLL_TIMEOUT / MAIL_POLL_INTERVAL  shared with the MailHog backend
"""
import email
import html
import imaplib
import os
import re
import time
from datetime import date, timedelta
from email.header import decode_header


def imap_enabled() -> bool:
    """True when the IMAP (real-inbox) backend is selected."""
    return os.getenv("MAIL_BACKEND", "mailhog").strip().lower() == "imap"


def _imap_cfg():
    return (
        os.getenv("IMAP_HOST", "imap.gmail.com"),
        int(os.getenv("IMAP_PORT", "993")),
        os.getenv("IMAP_USER", ""),
        os.getenv("IMAP_PASS", ""),
        os.getenv("IMAP_FOLDER", "INBOX"),
    )


def _connect():
    """Open and select the mailbox, or return None if IMAP is unconfigured."""
    host, port, user, pwd, folder = _imap_cfg()
    if not (user and pwd):
        return None
    conn = imaplib.IMAP4_SSL(host, port)
    conn.login(user, pwd)
    conn.select(folder)
    return conn


def _safe_logout(conn):
    if conn is not None:
        try:
            conn.logout()
        except Exception:
            pass


def _since_date() -> str:
    """IMAP SINCE token (DD-Mon-YYYY) that bounds the search to recent mail."""
    days = int(os.getenv("IMAP_SINCE_DAYS", "1"))
    return (date.today() - timedelta(days=days)).strftime("%d-%b-%Y")


def _search(conn, recipient: str = "", subject: str = ""):
    """Return matching message sequence numbers, newest first. `recipient` is only
    applied when it looks like an email (IMAP TO is a substring match, so a plus
    alias works); a non-email recipient label is ignored and the subject carries
    the search."""
    crit = ["SINCE", _since_date()]
    if recipient and "@" in recipient:
        crit += ["TO", recipient]
    if subject:
        crit += ["SUBJECT", subject]
    typ, data = conn.search(None, *crit)
    if typ != "OK" or not data or not data[0]:
        return []
    return list(reversed(data[0].split()))


def _fetch_message(conn, num):
    typ, data = conn.fetch(num, "(RFC822)")
    if typ != "OK" or not data or not data[0]:
        return None
    return email.message_from_bytes(data[0][1])


def _subject(msg) -> str:
    out = []
    for text, enc in decode_header(msg.get("Subject", "")):
        out.append(text.decode(enc or "utf-8", "ignore") if isinstance(text, bytes) else text)
    return "".join(out)


def _body_markup(msg) -> str:
    """Concatenated decoded text/plain + text/html parts, HTML markup KEPT (URL
    extraction needs the tags). Mirrors MailHog's _decode_mail_chunks."""
    chunks = []
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        if part.get_content_type() in ("text/plain", "text/html"):
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                chunks.append(payload.decode(charset, "ignore"))
    return " ".join(chunks)


def _body_text(msg) -> str:
    """Decoded body as plain text (tags stripped) for title / code matching."""
    text = re.sub(r"<[^>]+>", " ", _body_markup(msg))
    return re.sub(r"\s+", " ", text).strip()


def imap_fetch_verify_url(recipient: str, timeout_seconds: int = None) -> str:
    """Poll the IMAP inbox for the signing/activation email to `recipient` and
    return its verify-otp URL, or '' if not found / IMAP unreachable."""
    from flows.flow_mail_check import _VERIFY_URL_RE

    timeout_seconds = timeout_seconds or int(os.getenv("MAIL_POLL_TIMEOUT", "60"))
    interval = int(os.getenv("MAIL_POLL_INTERVAL", "5"))
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        conn = None
        try:
            conn = _connect()
            if conn is None:
                return ""
            for num in _search(conn, recipient=recipient):
                msg = _fetch_message(conn, num)
                if not msg:
                    continue
                markup = html.unescape(_body_markup(msg))
                match = _VERIFY_URL_RE.search(markup)
                if match:
                    url = re.sub(r"<[^>]+>", "", match.group(0))
                    print(f"[IMAP OK] verify URL for {recipient}: {url[:55]}...")
                    return url
        except Exception as exc:
            print(f"[DEBUG] IMAP verify-url error: {exc}")
        finally:
            _safe_logout(conn)
        time.sleep(interval)
    return ""


def imap_confirm_mail_received(subject: str, recipient: str = "", title: str = "",
                               timeout_seconds: int = None) -> None:
    """Assert (via IMAP) that an email reached `recipient`: Subject contains
    `subject`, To matches `recipient` (when it's a real email), body contains the
    run-unique `title`. Polls then raises. Falls back to the manual/auto prompt
    only when IMAP itself is unconfigured."""
    if not subject:
        raise ValueError("subject is required but not set")
    timeout_seconds = timeout_seconds or int(os.getenv("MAIL_POLL_TIMEOUT", "60"))
    interval = int(os.getenv("MAIL_POLL_INTERVAL", "5"))
    recipient_is_email = "@" in recipient

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        conn = None
        try:
            conn = _connect()
            if conn is None:
                from flows.flow_mail_check import _fallback_confirm
                print("[Mail Notification] IMAP unconfigured; falling back.")
                _fallback_confirm(subject, recipient)
                return
            for num in _search(conn, recipient=recipient, subject=subject):
                msg = _fetch_message(conn, num)
                if not msg:
                    continue
                if subject.lower() not in _subject(msg).lower():
                    continue
                if recipient_is_email and recipient not in (msg.get("To") or ""):
                    continue
                if title and title not in _body_text(msg):
                    continue
                print(f'[IMAP OK] subject="{subject}" recipient="{recipient or "-"}" '
                      f'title="{title or "-"}"')
                return
        except Exception as exc:
            print(f"[DEBUG] IMAP confirm error: {exc}")
        finally:
            _safe_logout(conn)
        time.sleep(interval)

    raise AssertionError(
        f'Email not found via IMAP within {timeout_seconds}s: '
        f'subject="{subject}" recipient="{recipient or "-"}" title="{title or "-"}"'
    )


def imap_fetch_verification_code(recipient_email: str, timeout_seconds: int = None) -> str:
    """Poll the IMAP inbox for the newest email to `recipient_email` and return the
    verification/OTP code parsed from its body, or '' if not found / unreachable.
    Same template as MailHog ("...registration: <code>")."""
    timeout_seconds = timeout_seconds or int(os.getenv("MAIL_POLL_TIMEOUT", "60"))
    interval = int(os.getenv("MAIL_POLL_INTERVAL", "5"))
    pattern = re.compile(
        os.getenv("MAIL_CODE_REGEX", r"registration:\s*([A-Za-z0-9]{4,8})"), re.IGNORECASE
    )
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        conn = None
        try:
            conn = _connect()
            if conn is None:
                return ""
            for num in _search(conn, recipient=recipient_email):
                msg = _fetch_message(conn, num)
                if not msg:
                    continue
                text = _body_text(msg)
                match = pattern.search(text)
                if match:
                    code = match.group(1) if match.groups() else match.group(0)
                    print(f"[IMAP OK] code for {recipient_email}: {code}")
                    return code
        except Exception as exc:
            print(f"[DEBUG] IMAP code error: {exc}")
        finally:
            _safe_logout(conn)
        time.sleep(interval)
    return ""
