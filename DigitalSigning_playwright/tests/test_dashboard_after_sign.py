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


def _poll_stat(page, key: str, target: int, timeout: float = 45.0) -> int:
    """The dashboard stats refresh asynchronously and may briefly read the old
    (stable) value, so poll — reloading to force a refetch — until `key` reaches
    `target` or it times out."""
    deadline = time.time() + timeout
    val = None
    while time.time() < deadline:
        val = _dashboard_stats(page)[key]
        if val == target:
            return val
        page.reload()
        page.wait_for_timeout(2000)
    return val


def test_dashboard_after_sign(page, sample_pdf_path) -> None:
    """A signing request moves the dashboard stats: a signer's "Inbox" rises by 1
    when they receive the request, and the sender's "Completed" rises by 1 once
    every signer has signed."""
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    # Sender is the dashboard owner, not a signer, so its delta reflects a sent
    # document completing.
    recipient_emails = [e for e in recipient_emails if e != sender_email]
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required and must contain a non-sender signer")
    sign_emails = list(dict.fromkeys(recipient_emails))
    inbox_signer = sign_emails[0]

    # Baselines: the chosen signer's Inbox and the sender's Completed.
    login(page, email=inbox_signer)
    inbox_before = _dashboard_stats(page)["Inbox"]
    login(page, email=sender_email, force_login=True)
    completed_before = _dashboard_stats(page)["Completed"]

    # Send a parallel request to the signers.
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=False,
        recipient_emails=recipient_emails,
    )
    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email, title=title)

    # Receiving the request must raise the signer's Inbox by 1.
    login(page, email=inbox_signer, force_login=True)
    inbox_after = _poll_stat(page, "Inbox", inbox_before + 1)
    assert inbox_after == inbox_before + 1, (
        f"signer '{inbox_signer}' dashboard 'Inbox' should be +1 on receipt: "
        f"before={inbox_before} after={inbox_after}"
    )

    # Everyone signs.
    for email in sign_emails:
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    # Back as the sender: the request is now Completed -> "Completed" stat +1.
    login(page, email=sender_email, force_login=True)
    check_signing_completed(page, title=title)
    completed_after = _poll_stat(page, "Completed", completed_before + 1)
    assert completed_after == completed_before + 1, (
        f"sender dashboard 'Completed' should be +1 after a signing completes: "
        f"before={completed_before} after={completed_after}"
    )
