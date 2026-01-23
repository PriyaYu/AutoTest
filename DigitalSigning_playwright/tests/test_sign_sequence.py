import os

from playwright.sync_api import expect

from flows.flow_login import login
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from pages.page_menu import Menu


def test_sign_parallel(page, sample_pdf_path) -> None:
    login(page)

    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=True,
    )
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    sign_emails = list(dict.fromkeys(e.strip() for e in sign_emails_raw.split(",") if e.strip()))
    if not sign_emails:
        raise ValueError("SIGN_EMAIL is required but not set")
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if sender_email and sender_email in sign_emails:
        login(page, email=sender_email, force_login=True)
        expect(Menu(page).all_tab).to_be_visible()
        Menu(page).all_tab.click()
        row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
        expect(row).to_be_visible()
        expect(row.get_by_role("button", name="Sign")).to_have_count(0)

    for email in sign_emails:
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title)
