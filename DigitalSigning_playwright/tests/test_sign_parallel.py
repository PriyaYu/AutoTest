import os
import random

from flows.flow_login import login
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title


def test_sign_parallel(page, sample_pdf_path) -> None:
    login(page)
    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=False,
    )

    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    sign_emails = list(dict.fromkeys(e.strip() for e in sign_emails_raw.split(",") if e.strip()))
    if not sign_emails:
        raise ValueError("SIGN_EMAIL is required but not set")

    for email in random.sample(sign_emails, k=len(sign_emails)):
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title)
