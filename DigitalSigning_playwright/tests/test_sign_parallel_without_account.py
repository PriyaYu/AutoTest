import os
import random
from datetime import datetime

from flows.flow_activate_account import activate_account
from flows.flow_login import login
from flows.flow_mail_check import confirm_mail_received, prompt_verify_url
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_sign import sign_by_title
from flows.flow_check_completed_signing import check_signing_completed


def test_sign_parallel(page, sample_pdf_path) -> None:
    login(page)
    sign_emails_raw = os.getenv("SIGN_EMAIL", "")
    recipient_emails = [e.strip() for e in sign_emails_raw.split(",") if e.strip()]
    base_alias = os.getenv("SIGNUP_ALIAS_BASE", "")
    appended_email = f"{base_alias}+{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
    recipient_emails.append(appended_email)
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required but not set")
    sign_emails = list(dict.fromkeys(recipient_emails))

    _, title = initiate_signing_request(
        page=page,
        pdf_path=sample_pdf_path,
        IsSequence=False,
        recipient_emails=recipient_emails,
    )

    for email in sign_emails:
        if email != appended_email:
            confirm_mail_received("Document Signing task", recipient=email)
        else:
            confirm_mail_received("You have a document to sign", recipient=email)

    for email in random.sample(sign_emails, k=len(sign_emails)):
        if email == appended_email:
            # NOTE: The appended account ({SIGNUP_ALIAS_BAS}+YYYYMMDDHHMMSS@gmail.com) must manually
            # check the inbox and sign; email receiving is not automated yet.
            # NOTE: Inbox email sample:
            # "Dear User, Please go to for signing Document: https://sign.nextore.io/DS#/verify-otp?token=..."
            verify_url = prompt_verify_url()
            activate_account(page, verify_url=verify_url)
        
        login(page, email=email, force_login=True)
        sign_by_title(page, title=title, signer_email=email)

    sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
    if not sender_email:
        raise ValueError("LOGIN_DEFAULT_EMAIL is required but not set")
    confirm_mail_received("Document signing completed", recipient="sender + all signers")
    login(page, email=sender_email, force_login=True)
    check_signing_completed(page, title=title)
