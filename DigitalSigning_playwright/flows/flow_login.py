import os
from playwright.sync_api import expect

from pages.page_login import LoginPage


def login(page, email=None, password=None, captcha=None, force_login=False, handle_notice=True):
    base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
    if email is None:
        email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if password is None:
        password = os.getenv("LOGIN_DEFAULT_PASSWORD", "")
    if captcha is None:
        captcha = os.getenv("LOGIN_DEFAULT_CAPTCHA", "")

    page.goto(f"{base}/#/login")

    if force_login:
        # Ensure we are on the target origin before clearing storage.
        page.context.clear_cookies()
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        page.goto(f"{base}/#/login")

    print(f"[DEBUG] login email: {email}")
    login_page = LoginPage(page).fill_email(email).fill_password(password)
    # Refresh the captcha (click the image to regenerate it) before filling it.
    # A stale captcha token — e.g. after a password-change redirect — makes the
    # fixed staging value fail; a fresh token accepts it again.
    try:
        captcha_img = page.locator(".captcha img, img[alt=captcha]").first
        if captcha_img.count() > 0:
            captcha_img.click()
            page.wait_for_timeout(800)
    except Exception:
        pass
    page = login_page.fill_captcha(captcha).submit()

    try:
        if handle_notice:
            # 如果有跳出 Notice 視窗 (例如：重複登入或提示)，就點擊 OK
            # 改用迴圈檢查，最多等待 15 秒，避免網路延遲導致彈窗比較晚出現
            for _ in range(30):
                if page.get_by_text("Notice").is_visible():
                    page.get_by_role("button", name="OK").click()
                    break
                if page.get_by_role("menuitem", name="Dashboard").is_visible():
                    # 進入 Dashboard 後，再檢查一次是否剛好彈出 Notice
                    if page.get_by_text("Notice").is_visible():
                        page.get_by_role("button", name="OK").click()
                    break
                page.wait_for_timeout(500)
    except Exception as e:
        print(f"[DEBUG] handle_notice error: {e}")

    return page
