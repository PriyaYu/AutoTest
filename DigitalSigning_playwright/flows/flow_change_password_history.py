import os

from flows.flow_login import login

# How many recent passwords the app forbids reusing.
_HISTORY_SIZE = 10
# Unique, policy-compliant passwords (no consecutive numbers/phrases).
_POOL = [f"Zq{chr(65 + i)}m$Wk7" for i in range(18)]


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


def _open_form(page):
    old_pw = page.locator("#basic_oldPassword")
    if old_pw.count() > 0 and old_pw.first.is_visible():
        return  # reuse a modal left open by a rejected attempt
    page.locator(".user-wrap").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Change password").first.click()
    old_pw.wait_for(state="visible", timeout=15000)


def _close_modal(page):
    close = page.locator(".ant-modal-close")
    if close.count() > 0 and close.first.is_visible():
        close.first.click()
    else:
        page.keyboard.press("Escape")
    page.wait_for_timeout(500)


def _attempt(page, email, old, new) -> bool:
    """Submit a change; True on success (re-logging in with `new`), False if
    rejected. Outcome is read from the toast (logout after change is flaky)."""
    _open_form(page)
    page.locator("#basic_oldPassword").fill(old)
    page.locator("#basic_password").fill(new)
    page.locator("#basic_confirmPassword").fill(new)
    page.get_by_role("button", name="Submit").click()

    outcome = None
    for _ in range(30):  # ~9s
        page.wait_for_timeout(300)
        if "/#/login" in page.url:
            outcome = "success"
            break
        msgs = " | ".join(_toasts(page))
        if "success" in msgs:
            outcome = "success"
            break
        if any(k in msgs for k in ["last 10", "not be the same", "invalid", "incorrect", "wrong", "consecutive"]):
            outcome = "rejected"
            break

    if outcome == "success":
        if "/#/login" in page.url or not _logged_in(page):
            login(page, email=email, password=new, force_login=True)
            assert _logged_in(page), "could not log in after a password change"
        return True

    _close_modal(page)
    return False


def change_password_history(page, email, old_password) -> dict:
    """Validate the "must not match last 10 passwords" policy on a throwaway
    account: after changing away, the original is rejected until enough fresh
    passwords push it out of the history window, then it is accepted again."""
    login(page, email=email, password=old_password, force_login=True)
    assert _logged_in(page), f"could not log in with the new account {email}"

    # Change to a fresh password.
    assert _attempt(page, email, old_password, _POOL[0]), "initial password change was rejected"
    current = _POOL[0]

    # Reusing the original immediately must be blocked by the last-10 policy.
    assert not _attempt(page, email, current, old_password), (
        "expected the original password to be rejected by the last-10 policy"
    )

    # Cycle through fresh passwords; the original must become reusable once it
    # falls out of the last-10 window.
    pi = 1
    for _ in range(len(_POOL)):
        if _attempt(page, email, current, old_password):
            assert _logged_in(page)
            return {"email": email, "cycles": pi}
        while pi < len(_POOL):
            candidate = _POOL[pi]
            pi += 1
            if candidate != current and _attempt(page, email, current, candidate):
                current = candidate
                break
        else:
            break

    raise AssertionError("the original password never became reusable after cycling")
