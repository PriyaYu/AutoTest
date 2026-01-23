
import os
import random

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
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
    initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        recipient_emails=[reviewer_email],
        IsSequence=False,
    )

    login(page, email=reviewer_email)
    review_action(page, action="approve")
