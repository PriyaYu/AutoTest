import time
from datetime import datetime

from playwright.sync_api import expect

from flows.flow_cancel_delete_request import _open_sent_row, _resilient_tab
from flows.flow_initiate_signing_request import initiate_signing_request
from pages.page_menu import Menu


def _fc_search(page, term):
    box = page.get_by_role("textbox", name="Search All Contacts")
    expect(box).to_be_visible(timeout=15000)
    box.fill(term)
    box.press("Enter")
    page.wait_for_timeout(2500)


def _fc_presence(page, email, want_present, timeout=30.0) -> bool:
    """Poll Frequent Contacts until `email` presence matches want_present."""
    _resilient_tab(page, Menu(page).frequent_contacts_tab)
    deadline = time.time() + timeout
    while time.time() < deadline:
        _fc_search(page, email)
        present = page.get_by_text(email, exact=True).count() > 0
        if present == want_present:
            return True
    return False


def _delete_fc(page, email):
    _resilient_tab(page, Menu(page).frequent_contacts_tab)
    _fc_search(page, email)
    row = page.locator("tr.vxe-body--row", has=page.get_by_text(email, exact=True)).first
    expect(row).to_be_visible(timeout=15000)
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Discard").first.click()
    page.get_by_role("button", name="Delete", exact=True).click()
    _fc_search(page, email)
    expect(page.get_by_text(email, exact=True)).to_have_count(0, timeout=15000)


def _cancel_request(page, title):
    _resilient_tab(page, Menu(page).sent_tab)
    try:
        row = _open_sent_row(page, title)
    except Exception:
        return  # best-effort cleanup
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Cancel & Delete").first.click()
    page.get_by_role("button", name="Delete", exact=True).click()


def save_to_frequent_contact(page, pdf_path) -> dict:
    """One request with two recipients: the first ticks 'Save to Frequent
    Contact', the second does not. Verify only the ticked one is saved."""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    saved = f"qa_fc_saved_{ts}@example.com"
    not_saved = f"qa_fc_unsaved_{ts}@example.com"

    _, title = initiate_signing_request(
        page=page,
        pdf_path=pdf_path,
        recipient_emails=[saved, not_saved],
        save_to_fc=[True, False],
    )

    assert _fc_presence(page, saved, want_present=True), (
        f"{saved} was not saved to Frequent Contacts"
    )
    assert _fc_presence(page, not_saved, want_present=False), (
        f"{not_saved} should NOT be in Frequent Contacts"
    )

    # Cleanup: remove the saved contact and the sent request.
    _delete_fc(page, saved)
    _cancel_request(page, title)

    return {"saved": saved, "not_saved": not_saved, "title": title}
