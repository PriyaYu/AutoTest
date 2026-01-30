import os
import random

from playwright.sync_api import expect

from flows.flow_check_completed_signing import check_signing_completed
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received
from flows.flow_sign import sign_by_title
from pages.page_initiate_signing_request import InitiateSigningRequestPage


def test_use_draft_sent_signing_request(page, sample_pdf_path) -> None:
    login(page)
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required but not set")
    sign_emails = list(dict.fromkeys(recipient_emails))

    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        mode="draft",
        recipient_emails=recipient_emails,
    )

    flow = InitiateSigningRequestPage(page)
    flow.menu.drafts_tab.click()
    search_box = page.get_by_role("textbox", name="Search Draft")
    expect(search_box).to_be_visible()
    search_box.fill(title)
    search_box.press("Enter")
    row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
    expect(row).to_be_visible()
    row.get_by_role("button", name="Use").click()

    for idx in range(len(sign_emails)):
        flow.signature_field_buttons.nth(idx).click()

    flow.send_button.click()
    flow.confirm_yes_button.click()
    flow.ok_button.click()

    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email)

    for email in random.sample(sign_emails, k=len(sign_emails)):
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")
    confirm_mail_received("Document signing completed", recipient="sender + all signers")
    login(page, email=sender_email, force_login=True)
    check_signing_completed(page, title=title)
