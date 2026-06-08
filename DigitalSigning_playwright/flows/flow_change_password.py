import os

from flows.flow_login import login

DEFAULT = os.getenv("LOGIN_DEFAULT_PASSWORD", "")
# Deterministic pool of unique, complexity-safe passwords used to cycle the
# history window (and to recover if a previous run left a non-default password).
_POOL = [DEFAULT + f"Qp{i}!9" for i in range(20)]


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


def _current_password(page):
    """Determine the password the account is currently on. Normally DEFAULT
    (the test already logged in); falls back to scanning the pool so a dirty
    state left by a previous run can self-heal."""
    if _logged_in(page):
        return DEFAULT
    login(page, force_login=True)
    if _logged_in(page):
        return DEFAULT
    for pw in _POOL:
        login(page, password=pw, force_login=True)
        if _logged_in(page):
            return pw
    return None


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


def _attempt(page, old, new) -> bool:
    """Submit a password change; detect the outcome from the toast message
    (robust to the inconsistent logout-after-change behaviour). Returns True on
    success (re-logging in with `new` if we were logged out), False if rejected."""
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
        if any(k in msgs for k in ["last 10", "not be the same", "invalid", "incorrect", "wrong"]):
            outcome = "rejected"
            break

    if outcome == "success":
        if "/#/login" in page.url or not _logged_in(page):
            login(page, password=new, force_login=True)
            assert _logged_in(page), "Could not log in after a password change"
        return True

    print(f"[change_password] rejected new=..{new[-4:]} :: {_toasts(page)}")
    _close_modal(page)
    return False


def change_password(page) -> dict:
    """Change the password to a new value, verify it works, then cycle through
    enough fresh passwords to legitimately set it back to the original default
    (the app forbids reusing any of the last 10 passwords)."""
    assert DEFAULT, "LOGIN_DEFAULT_PASSWORD must be set"

    current = _current_password(page)
    assert current, "Could not determine the current password"

    def _next_pool(after):
        for p in _POOL:
            if p != after:
                return p
        raise AssertionError("pool exhausted")

    # 1) Change to a fresh password and confirm the new one works.
    first = _next_pool(current)
    assert _attempt(page, current, first), "Initial password change was rejected"
    current = first

    # 2) Restore the default, cycling through fresh passwords whenever the
    #    last-10 policy blocks it.
    used = {current}
    for _ in range(len(_POOL)):
        if _attempt(page, current, DEFAULT):
            assert _logged_in(page)
            return {"changed": True, "restored": True}
        advanced = False
        for cand in _POOL:
            if cand in used:
                continue
            used.add(cand)
            if _attempt(page, current, cand):
                current = cand
                advanced = True
                break
        if not advanced:
            break

    raise AssertionError("Could not restore the default password within the pool")
