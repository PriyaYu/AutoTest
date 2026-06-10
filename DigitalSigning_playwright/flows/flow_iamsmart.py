import re
from playwright.sync_api import expect

def open_profile_menu(page):
    page.locator('//*[@id="ds-app"]/section/header/section/div[3]').click()


def register_iamSmart(page, action: str, password: str = None):
    open_profile_menu(page)
    page.get_by_text("My Profile info").last.click()
    
    if action == "register":
        page.get_by_role("button", name="Register iAM Smart").click()
        
        password_input = page.get_by_role("textbox", name="Enter password")
        password_input.click()
        if password:
            password_input.fill(password)
        page.get_by_role("button", name="Submit").click()
        
        print("[DEBUG] Reached the check for 'Successfully registered'. 請掃描 QR Code...")
        expect(page.locator("body")).to_contain_text(re.compile(r"Successfully registered", re.IGNORECASE), timeout=60000)
        
    elif action == "unregister":
        page.get_by_role("button", name="Un-register iAM Smart").click()
        
        expect(page.locator("body")).to_contain_text(re.compile(r"Are you sure you want to un", re.IGNORECASE), timeout=5000)
        page.get_by_role("button", name="Yes").click()
        
        expect(page.locator("body")).to_contain_text(re.compile(r"Successfully unregistered", re.IGNORECASE), timeout=15000)
        
    else:
        raise ValueError("action must be 'register' or 'unregister'")

def ensure_iamsmart_unregistered(page):
    """Make sure the account starts UNBOUND. If it is already bound to iAM
    Smart the profile shows 'Un-register iAM Smart' instead of 'Register iAM
    Smart', which would break the bind test — so unregister it first. The bind
    state loads slowly, so wait for one of the two buttons before deciding."""
    open_profile_menu(page)
    page.get_by_text("My Profile info").last.click()

    register_btn = page.get_by_role("button", name="Register iAM Smart")
    unregister_btn = page.get_by_role("button", name="Un-register iAM Smart")
    for _ in range(15):
        page.wait_for_timeout(1000)
        if (register_btn.count() > 0 and register_btn.first.is_visible()) or (
            unregister_btn.count() > 0 and unregister_btn.first.is_visible()
        ):
            break

    if unregister_btn.count() > 0 and unregister_btn.first.is_visible():
        unregister_btn.first.click()
        expect(page.locator("body")).to_contain_text(
            re.compile(r"Are you sure you want to un", re.IGNORECASE), timeout=5000
        )
        page.get_by_role("button", name="Yes").click()
        expect(page.locator("body")).to_contain_text(
            re.compile(r"Successfully unregistered", re.IGNORECASE), timeout=15000
        )


def login_with_iam_smart(page, force_login=False):
    if force_login:
        import os
        base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
        page.context.clear_cookies()
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        page.goto(f"{base}/#/login")

    page.get_by_text("Continue with iAM Smart").click()

    print("[DEBUG] 請掃描 QR Code... 等待 Welcome back")
    expect(page.get_by_role("heading", name=re.compile(r"^Welcome back", re.IGNORECASE))).to_be_visible(timeout=60000)

def logout_from_profile_menu(page):
    open_profile_menu(page)
    # Click the dropdown's Logout item specifically (the page also has a sidebar
    # "Logout" menuitem, so get_by_text("Logout").nth(1) was unreliable).
    page.locator(".ant-dropdown-menu-item", has_text="Logout").first.click()
    expect(page).to_have_url(re.compile(r"/#/login"), timeout=15000)

