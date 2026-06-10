import os

from flows.flow_login import login

# A policy-compliant new password (no consecutive numbers/phrases). Overridable.
NEW_PASSWORD = os.getenv("CHANGE_PASSWORD_NEW", "Kp9$mWq3z")


def _logged_in(page) -> bool:
    try:
        page.get_by_role("menuitem", name="Dashboard").wait_for(state="visible", timeout=15000)
        return True
    except Exception:
        return False


def _toasts(page):
    return page.evaluate(
        r"""() => [...document.querySelectorAll(
            '.ant-message-notice, .ant-message-custom-content, .ant-notification-notice, [role=alert], .ant-form-item-explain, .ant-form-item-explain-error'
        )].map(e => (e.textContent||'').trim().toLowerCase()).filter(Boolean)"""
    )


def _submit_change(page, old, new) -> bool:
    """Open the Change password dialog, submit, and detect the outcome from the
    toast (a successful change logs out / shows a success toast)."""
    page.locator(".user-wrap").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Change password").first.click()
    page.locator("#basic_oldPassword").wait_for(state="visible", timeout=15000)
    page.locator("#basic_oldPassword").fill(old)
    page.locator("#basic_password").fill(new)
    page.locator("#basic_confirmPassword").fill(new)
    page.get_by_role("button", name="Submit").click()

    for _ in range(30):  # ~9s
        page.wait_for_timeout(300)
        if "/#/login" in page.url:
            return True
        msgs = " | ".join(_toasts(page))
        if "success" in msgs:
            return True
        if any(k in msgs for k in ["last 10", "not be the same", "invalid", "incorrect", "wrong", "consecutive"]):
            return False
    return False


def change_password(page, email, old_password) -> dict:
    """Change the password of a freshly created (throwaway) account and verify
    the new password works while the old one no longer does. No restore needed
    since the account is disposable."""
    new_password = NEW_PASSWORD
    assert new_password != old_password, "new password must differ from the old one"

    # Log in as the new account.
    login(page, email=email, password=old_password, force_login=True)
    assert _logged_in(page), f"could not log in with the new account {email}"

    # Change the password.
    assert _submit_change(page, old_password, new_password), "password change was rejected"

    # The new password must work...
    login(page, email=email, password=new_password, force_login=True)
    assert _logged_in(page), "new password did not work after change"

    # ...and the old one must not.
    login(page, email=email, password=old_password, force_login=True)
    assert not _logged_in(page), "old password still works after change"

    return {"email": email, "new": new_password}
