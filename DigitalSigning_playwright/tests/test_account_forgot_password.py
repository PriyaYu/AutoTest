import os

import re

from playwright.sync_api import expect

from flows.flow_signup import signup
from flows.flow_login import login


def test_account_forgot_password(page) -> None:
    base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
    email, old_password = signup(page)
    new_password = os.getenv("FORGOT_PASSWORD_NEW_PASSWORD", "Zxc123456")
    verification_code = os.getenv("FORGOT_PASSWORD_CODE", "")

    page.goto(f"{base}/ds#/login")
    page.get_by_text("Forgot Password?").click()
    expect(page.locator("section")).to_contain_text("Forgot Password")
    page.get_by_role("textbox").first.click()
    page.get_by_role("textbox").first.fill(email)
    page.get_by_text("Verify My Email").click()
    expect(page.locator("body")).to_contain_text("Verification code sent")
    if not verification_code:
        verification_code = input(
            '[Email Notification] Receive "Forgot Password" verification email then enter code: '
        ).strip()
    if not verification_code:
        raise ValueError("Verification code is required but not set")
    page.get_by_role("textbox").first.fill(verification_code)
    page.get_by_text("Continue").click()
    page.get_by_role("textbox").first.fill(new_password)
    page.get_by_role("textbox").nth(1).fill(new_password)
    page.get_by_text("Continue").click()

    login(page, email=email, password=old_password)
    expect(page.get_by_text("Invalid Login Name or Password.")).to_be_visible()

    login(page, email=email, password=new_password)
    expect(
        page.get_by_role("heading", name=re.compile(r"^Welcome back"))
    ).to_be_visible(timeout=15000)
