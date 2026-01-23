from playwright.sync_api import expect

import re

from flows.flow_login import login

def test_login_invalid_password(page) -> None:
    login(page, password="invalid-password", force_login=False)
    expect(page.get_by_text("Authentication failed")).to_be_visible()

    login(page, captcha="invalid-captcha", force_login=False)
    expect(page.get_by_text("Incorrect Captcha")).to_be_visible()

def test_login_success(page) -> None:
    login(page)
    expect(page.get_by_role("heading", name=re.compile(r"^Welcome back"))).to_be_visible()