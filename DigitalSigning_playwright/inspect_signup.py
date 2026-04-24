import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        base = "https://sign.nextore.io"
        page.goto(f"{base}/#/login")
        page.get_by_text("Sign Up").click()
        page.get_by_text("Sign Up with iAM Smart").click()
        
        page.wait_for_url("**/getQR**", timeout=10000)
        time.sleep(2)
        
        html = page.content()
        with open("mock_signup.html", "w") as f:
            f.write(html)
            
        browser.close()

if __name__ == "__main__":
    inspect()
