import os
from playwright.sync_api import sync_playwright
from flows.flow_login import login
from flows.flow_iam_smart import register_iamSmart

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        login(page)
        
        # Go to profile
        page.locator('//*[@id="ds-app"]/section/header/section/div[3]').click()
        page.get_by_text("My Profile info").click()
        
        # Click Register
        page.get_by_role("button", name="Register iAM Smart").click()
        
        password_input = page.get_by_role("textbox", name="Enter password")
        password_input.click()
        password_input.fill("Zxc12345")
        page.get_by_role("button", name="Submit").click()
        
        # Wait for navigation to apigw-isit.staging-eid.gov.hk
        page.wait_for_url("**/getQR**", timeout=10000)
        page.wait_for_timeout(2000)
        
        html = page.content()
        with open("mock_page.html", "w") as f:
            f.write(html)
            
        print("Mock page HTML saved.")
        
        browser.close()

if __name__ == "__main__":
    inspect()
