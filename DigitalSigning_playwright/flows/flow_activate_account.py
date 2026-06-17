import os

from playwright.sync_api import expect

from flows.flow_signup import (
    _focus_terminal,
    _focus_browser,
    latest_mailhog_id,
    _fetch_verification_code_from_mailhog,
)


def activate_account(page, verify_url, recipient="", otp=None, password=None):
    if not verify_url:
        raise ValueError("verify_url is required but not set")
    if password is None:
        # Match the login default (see flow_signup) so the activated account is
        # usable by later login() calls and meets the password policy.
        password = os.getenv("SIGNUP_PASSWORD") or os.getenv("LOGIN_DEFAULT_PASSWORD", "")
    page.goto(verify_url)
    expect(page.get_by_role("heading", name="Verify OTP")).to_be_visible()
    # GENERATE OTP sends an OTP email ("Verify your email address (OTP)") that uses
    # the same "...registration: <code>" template as signup. Record a baseline
    # first, then fetch the newer (OTP) mail from MailHog.
    from flows.flow_imap_check import imap_enabled, imap_fetch_verification_code
    use_imap = imap_enabled()
    # IMAP has no message-id baseline; freshness comes from IMAP_SINCE + newest-first.
    baseline_id = latest_mailhog_id(recipient) if (recipient and not use_imap) else None
    page.get_by_role("button", name="GENERATE OTP").click()
    if otp is None and recipient:
        if use_imap:
            otp = imap_fetch_verification_code(recipient)
        else:
            otp = _fetch_verification_code_from_mailhog(recipient, after_id=baseline_id)
    if not otp:
        _focus_terminal()
        otp = input("[Mail Notification] Enter OTP from email (run pytest -s): ").strip()
        page.bring_to_front()
        _focus_browser()
    if not otp:
        raise ValueError("OTP is required but not set")
    page.get_by_role("textbox", name="OTP").fill(otp)
    page.get_by_role("button", name="VERIFY").click()
    page.get_by_role("textbox", name="Enter new password").fill(password)
    page.get_by_role("textbox", name="Re-type new password").fill(password)
    page.get_by_role("button", name="Confirm").click()
