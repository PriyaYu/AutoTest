import os
from playwright.sync_api import sync_playwright
from flows.flow_login import login
from flows.flow_iamsmart import register_iamSmart

def cleanup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        login(page)
        
        # Unregister if registered
        try:
            register_iamSmart(page, action="unregister")
            print("Successfully unregistered.")
        except Exception as e:
            print("Already unregistered or Error:", e)
            
        browser.close()

if __name__ == "__main__":
    cleanup()
