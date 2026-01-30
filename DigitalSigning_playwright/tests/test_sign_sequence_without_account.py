import os
from datetime import datetime

from playwright.sync_api import expect

from flows.flow_activate_account import activate_account
from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received, prompt_verify_url
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed
from pages.page_menu import Menu


def test_sign_parallel(page, sample_pdf_path) -> None:
    login(page)

    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    base_alias = os.getenv("SIGNUP_ALIAS_BASE", "")
    appended_email = f"{base_alias}+{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
    recipient_emails.append(appended_email)
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required but not set")
    sign_emails = list(dict.fromkeys(recipient_emails))
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=True,
        recipient_emails=recipient_emails,
    )
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if sender_email and sender_email in sign_emails:
        login(page, email=sender_email, force_login=True)
        expect(Menu(page).all_tab).to_be_visible()
        Menu(page).all_tab.click()
        row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
        expect(row).to_be_visible()
        expect(row.get_by_role("button", name="Sign")).to_have_count(0)

    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email)
        if email == appended_email:
            verify_url = prompt_verify_url()
            activate_account(page, verify_url=verify_url)
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")
    confirm_mail_received("Document signing completed", recipient="sender + all signers")
    login(page, email=sender_email, force_login=True)
    check_signing_completed(page, title=title)
