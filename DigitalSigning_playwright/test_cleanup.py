import os
import time
from playwright.sync_api import sync_playwright

def cleanup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Login
        page.goto("https://sign.nextore.io/#/login")
        page.get_by_role("textbox", name="Email").fill("pyu@nexify.com.hk")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("textbox", name="Password").fill("Zxc12345")
        page.get_by_role("button", name="Login").click()
        
        page.wait_for_timeout(3000)
        
        # Go to profile
        page.locator('//*[@id="ds-app"]/section/header/section/div[3]').click()
        page.get_by_text("My Profile info").click()
        
        page.wait_for_timeout(2000)
        
        # Unregister if registered
        try:
            btn = page.get_by_role("button", name="Un-register iAM Smart")
            if btn.is_visible():
                btn.click()
                page.get_by_role("button", name="Yes").click()
                page.wait_for_timeout(2000)
                print("Successfully unregistered.")
            else:
                print("Not registered.")
        except Exception as e:
            print("Error:", e)
            
        browser.close()

if __name__ == "__main__":
    cleanup()
