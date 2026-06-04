import os
import time

from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from pages.page_initiate_signing_request import InitiateSigningRequestPage
from pages.page_menu import Menu


def _resilient_tab(page, tab):
    """Click a sidebar tab, getting past the dashboard upload overlay that can
    intercept the first menu click after login."""
    for _ in range(3):
        try:
            tab.click(timeout=8000)
            return
        except Exception:
            page.wait_for_timeout(1500)
    tab.click(force=True)


def _open_sent_row(page, title, attempts: int = 3):
    """Find the sent request's row. The Sent list loads asynchronously, so we
    wait patiently for the filtered result instead of reloading on every miss
    (reloading mid-load just restarts the load). Reload only as a bounded
    last resort in case the request is still propagating to the list."""
    search = page.get_by_role("textbox", name="Search Sent")
    expect(search).to_be_visible(timeout=15000)
    page.wait_for_timeout(2000)  # let the Sent list settle before the first search
    row = page.locator("tr.vxe-body--row", has=page.get_by_text(title, exact=True))
    for attempt in range(attempts):
        search.fill(title)
        search.press("Enter")
        for _ in range(20):
            page.wait_for_timeout(1000)
            if row.count() > 0:
                expect(row.first).to_be_visible(timeout=10000)
                return row.first
        if attempt < attempts - 1:
            page.reload()
            _resilient_tab(page, Menu(page).sent_tab)
            page.wait_for_timeout(3000)
    raise AssertionError(f"Sent request not found: {title}")


def _inbox_presence(page, title, want_present: bool, timeout: float = 90.0) -> bool:
    """Poll the current account's Inbox until `title` presence matches
    `want_present` (no reloading — the list loads asynchronously)."""
    _resilient_tab(page, Menu(page).inbox_tab)
    search = page.get_by_role("textbox", name="Search Inbox")
    expect(search).to_be_visible(timeout=15000)
    page.wait_for_timeout(2000)
    deadline = time.time() + timeout
    while time.time() < deadline:
        search.fill(title)
        search.press("Enter")
        page.wait_for_timeout(2500)
        present = page.get_by_text(title, exact=True).count() > 0
        if present == want_present:
            return True
    return False


def cancel_delete_request(page, pdf_path) -> dict:
    flow = InitiateSigningRequestPage(page)
    sender = os.getenv("LOGIN_DEFAULT_EMAIL", "") or None
    recipients = [e.strip() for e in os.getenv("SIGN_EMAIL", "").split(",") if e.strip()]
    assert recipients, "SIGN_EMAIL must contain at least one recipient"
    recipient = recipients[0]

    # 1) Create and send a signing request.
    _, title = initiate_signing_request(page=page, pdf_path=pdf_path)

    # 2) The recipient should receive it in their Inbox.
    login(page, email=recipient, force_login=True)
    assert _inbox_presence(page, title, want_present=True), (
        f"'{title}' did not reach the recipient's Inbox after send"
    )

    # 3) Sender cancels & deletes the request from Sent.
    login(page, email=sender, force_login=True)
    _resilient_tab(page, flow.menu.sent_tab)
    row = _open_sent_row(page, title)
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Cancel & Delete").first.click()
    page.get_by_role("button", name="Delete", exact=True).click()

    search = page.get_by_role("textbox", name="Search Sent")
    search.fill(title)
    search.press("Enter")
    page.wait_for_timeout(2000)
    expect(page.get_by_text(title, exact=True)).to_have_count(0, timeout=15000)

    # 4) The request must also be gone from the recipient's Inbox.
    login(page, email=recipient, force_login=True)
    assert _inbox_presence(page, title, want_present=False), (
        f"'{title}' is still in the recipient's Inbox after cancel & delete"
    )

    return {"title": title, "recipient": recipient}
