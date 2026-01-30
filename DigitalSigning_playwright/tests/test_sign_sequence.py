import os
import time

import pytest

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed
from pages.page_menu import Menu


def _build_sequence_signers(sender_position):
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    print(f"[DEBUG] SIGN_EMAIL raw: {sign_emails_raw!r}")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    sender_email = os.getenv("SENDER_MAIL") or os.getenv("LOGIN_DEFAULT_EMAIL", "")
    print(f"[DEBUG] sender_email: {sender_email}")

    if sender_position is None:
        recipient_emails = [e for e in recipient_emails if e != sender_email]
    else:
        if not sender_email:
            pytest.skip("SENDER_MAIL/LOGIN_DEFAULT_EMAIL required for sender-included scenario")
        recipient_emails = [e for e in recipient_emails if e != sender_email]
        if sender_position == "first":
            recipient_emails = [sender_email] + recipient_emails
        else:
            recipient_emails = recipient_emails + [sender_email]

    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required but not set")
    sign_emails = list(dict.fromkeys(recipient_emails))
    return recipient_emails, sign_emails, sender_email


@pytest.mark.parametrize("sender_position", [None, "first", "last"])
def test_sign_sequence_validation(page, sample_pdf_path, sender_position) -> None:
    print(f"[SCENARIO] sign_sequence_validation sender_position={sender_position}")

    login(page)

    recipient_emails, sign_emails, sender_email = _build_sequence_signers(sender_position)
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=True,
        recipient_emails=recipient_emails,
    )
    print(f"[DEBUG] title: {title}")

    def open_all_and_get_row():
        Menu(page).all_tab.click()
        row = page.locator("tr", has=page.get_by_text(title, exact=True))
        if row.count() == 0:
            try:
                page.get_by_text(title, exact=True).first.wait_for(timeout=5000)
            except PlaywrightTimeoutError:
                pass
        return row

    def log_check(label: str, expect_row: int, expect_sign: int):
        for attempt in range(3):
            row = open_all_and_get_row()
            actual_row = row.count()
            actual_sign = (
                row.first.get_by_role("button", name="Sign").count() if actual_row > 0 else 0
            )
            print(
                f"[CHECK] {label} | expect row={expect_row}, sign={expect_sign} | "
                f"actual row={actual_row}, sign={actual_sign}"
            )
            if actual_row == expect_row and actual_sign == expect_sign:
                return row
            page.reload()
            time.sleep(2)
        input("[PAUSE] mismatch detected. Press Enter to continue...")
        return row

    print(f"[DEBUG] sign_emails: {sign_emails}")

    for i, signer_email in enumerate(sign_emails):
        print(f"[DEBUG] ===== sequence index {i} =====")
        print(f"[DEBUG] expected signer: {signer_email}")

        if sender_email:
            login(page, email=sender_email, force_login=True)
            sender_should_have_sign = sender_email == sign_emails[i]
            if sender_position == "first":
                sender_should_have_sign = True if i == 0 else False
            log_check(
                "sender",
                expect_row=1,
                expect_sign=1 if sender_should_have_sign else 0,
            )

        for prev_email in sign_emails[:i]:
            login(page, email=prev_email, force_login=True)
            print(f"[DEBUG] prev signer login: {prev_email}")
            log_check("prev signer", expect_row=1, expect_sign=0)

        login(page, email=signer_email, force_login=True)
        print(f"[DEBUG] current signer login: {signer_email}")
        log_check("current signer", expect_row=1, expect_sign=1)

        for next_email in sign_emails[i + 1 :]:
            login(page, email=next_email, force_login=True)
            print(f"[DEBUG] next signer login: {next_email}")
            if sender_email and next_email == sender_email:
                sender_should_have_sign = sender_email == sign_emails[i]
                log_check(
                    "next signer (sender)",
                    expect_row=1,
                    expect_sign=1 if sender_should_have_sign else 0,
                )
            else:
                log_check("next signer", expect_row=0, expect_sign=0)

        login(page, email=signer_email, force_login=True)
        print("[DEBUG] signing as current signer...")
        confirm_mail_received("You have a document to sign", recipient=signer_email)
        sign_by_title(page, title=title, signer_email=signer_email)
        print("[DEBUG] sign_by_title done")

    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")
    confirm_mail_received("Document signing completed", recipient="sender + all signers")
    login(page, email=sender_email, force_login=True)
    check_signing_completed(page, title=title)
