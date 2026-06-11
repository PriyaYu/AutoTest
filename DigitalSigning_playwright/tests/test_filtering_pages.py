import re
from datetime import datetime, timedelta

from playwright.sync_api import expect

from flows.flow_login import login

# Relative date filter options and their window length.
_DATE_PERIODS = [
    ("Last 24 hours", timedelta(hours=24)),
    ("Last week", timedelta(days=7)),
    ("Last 30 days", timedelta(days=30)),
    ("Last 6 months", timedelta(days=186)),
    ("Last 12 months", timedelta(days=366)),
]


def _open_tab(page, tab_name: str):
    item = page.get_by_role("menuitem", name=tab_name)
    item.click()
    # Confirm navigation by the tab becoming selected (more robust than matching
    # a heading text, which differs across pages/environments).
    expect(item).to_have_class(re.compile(r"ant-menu-item-selected"), timeout=15000)
    page.wait_for_timeout(1500)


def _rows(page):
    return page.locator("tr.vxe-body--row")


def _total(page):
    """Read the '<start>-<end> of <total>' pagination total."""
    el = page.locator("li.ant-pagination-total-text")
    if el.count() == 0:
        return None
    match = re.search(r"of\s+(\d+)", el.first.inner_text())
    return int(match.group(1)) if match else None


def _search(page, label: str, term: str = "2026"):
    search = page.get_by_role("textbox", name=label)
    expect(search).to_be_visible()
    search.click()
    search.fill(term)
    search.press("Enter")
    page.wait_for_timeout(2000)
    # Content check: every visible row actually contains the search term.
    rows = _rows(page)
    for i in range(rows.count()):
        text = rows.nth(i).inner_text()
        assert term in text, f"search '{term}' but a row does not contain it: {text[:60]!r}"


def _open_filter(page, label: str):
    page.locator("div").filter(has_text=label).nth(4).click()


def _apply_filter(page):
    page.get_by_role("button", name="Apply").click()


def _reset_filter(page):
    page.get_by_role("button", name="Reset").click()


def _select_option(page, option: str):
    page.get_by_text(option, exact=True).last.click()


def _row_title_dates(page):
    """Parse YYYYMMDD_HHMMSS (our request naming convention) from each visible
    row's title. Rows without it (older/manually-named items) are skipped."""
    dates = []
    rows = _rows(page)
    for i in range(rows.count()):
        match = re.search(r"(\d{8})_(\d{6})", rows.nth(i).inner_text())
        if match:
            dates.append(datetime.strptime(match.group(1) + match.group(2), "%Y%m%d%H%M%S"))
    return dates


def _filter_date(page):
    """Apply each relative date range and verify (a) the visible rows were
    created within the range (parsed from the title date), and (b) the totals
    grow monotonically as the range widens."""
    now = datetime.now()
    buffer = timedelta(days=2)  # tolerate timezone / sent-vs-created / boundary
    totals = []
    for option, period in _DATE_PERIODS:
        _open_filter(page, "Date")
        _select_option(page, option)
        _apply_filter(page)
        page.wait_for_timeout(2000)
        totals.append(_total(page))
        cutoff = now - period - buffer
        for dt in _row_title_dates(page):
            assert dt >= cutoff, f"Date filter '{option}': a row created {dt} is older than the range"

    # Exercise the Custom range too (date picker; no content assertion).
    _open_filter(page, "Date")
    _select_option(page, "Custom")
    _apply_filter(page)

    nums = [t for t in totals if t is not None]
    assert nums == sorted(nums), f"date filter totals are not monotonic by range: {totals}"

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
    """Apply each status filter and verify the visible rows actually match it,
    plus that the three categories partition the full ("All") list."""
    status_header = page.locator("th.vxe-header--column", has_text="Status")
    status_colid = status_header.first.get_attribute("colid") if status_header.count() else None

    totals = {}
    for option in ["In Progress", "Completed", "Incomplete"]:
        _open_filter(page, "Status")
        _select_option(page, option)
        _apply_filter(page)
        page.wait_for_timeout(2000)
        totals[option] = _total(page)

        if status_colid:
            rows = _rows(page)
            for i in range(rows.count()):
                status = rows.nth(i).locator(f"td.{status_colid}").first.inner_text().strip()
                if option == "Completed":
                    assert status == "Completed", f"Completed filter but row shows '{status}'"
                else:
                    assert status != "Completed", f"{option} filter but a row still shows 'Completed'"

    # "All" shows everything — the three categories should sum to it.
    _open_filter(page, "Status")
    _select_option(page, "All")
    _apply_filter(page)
    page.wait_for_timeout(2000)
    all_total = _total(page)
    if all_total is not None and all(v is not None for v in totals.values()):
        assert sum(totals.values()) == all_total, (
            f"status filters do not partition the list: {totals} sum != all={all_total}"
        )

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
