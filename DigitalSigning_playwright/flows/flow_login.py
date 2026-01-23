import os

from pages.page_login import LoginPage


def login(page, email=None, password=None, captcha=None, force_login=False):
    base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
    if email is None:
        email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if password is None:
        password = os.getenv("LOGIN_DEFAULT_PASSWORD", "")
    if captcha is None:
        captcha = os.getenv("LOGIN_DEFAULT_CAPTCHA", "")

    page.goto(f"{base}/ds#/login")

    if force_login:
        # Ensure we are on the target origin before clearing storage.
        page.context.clear_cookies()
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        page.goto(f"{base}/ds#/login")

    print(f"[DEBUG] login email: {email}")
    return (
        LoginPage(page)
        .fill_email(email)
        .fill_password(password)
        .fill_captcha(captcha)
        .submit()
    )
