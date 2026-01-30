import json
import os
import re
import time
from datetime import datetime
from urllib.request import Request, urlopen

from playwright.sync_api import expect

from pages.page_login import LoginPage


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
        password = os.getenv("SIGNUP_PASSWORD", "Zxc12345")
    if verification_code is None:
        verification_code = os.getenv("SIGNUP_VERIFICATION_CODE", "")
    if first_name is None:
        first_name = os.getenv("SIGNUP_FIRST_NAME", "YU")
    if last_name is None:
        last_name = os.getenv("SIGNUP_LAST_NAME", "ZIH")

    page.goto(f"{base}/ds#/signup")

    #page.get_by_text("Sign Up").click()
    page.get_by_role("textbox").first.fill(email)
    page.get_by_text("Verify My Email").click()
    expect(page.get_by_text("Verification code sent")).to_be_visible()
    if not verification_code:
        use_mailtrap = os.getenv("MAILTRAP_STATUS", "").lower() in {"1", "true", "yes"}
        if use_mailtrap:
            verification_code = _fetch_verification_code_from_mailtrap(email)
        if not verification_code:
            verification_code = input('[Email Notification] Receive "Verify your email address" then enter verification code: ').strip()
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
