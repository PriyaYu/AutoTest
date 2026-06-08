import os
import re

from playwright.sync_api import expect

from pages.page_menu import Menu

BASE = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
_LOGIN_URL = re.compile(r"/#/login")


def _logout_via_menu(page):
    menu = Menu(page)
    try:
        menu.logout_tab.click(timeout=8000)
    except Exception:
        # Dashboard upload overlay can intercept the sidebar click.
        menu.logout_tab.click(force=True)


def _logout_via_dropdown(page):
    page.locator(".user-wrap").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Logout").first.click()


def logout(page, entry: str = "menu") -> None:
    """Log out via the given entry ('menu' = sidebar, 'dropdown' = user menu)
    and verify the session is actually cleared."""
    page.wait_for_timeout(1500)  # let the dashboard settle

    if entry == "menu":
        _logout_via_menu(page)
    elif entry == "dropdown":
        _logout_via_dropdown(page)
    else:
        raise ValueError(f"Unknown logout entry: {entry}")

    # 1) Redirected to the login page.
    expect(page).to_have_url(_LOGIN_URL, timeout=15000)

    # 2) Session is cleared: visiting a protected page bounces back to login.
    page.goto(f"{BASE}/#/dashboard")
    expect(page).to_have_url(_LOGIN_URL, timeout=15000)
