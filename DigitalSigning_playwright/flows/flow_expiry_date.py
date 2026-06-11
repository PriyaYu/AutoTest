import os
import re
from datetime import datetime, timedelta

from playwright.sync_api import expect

from flows.flow_cancel_delete_request import _open_sent_row, _resilient_tab
from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_view_request import _open_request_view
from pages.page_menu import Menu

EXPIRY_DAYS = 14


def verify_expiry_date(page, pdf_path) -> dict:
    """Create a request with a known Expiry Date ("N days") and verify it on
    both the Sent list ("Expires on" absolute date = created + N) and the View
    detail ("Expiry date: X days" remaining ~ N)."""
    recipients = [e.strip() for e in os.getenv("SIGN_EMAIL", "").split(",") if e.strip()]
    assert recipients, "SIGN_EMAIL must contain at least one recipient"

    _, title = initiate_signing_request(
        page=page, pdf_path=pdf_path, recipient_emails=recipients, expiry_days=EXPIRY_DAYS
    )

    # Expected expiry = creation date (from the title) + N days.
    created_match = re.search(r"(\d{8})_(\d{6})", title)
    created = datetime.strptime(created_match.group(1) + created_match.group(2), "%Y%m%d%H%M%S")
    expected_date = (created + timedelta(days=EXPIRY_DAYS)).date()

    # 1) Sent list: the "Expires on" column (col_4) absolute date.
    _resilient_tab(page, Menu(page).sent_tab)
    row = _open_sent_row(page, title)
    rowid = row.get_attribute("rowid")
    expires_text = page.locator(f"tr.vxe-body--row[rowid='{rowid}'] td.col_4").first.inner_text()
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", expires_text)
    assert m, f"could not parse 'Expires on' date from {expires_text!r}"
    shown_date = datetime(int(m.group(3)), int(m.group(1)), int(m.group(2))).date()
    assert shown_date == expected_date, (
        f"Sent 'Expires on' {shown_date} != expected {expected_date} (set {EXPIRY_DAYS} days)"
    )

    # 2) View detail: "Expiry date: X days" remaining (allow N-1 for time elapsed).
    _open_request_view(page, title)
    drawer = page.locator(".document-sign-drawer.is-view")
    item = drawer.locator(".request-info-item").filter(has_text="Expiry date")
    expect(item).to_be_visible(timeout=15000)
    dm = re.search(r"(\d+)\s*days?", item.inner_text())
    assert dm, f"could not parse View expiry from {item.inner_text()!r}"
    days = int(dm.group(1))
    assert days in (EXPIRY_DAYS - 1, EXPIRY_DAYS), (
        f"View 'Expiry date: {days} days' not in {{{EXPIRY_DAYS - 1}, {EXPIRY_DAYS}}}"
    )

    # Close the View drawer.
    close = page.locator(".ant-drawer-close")
    if close.count() > 0 and close.first.is_visible():
        close.first.click()
    else:
        page.keyboard.press("Escape")
    page.wait_for_timeout(800)

    # 3) Cleanup: cancel & delete the request.
    _resilient_tab(page, Menu(page).sent_tab)
    row = _open_sent_row(page, title)
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Cancel & Delete").first.click()
    page.get_by_role("button", name="Delete", exact=True).click()

    return {"title": title, "expiry_days": EXPIRY_DAYS, "expires_on": str(shown_date)}
