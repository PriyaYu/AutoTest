import os
import re
import random
from datetime import datetime
from playwright.sync_api import expect

from flows.flow_login import login
from flows.flow_iamsmart import register_iamSmart, login_with_iam_smart
from flows.flow_mail_check import confirm_mail_received
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed

def test_sign_parallel_iamsmart(page, sample_pdf_path) -> None:
    base = os.getenv("WEBSITE_URL", "https://sign.nextore.io")
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    password = os.getenv("LOGIN_DEFAULT_PASSWORD", "")
    
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")

    # 0. 預先驗證：確保測試環境乾淨，沒有殘留綁定的 iAM Smart 帳號
    page.goto(f"{base}/#/login")
    page.get_by_text("Continue with iAM Smart").click()
    
    # 給予 60 秒的時間讓使用者掃描 QR Code。
    # 同時監聽 "Welcome back" 或 "Could not find account"，只要其中一個出現就不會繼續白等 60 秒。
    is_bound = False
    print("[DEBUG] Waiting for user to scan iAM Smart QR code...")
    try:
        welcome_locator = page.get_by_role("heading", name=re.compile(r"^Welcome back", re.IGNORECASE))
        not_found_locator = page.get_by_text(re.compile(r"Could not find account", re.IGNORECASE))
        
        expect(welcome_locator.or_(not_found_locator).first).to_be_visible(timeout=60000)
        
        if welcome_locator.is_visible():
            is_bound = True
    except Exception as e:
        print(f"[DEBUG] Timeout waiting for QR scan: {e}")

    if is_bound:
        # 如果出現 Welcome back，代表可能成功登入了，我們就執行解除綁定
        print("[DEBUG] 'Welcome back' visible. Account might be already bound. Attempting to unregister.")
        try:
            register_iamSmart(page, action="unregister")
            print("[DEBUG] Successfully unregistered during pre-check.")
            page.context.clear_cookies()
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        except Exception as e:
            print(f"[DEBUG] Failed to unregister during pre-check: {e}")
    else:
        # 如果沒有出現 Welcome back，代表應該是乾淨狀態，確認是否出現 Could not find account
        expect(page.locator("body")).to_contain_text(re.compile(r"Could not find account", re.IGNORECASE))
        print("[DEBUG] 'Could not find account' verified. Environment is clean.")

    # 回到登入頁，準備開始正式的註冊流程
    page.goto(f"{base}/#/login")

    # 1. 建立新的 iAM Smart 帳號
    page.get_by_text("Sign Up").click()
    page.get_by_text("Sign Up with iAM Smart").click()
    
    new_account_email = f"zihsyuan0603+{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
    
    page.get_by_role("textbox").nth(1).fill(new_account_email)
    page.get_by_role("textbox").nth(2).fill("PM")
    page.get_by_role("textbox").nth(3).fill(password)
    page.get_by_role("textbox").nth(4).fill(password)
    page.get_by_role("button", name="Confirm").click()

    page.wait_for_timeout(3000)
    
    # 2. 登入發件者帳號 (一般登入) 以發起平行簽署
    login(page, email=sender_email, password=password, force_login=True)
    
    # 組合收件者名單
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    
    # 加上剛剛新註冊的 iAM Smart 帳號
    recipient_emails.append(new_account_email)
    
    # 根據 test_sign_parallel.py 的邏輯過濾掉 sender 自身
    recipient_emails = [e for e in recipient_emails if e != sender_email]
    
    # 移除重複的 Email
    sign_emails = list(dict.fromkeys(recipient_emails))
    
    # 發起簽署
    page.goto(f"{base}/#/dashboard")
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=False,
        recipient_emails=recipient_emails,
    )
    print(f"[DEBUG] Initiated parallel signing request with title: {title}")

    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email, title=title)

    # 3. 各個收件者進行簽署 (隨機順序)
    for email in random.sample(sign_emails, k=len(sign_emails)):
        if email == new_account_email:
            # 使用剛剛註冊的 iAM Smart 帳號登入並簽署
            print(f"[DEBUG] Signing with newly registered iAM Smart account: {email}")
            login_with_iam_smart(page, force_login=True)
            sign_by_title(page, title=title, signer_email=email, use_iamsmart=True)
            
            # 簽署完畢後，解除綁定 iAM Smart
            try:
                register_iamSmart(page, action="unregister")
                print(f"[DEBUG] Unregistered iAM Smart for {email}")
            except Exception as e:
                print(f"[DEBUG] Failed to unregister iAM Smart for {email}: {e}")
        else:
            # 其他帳號一般登入與簽署
            print(f"[DEBUG] Signing with regular account: {email}")
            login(page, email=email, password=password, force_login=True)
            sign_by_title(page, title=title, signer_email=email, use_iamsmart=False)

    # 4. 驗證簽署已完成
    confirm_mail_received("Document signing completed", recipient="sender + all signers", title=title)
    login(page, email=sender_email, password=password, force_login=True)
    check_signing_completed(page, title=title)
