import os

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from flows.flow_sign import sign_by_title
from pages.page_menu import Menu


def test_sign_sequence_validation(page, sample_pdf_path) -> None:

    login(page)
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=True,
    )
    print(f"[DEBUG] title: {title}")

    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    print(f"[DEBUG] SIGN_EMAIL raw: {sign_emails_raw!r}")
    sign_emails = list(dict.fromkeys(e.strip() for e in sign_emails_raw.split(",") if e.strip()))
    if not sign_emails:
        raise ValueError("SIGN_EMAIL is required but not set")

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
        row = open_all_and_get_row()
        actual_row = row.count()
        actual_sign = row.first.get_by_role("button", name="Sign").count() if actual_row > 0 else 0
        print(
            f"[CHECK] {label} | expect row={expect_row}, sign={expect_sign} | "
            f"actual row={actual_row}, sign={actual_sign}"
        )
        if actual_row != expect_row or actual_sign != expect_sign:
            input("[PAUSE] mismatch detected. Press Enter to continue...")
        return row

    sender_email = os.getenv("SENDER_MAIL") or os.getenv("LOGIN_DEFAULT_EMAIL", "")
    print(f"[DEBUG] sender_email: {sender_email}")
    print(f"[DEBUG] sign_emails: {sign_emails}")

    for i, signer_email in enumerate(sign_emails):
        print(f"[DEBUG] ===== sequence index {i} =====")
        print(f"[DEBUG] expected signer: {signer_email}")

        if sender_email:
            login(page, email=sender_email, force_login=True)
            sender_should_have_sign = sender_email == sign_emails[i]
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
        sign_by_title(page, title=title)
        print("[DEBUG] sign_by_title done")
