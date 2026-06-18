import os
import time

from flows.flow_login import login
from flows.flow_dashboard import _read_dashboard_stats
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed
from flows.flow_mail_check import confirm_mail_received
from pages.page_menu import Menu


def _dashboard_stats(page) -> dict:
    Menu(page).dashboard_tab.click()
    return _read_dashboard_stats(page)


def test_dashboard_after_sign(page, sample_pdf_path) -> None:
    """A completed signing must move the sender's dashboard: the "Completed" stat
    increments by exactly 1."""
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    # Sender is the dashboard owner, not a signer, so the delta reflects a sent
    # document completing.
    recipient_emails = [e for e in recipient_emails if e != sender_email]
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required and must contain a non-sender signer")
    sign_emails = list(dict.fromkeys(recipient_emails))

    # Baseline dashboard for the sender.
    login(page, email=sender_email)
    before = _dashboard_stats(page)

    # Send a parallel request and have every signer sign it.
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=False,
        recipient_emails=recipient_emails,
    )
    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email, title=title)
    for email in sign_emails:
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    # Back as the sender: the request is now Completed.
    login(page, email=sender_email, force_login=True)
    check_signing_completed(page, title=title)

    # The dashboard stat refreshes asynchronously and may briefly read the old
    # (stable) value, so poll — reloading to force a refetch — until "Completed"
    # reflects the new completion.
    target = before["Completed"] + 1
    after_completed = before["Completed"]
    deadline = time.time() + 45
    while time.time() < deadline:
        after_completed = _dashboard_stats(page)["Completed"]
        if after_completed == target:
            break
        page.reload()
        page.wait_for_timeout(2000)

    assert after_completed == target, (
        f"dashboard 'Completed' should be +1 after a signing completes: "
        f"before={before['Completed']} after={after_completed}"
    )
