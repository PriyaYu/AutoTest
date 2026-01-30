import os

from playwright.sync_api import expect


def activate_account(page, verify_url, otp=None, password=None):
    if not verify_url:
        raise ValueError("verify_url is required but not set")
    if password is None:
        password = os.getenv("SIGNUP_PASSWORD", "Zxc12345")
    page.goto(verify_url)
    expect(page.get_by_role("heading", name="Verify OTP")).to_be_visible()
    page.get_by_role("button", name="GENERATE OTP").click()
    if otp is None:
        otp = input("[Mail Notification] Enter OTP from email (run pytest -s): ").strip()
    if not otp:
        raise ValueError("OTP is required but not set")
    page.get_by_role("textbox", name="OTP").fill(otp)
    page.get_by_role("button", name="VERIFY").click()
    page.get_by_role("textbox", name="Enter new password").fill(password)
    page.get_by_role("textbox", name="Re-type new password").fill(password)
    page.get_by_role("button", name="Confirm").click()
