def confirm_mail_received(subject: str, recipient: str = "") -> None:
    if not subject:
        raise ValueError("subject is required but not set")

    recipient_part = recipient if recipient else "-"
    prompt = (
        f'[Mail Notification] Confirm subject="{subject}" recipient="{recipient_part}" (Y/N): '
    )
    mail_ready = input(prompt).strip()
    if mail_ready.lower() not in {"y", "yes"}:
        print("[Mail Notification] Email not received yet; continuing as requested.")


def prompt_verify_url() -> str:
    verify_url = input("[Mail Notification] Paste verify URL from email (run pytest -s): ").strip()
    if not verify_url:
        raise ValueError("verify URL is required but not set")
    return verify_url
