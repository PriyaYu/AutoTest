
import os
import random

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received
from flows.flow_review import review_action


def test_review_approval(page, sample_pdf_path) -> None:
    reviewee_email = os.getenv("REVIEWEE_EMAIL", "")
    reviewer_emails_raw = os.getenv("REVIEWER_EMAIL", "")
    reviewer_emails = [e.strip() for e in reviewer_emails_raw.split(",") if e.strip()]

    reviewer_email = random.choice(reviewer_emails) if reviewer_emails else ""
    if not reviewee_email:
        raise ValueError("REVIEWEE_EMAIL is required but not set")
    if not reviewer_email:
        raise ValueError("REVIEWER_EMAIL is required but not set")

    login(page, email=reviewee_email)
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required but not set")

    initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        recipient_emails=recipient_emails,
        IsSequence=False,
    )

    for email in reviewer_emails:
        confirm_mail_received("A document requires your review", recipient=email)

    login(page, email=reviewer_email, force_login=True)
    review_action(page, action="approve")

    confirm_mail_received("Document review result", recipient=reviewee_email)
