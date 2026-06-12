import base64
import json
import os
import quopri
import re
import time
from datetime import datetime
from urllib.parse import quote
from urllib.request import Request, urlopen

from playwright.sync_api import expect

from pages.page_login import LoginPage


def _focus_terminal():
    import os
    import platform
    if platform.system() == "Darwin":
        try:
            term = os.environ.get("TERM_PROGRAM", "")
            if term == "Apple_Terminal":
                app = "Terminal"
            elif term == "iTerm.app":
                app = "iTerm"
            elif term == "vscode":
                app = "Visual Studio Code"
            else:
                app = "Terminal"
            os.system(f"osascript -e 'tell application \"{app}\" to activate'")
        except Exception:
            pass

def _focus_browser():
    import os
    import platform
    if platform.system() == "Darwin":
        try:
            # Playwright browser might be Chromium or Google Chrome
            os.system("osascript -e 'tell application \"Chromium\" to activate' >/dev/null 2>&1")
            os.system("osascript -e 'tell application \"Google Chrome\" to activate' >/dev/null 2>&1")
            os.system("osascript -e 'tell application \"Google Chrome for Testing\" to activate' >/dev/null 2>&1")
        except Exception:
            pass

def signup(
    page,
    email=None,
    verification_code=None,
    first_name=None,
    last_name=None,
    password=None,
    login_after=False,
):
    base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
    if email is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        base_alias = os.getenv("SIGNUP_ALIAS_BASE", "")
        email = f"{base_alias}+{timestamp}@gmail.com"
    if password is None:
        # Fall back to the login default so the new account is usable by later
        # login() calls; the old "Zxc12345" default both mismatched that and
        # violated the "no consecutive numbers/phrases" password policy.
        password = os.getenv("SIGNUP_PASSWORD") or os.getenv("LOGIN_DEFAULT_PASSWORD", "")
    if verification_code is None:
        verification_code = os.getenv("SIGNUP_VERIFICATION_CODE", "")
    if first_name is None:
        first_name = os.getenv("SIGNUP_FIRST_NAME", "YU")
    if last_name is None:
        last_name = os.getenv("SIGNUP_LAST_NAME", "ZIH")

    page.goto(f"{base}/#/signup")

    #page.get_by_text("Sign Up").click()
    page.get_by_role("textbox").first.fill(email)
    page.get_by_text("Verify My Email").click()
    expect(page.get_by_text("Verification code sent")).to_be_visible()
    if not verification_code:
        verification_code = _fetch_verification_code_from_mailhog(email)
    if not verification_code:
        use_mailtrap = os.getenv("MAILTRAP_STATUS", "").lower() in {"1", "true", "yes"}
        if use_mailtrap:
            verification_code = _fetch_verification_code_from_mailtrap(email)
    if not verification_code:
        _focus_terminal()
        verification_code = input('[Email Notification] Receive "Verify your email address" then enter verification code: ').strip()
        page.bring_to_front()
        _focus_browser()
    if not verification_code:
        raise ValueError("Verification code is required but not set")
    page.get_by_role("textbox").first.fill(verification_code)
    page.get_by_text("Continue").click()

    page.get_by_role("textbox").first.click()
    page.get_by_role("textbox").first.fill(first_name)
    page.get_by_role("textbox").first.press("Tab")
    page.get_by_role("textbox").nth(1).fill(last_name)
    page.get_by_role("textbox").nth(1).press("Tab")
    page.locator("input[type=\"password\"]").fill(password)
    page.get_by_label("", exact=True).check()
    page.get_by_text("Continue").click()
    expect(page.get_by_text("SEND SUCCESS")).to_be_visible()
    page.get_by_role("button", name="Ok").click()

    if login_after:
        captcha = os.getenv("LOGIN_DEFAULT_CAPTCHA", "")
        if not captcha:
            raise ValueError("LOGIN_DEFAULT_CAPTCHA is required but not set")
        return (
            LoginPage(page)
            .fill_email(email)
            .fill_password(password)
            .fill_captcha(captcha)
            .submit()
        )

    return email, password


