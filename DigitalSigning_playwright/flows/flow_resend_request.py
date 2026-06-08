from playwright.sync_api import expect

from flows.flow_cancel_delete_request import _resilient_tab
from pages.page_menu import Menu


def resend_request(page) -> dict:
    """Resend an existing pending request from Sent and verify the success
    toast. Uses whatever pending request is already there (a pending request
    exposes a 'Resent' button)."""
    _resilient_tab(page, Menu(page).sent_tab)

    # The Sent list loads asynchronously; poll for a visible Resent button.
    target = None
    for _ in range(25):
        page.wait_for_timeout(1000)
        resent = page.get_by_role("button", name="Resent")
        for i in range(resent.count()):
            if resent.nth(i).is_visible():
                target = resent.nth(i)
                break
        if target:
            break
    assert target, "No pending request with a Resent button found in Sent"

    target.click()
    expect(page.get_by_text("Resent success")).to_be_visible(timeout=10000)

    return {"toast": "Resent success"}
