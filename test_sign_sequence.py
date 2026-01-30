import os

import pytest

from playwright.sync_api import expect

from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed
from pages.page_menu import Menu


def _build_sequence_signers(sender_position):
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")

    if sender_position is None:
        recipient_emails = [e for e in recipient_emails if e != sender_email]
    else:
        if not sender_email:
            pytest.skip("LOGIN_DEFAULT_EMAIL is required for sender-included scenario")
        recipient_emails = [e for e in recipient_emails if e != sender_email]
        if sender_position == "first":
            recipient_emails = [sender_email] + recipient_emails
        else:
            recipient_emails = recipient_emails + [sender_email]

    if not recipient_emails:
        pytest.skip("SIGN_EMAIL empty after scenario setup")
    sign_emails = list(dict.fromkeys(recipient_emails))
    return recipient_emails, sign_emails, sender_email


@pytest.mark.parametrize("sender_position", [None, "first", "last"])
def test_sign_sequence(page, sample_pdf_path, sender_position) -> None:
    print(f"[SCENARIO] sign_sequence sender_position={sender_position}")
    login(page)

    recipient_emails, sign_emails, sender_email = _build_sequence_signers(sender_position)
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=True,
        recipient_emails=recipient_emails,
    )
    if sender_email and sender_email in sign_emails:
        login(page, email=sender_email, force_login=True)
        expect(Menu(page).all_tab).to_be_visible()
        Menu(page).all_tab.click()
        row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
        expect(row).to_be_visible()
        expected_count = 1 if sender_position == "first" else 0
        expect(row.get_by_role("button", name="Sign")).to_have_count(expected_count)

    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email)
        
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    if sender_email:
        confirm_mail_received("Document signing completed", recipient="sender + all signers")
        login(page, email=sender_email, force_login=True)
        check_signing_completed(page, title=title)
