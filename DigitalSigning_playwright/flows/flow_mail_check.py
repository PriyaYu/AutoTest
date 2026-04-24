import os
from flows.flow_signup import _focus_terminal, _focus_browser

def confirm_mail_received(subject: str, recipient: str = "") -> None:
    if not subject:
        raise ValueError("subject is required but not set")

    recipient_part = recipient if recipient else "-"
    
    # 新增 Config: 如果設定了 AUTO_CONFIRM_MAIL，就自動順跑不暫停
    auto_confirm = os.getenv("AUTO_CONFIRM_MAIL", "0").lower() in {"1", "true", "yes"}
    if auto_confirm:
        print(f'[Mail Notification] Auto-confirmed subject="{subject}" recipient="{recipient_part}"')
        return

    prompt = (
        f'[Mail Notification] Confirm subject="{subject}" recipient="{recipient_part}" (Y/N): '
    )
    _focus_terminal()
    mail_ready = input(prompt).strip()
    _focus_browser()
    if mail_ready.lower() not in {"y", "yes"}:
        print("[Mail Notification] Email not received yet; continuing as requested.")


def prompt_verify_url() -> str:
    _focus_terminal()
    verify_url = input("[Mail Notification] Paste verify URL from email (run pytest -s): ").strip()
    _focus_browser()
    if not verify_url:
        raise ValueError("verify URL is required but not set")
    return verify_url
