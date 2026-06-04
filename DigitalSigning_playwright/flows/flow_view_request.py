import os

from playwright.sync_api import expect

from flows.flow_cancel_delete_request import _resilient_tab
from flows.flow_initiate_signing_request import initiate_signing_request
from pages.page_menu import Menu


def _open_request_view(page, title):
    """Open a sent request's detail drawer (View). A freshly sent request only
    exposes its View action after the Sent list is refreshed a few times, so
    re-search (and periodically reload) until the button appears, then click it.
    vxe-table also splits a logical row across sibling <tr>s sharing a rowid, so
    the View button can sit in a different <tr> than the title."""
    _resilient_tab(page, Menu(page).sent_tab)
    search = page.get_by_role("textbox", name="Search Sent")
    expect(search).to_be_visible(timeout=15000)
    base = page.locator("tr.vxe-body--row", has=page.get_by_text(title, exact=True))

    for attempt in range(15):
        search.fill(title)
        search.press("Enter")
        page.wait_for_timeout(2500)
        if base.count() > 0:
            rowid = base.first.get_attribute("rowid")
            views = page.locator(
                f"tr.vxe-body--row[rowid='{rowid}']"
            ).get_by_role("button", name="View")
            for i in range(views.count()):
                if views.nth(i).is_visible():
                    views.nth(i).click()
                    return
        # Stronger refresh every few attempts.
        if attempt % 3 == 2:
            page.reload()
            _resilient_tab(page, Menu(page).sent_tab)
            page.wait_for_timeout(2000)
    raise AssertionError(f"View action never became available for request: {title}")


def verify_request_detail(page, title, recipient_emails) -> dict:
    """Open a sent request's detail drawer (View) and assert it shows the
    correct title, recipients, document and expiry. Reusable: can also be
    called from a signing test after the request has been sent."""
    _open_request_view(page, title)

    drawer = page.locator(".document-sign-drawer.is-view")
    expect(drawer).to_be_visible(timeout=15000)

    # Request Info: title and expiry.
    expect(drawer.locator(".request-info-item").filter(has_text="Title")).to_contain_text(title)
    expect(drawer.locator(".request-info-item").filter(has_text="Expiry date")).to_be_visible()

    # The uploaded document is listed.
    expect(drawer.locator(".document-name").first).to_be_visible()

    # Every recipient is shown in the signer list.
    for email in recipient_emails:
        expect(drawer.get_by_text(email, exact=False).first).to_be_visible(timeout=10000)

    return {"title": title, "recipients": recipient_emails}


def view_request(page, pdf_path) -> dict:
    recipient_emails = [e.strip() for e in os.getenv("SIGN_EMAIL", "").split(",") if e.strip()]
    assert recipient_emails, "SIGN_EMAIL must contain at least one recipient"

    # Send a request with known content, then verify its detail view.
    _, title = initiate_signing_request(
        page=page, pdf_path=pdf_path, recipient_emails=recipient_emails
    )
    return verify_request_detail(page, title, recipient_emails)
