import os
import random

import pytest

from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed


def _build_parallel_signers(include_sender: bool):
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if include_sender:
        if not sender_email:
            pytest.skip("LOGIN_DEFAULT_EMAIL is required for sender-included scenario")
        recipient_emails = [e for e in recipient_emails if e != sender_email]
        recipient_emails.append(sender_email)
    else:
        recipient_emails = [e for e in recipient_emails if e != sender_email]
    if not recipient_emails:
        pytest.skip("SIGN_EMAIL empty after scenario setup")
    sign_emails = list(dict.fromkeys(recipient_emails))
    return recipient_emails, sign_emails, sender_email


@pytest.mark.parametrize("include_sender", [True, False])
def test_sign_parallel(page, sample_pdf_path, include_sender) -> None:
    print(f"[SCENARIO] sign_parallel include_sender={include_sender}")
    login(page)
    recipient_emails, sign_emails, sender_email = _build_parallel_signers(include_sender)
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=False,
        recipient_emails=recipient_emails,
    )

    for email in sign_emails:
        confirm_mail_received("You have a document to sign", recipient=email, title=title)

    for email in random.sample(sign_emails, k=len(sign_emails)):
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    if sender_email:
        confirm_mail_received("Document signing completed", recipient="sender + all signers", title=title)
        login(page, email=sender_email, force_login=True)
        check_signing_completed(page, title=title)
