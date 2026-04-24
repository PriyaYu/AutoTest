import os
import re
from datetime import datetime
from playwright.sync_api import expect

from flows.flow_iamsmart import register_iamSmart

def test_signup_iamsmart_flow(page) -> None:
    base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
    password = os.getenv("LOGIN_DEFAULT_PASSWORD", "Zxc12345")
    
    # 0. 預先驗證：確保測試環境乾淨，沒有殘留綁定的 iAM Smart 帳號
    page.goto(f"{base}/#/login")
    page.get_by_text("Continue with iAM Smart").click()
    
    print("[DEBUG] 請掃描 QR Code 進行登入預先驗證...")
    try:
        # 給予 60 秒的時間掃描。先用 iamsmart登入看看，如果有 Could not find account 代表是乾淨的狀態
        expect(page.locator("body")).to_contain_text(re.compile(r"Could not find account", re.IGNORECASE), timeout=60000)
        print("[DEBUG] 'Could not find account' verified. Environment is clean.")
    except Exception:
        # 如果沒有出現，代表可能成功登入了，我們就執行解除綁定
        print("[DEBUG] Account might be already bound. Attempting to unregister.")
        try:
            register_iamSmart(page, action="unregister")
            print("[DEBUG] Successfully unregistered during pre-check.")
        except Exception as e:
            print(f"[DEBUG] Failed to unregister during pre-check: {e}")

    # 回到登入頁，準備開始正式的註冊流程
    page.goto(f"{base}/#/login")
    
    # 1. 前往註冊
    page.get_by_text("Sign Up").click()
    
    # 2. 點擊使用 iAM Smart 註冊
    page.get_by_text("Sign Up with iAM Smart").click()
    
    # 3. 自動跳轉回系統，驗證到達 Create Account 頁面
    expect(page.get_by_role("heading", name="Create Account")).to_be_visible(timeout=15000)
    
    # 為了避免重複執行測試時出現「Email已被註冊」的錯誤，使用動態 Email
    email = f"zihsyuan0603+{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
    
    # 4. 填寫註冊資料
    page.get_by_role("textbox").nth(1).fill(email)
    page.get_by_role("textbox").nth(2).fill("PM")
    page.get_by_role("textbox").nth(3).fill(password)
    page.get_by_role("textbox").nth(4).fill(password)
    page.get_by_role("button", name="Confirm").click()

    page.wait_for_timeout(3000)
    page.goto(f"{base}/#/login")
    
    # 6. 使用 iAM Smart 登入
    page.get_by_text("Continue with iAM Smart").click()
    
    # 驗證成功登入
    expect(page.get_by_role("heading")).to_contain_text(re.compile(r"Welcome back", re.IGNORECASE), timeout=15000)

    # 7. 取消 bind (復原測試環境)
    try:
        register_iamSmart(page, action="unregister")
    except Exception as e:
        print(f"取消綁定時發生錯誤（或已經取消）：{e}")
