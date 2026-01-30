from playwright.sync_api import expect

from flows.flow_login import login


def _open_tab(page, tab_name: str):
    page.get_by_role("menuitem", name=tab_name).click()
    expect(page.get_by_role("main").get_by_text(tab_name, exact=True)).to_be_visible()


def _search(page, label: str):
    search = page.get_by_role("textbox", name=label)
    expect(search).to_be_visible()
    search.click()
    search.fill("2026")
    search.press("Enter")


def _open_filter(page, label: str):
    page.locator("div").filter(has_text=label).nth(4).click()


def _apply_filter(page):
    page.get_by_role("button", name="Apply").click()

def _reset_filter(page):
    page.get_by_role("button", name="Reset").click()

def _select_option(page, option: str):
    page.get_by_text(option, exact=True).last.click()

def _filter_date(page):  
    for option in ["Last 12 months", "Last 6 months", "Last 30 days", "Last week", "Last 24 hours", "Custom"]:
        _open_filter(page, "Date")
        _select_option(page, option)
        _apply_filter(page)
    _open_filter(page, "Date")
    _reset_filter(page)


def _filter_due_date(page):
    for option in ["All Period", "30 days remaining", "14 days remaining", "7 days remaining", "3 days remaining"]:
        _open_filter(page, "Due Date")
        _select_option(page, option)
        _apply_filter(page)
    _open_filter(page, "Due Date")
    _reset_filter(page)


def _filter_status(page):
    for option in ["All","In Progress", "Completed", "Incomplete"]:
        _open_filter(page, "Status")
        _select_option(page, option)
        _apply_filter(page)
    _open_filter(page, "Status")
    _reset_filter(page)


def _filter_sender(page):
    for option in ["Sent by anyone", "Sent by me", "Sent to me"]:
        _open_filter(page, "Sender")
        _select_option(page, option)
        _apply_filter(page)
    _open_filter(page, "Sender")
    _reset_filter(page)


def _clear_filters(page):
    page.get_by_role("button", name="Clear").click()


def test_page_filters(page) -> None:
    login(page)

    # All
    _open_tab(page, "All")
    _search(page, "Search All")
    _filter_date(page)
    _filter_due_date(page)
    _filter_status(page)
    _filter_sender(page)
    _clear_filters(page)

    # Sent
    _open_tab(page, "Sent")
    _search(page, "Search Sent")
    _filter_date(page)
    _filter_due_date(page)
    _filter_status(page)
    _clear_filters(page)

    # Inbox
    _open_tab(page, "Inbox")
    _search(page, "Search Inbox")
    _filter_date(page)
    _clear_filters(page)

    # Waiting for Others
    _open_tab(page, "Waiting for Others")
    _search(page, "Search Waiting")
    _filter_date(page)
    _clear_filters(page)

    # Expiring Soon
    _open_tab(page, "Expiring Soon")
    _search(page, "Search Expiring Soon")
    _filter_date(page)
    _clear_filters(page)

    # Completed
    _open_tab(page, "Completed")
    _search(page, "Search Completed")
    _filter_date(page)
    _clear_filters(page)

    # Review
    _open_tab(page, "Review")
    _search(page, "Search Review")
    _filter_date(page)
    _clear_filters(page)

    # Deleted
    _open_tab(page, "Deleted")
    _search(page, "Search Deleted")
    _filter_date(page)
    _clear_filters(page)