def _fetch_verification_code_from_mailtrap(recipient_email: str) -> str:
    api_token = os.getenv("MAILTRAP_API_TOKEN", "")
    account_id = os.getenv("MAILTRAP_ACCOUNT_ID", "")
    inbox_id = os.getenv("MAILTRAP_INBOX_ID", "")
    if not (api_token and account_id and inbox_id):
        return ""

    timeout_seconds = int(os.getenv("MAILTRAP_POLL_TIMEOUT", "60"))
    interval_seconds = int(os.getenv("MAILTRAP_POLL_INTERVAL", "5"))
    code_pattern = os.getenv("SIGNUP_VERIFICATION_REGEX", r"\b[A-Za-z0-9]{4,6}\b")
    pattern = re.compile(code_pattern)

    base_url = f"https://mailtrap.io/api/accounts/{account_id}/inboxes/{inbox_id}"
    headers = {"Api-Token": api_token}

    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            list_url = f"{base_url}/messages?search={recipient_email}"
            req = Request(list_url, headers=headers)
            with urlopen(req, timeout=30) as resp:
                messages = json.loads(resp.read().decode("utf-8"))
            print(f"[DEBUG] Mailtrap messages found: {len(messages)}")
            if messages:
                message_id = max(m.get("id", 0) for m in messages)
                print(f"[DEBUG] Mailtrap latest message id: {message_id}")
                body_url = f"{base_url}/messages/{message_id}/body.txt"
                body_req = Request(body_url, headers=headers)
                with urlopen(body_req, timeout=30) as body_resp:
                    body_text = body_resp.read().decode("utf-8")
                print("[DEBUG] Mailtrap body (first 200 chars):")
                print(body_text[:200])
                match = pattern.search(body_text)
                if match:
                    return match.group(0)
        except Exception as exc:
            last_error = str(exc)
        time.sleep(interval_seconds)

    if last_error:
        print(f"[DEBUG] Mailtrap lookup error: {last_error}")
    return ""


def _query_mailhog_latest(recipient_email: str):
    """Single-shot: return the newest MailHog message dict for `recipient_email`,
    or None. Raises on transport errors (caller handles)."""
    base = os.getenv("MAILHOG_API_URL", "http://61.31.169.97:8025")
    if not base:
        return None
    user = os.getenv("MAILHOG_USER", "admin")
    pwd = os.getenv("MAILHOG_PASS", "admin123")
    auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    url = f"{base}/api/v2/search?kind=to&query={quote(recipient_email)}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = data.get("items", [])
    if not items:
        return None
    return max(items, key=lambda m: m.get("Created", ""))


def latest_mailhog_id(recipient_email: str):
    """Return the newest message's ID for `recipient_email` (a baseline to wait
    past), or None. Never raises."""
    try:
        msg = _query_mailhog_latest(recipient_email)
        return msg.get("ID") if msg else None
    except Exception:
        return None


def _fetch_latest_mailhog_body(recipient_email: str, timeout_seconds: int = None,
                               after_id: str = None) -> str:
    """Poll MailHog for the newest email to `recipient_email` and return its body.
    If `after_id` is given, wait until a message with a *different* ID arrives
    (so a freshly-sent email isn't confused with an older one to the same address).
    Returns '' if MailHog is unconfigured/unreachable or it times out."""
    timeout_seconds = timeout_seconds or int(os.getenv("MAIL_POLL_TIMEOUT", "60"))
    interval_seconds = int(os.getenv("MAIL_POLL_INTERVAL", "5"))

    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            msg = _query_mailhog_latest(recipient_email)
            if msg is None:
                print(f"[DEBUG] MailHog: no messages yet for {recipient_email}")
            else:
                msg_id = msg.get("ID")
                if after_id is not None and msg_id == after_id:
                    print(f"[DEBUG] MailHog: only baseline {msg_id!r}, waiting for newer")
                else:
                    body = msg.get("Content", {}).get("Body", "")
                    print(f"[DEBUG] MailHog id={msg_id!r} body (first 200): {body[:200]!r}")
                    return body
        except Exception as exc:
            last_error = str(exc)
        time.sleep(interval_seconds)

    if last_error:
        print(f"[DEBUG] MailHog lookup error: {last_error}")
    return ""


def _fetch_verification_code_from_mailhog(recipient_email: str, after_id: str = None) -> str:
    body = _fetch_latest_mailhog_body(recipient_email, after_id=after_id)
    if not body:
        return ""
    # The body is quoted-printable HTML; decode and strip tags before parsing.
    decoded = quopri.decodestring(body.encode("utf-8", "ignore")).decode("utf-8", "ignore")
    text = re.sub(r"<[^>]+>", " ", decoded)
    text = re.sub(r"\s+", " ", text)
    # The code follows "...complete your registration: <CODE>" (same template for
    # signup and password reset).
    pattern = re.compile(
        os.getenv("MAIL_CODE_REGEX", r"registration:\s*([A-Za-z0-9]{4,8})"), re.IGNORECASE
    )
    match = pattern.search(text)
    if match:
        return match.group(1) if match.groups() else match.group(0)
    print(f"[DEBUG] MailHog: code not found in: {text[:200]!r}")
    return ""
