import re
import time

from playwright.sync_api import expect

from pages.page_menu import Menu

# Dashboard stat card title -> the Menu tab whose list total it should match.
STAT_TO_TAB = {
    "Inbox": "inbox_tab",
    "Waiting for Others": "waiting_for_others_tab",
    "Expiring Soon": "expiring_soon_tab",
    "Completed": "completed_tab",
}


def _read_dashboard_stats(page) -> dict:
    """Read the four dashboard stat cards once their values have stabilised."""
    expect(page.locator(".dashboard-container")).to_be_visible(timeout=20000)
    items = page.locator(".classify-count-item")
    expect(items).to_have_count(4, timeout=20000)

    # Values are filled by an async call and may start at 0, so wait until two
    # consecutive reads agree and every value is populated.
    prev = None
    cur = {}
    for _ in range(15):
        page.wait_for_timeout(1000)
        cur = {}
        for i in range(items.count()):
            title = items.nth(i).locator(".classify-count-item-title").inner_text().strip()
            value = items.nth(i).locator(".classify-count-item-value").inner_text().strip()
            cur[title] = value
        if cur == prev and all(v != "" for v in cur.values()):
            break
        prev = cur

    return {title: int(value) for title, value in cur.items()}


def _list_total(page, expected: int, timeout: float = 25.0) -> int:
    """Read the '<start>-<end> of <total>' pagination text, polling until it
    matches the expected value (handles the list's async load) or times out."""
    total_text = page.locator("li.ant-pagination-total-text")
    expect(total_text).to_be_visible(timeout=20000)
    last = None
    deadline = time.time() + timeout
    while time.time() < deadline:
        match = re.search(r"of\s+(\d+)", total_text.inner_text())
        if match:
            last = int(match.group(1))
            if last == expected:
                return last
        page.wait_for_timeout(1000)
    return last


def verify_dashboard(page) -> dict:
    menu = Menu(page)

    # 1) Header: greeting + date are present.
    container = page.locator(".dashboard-container")
    expect(container.locator(".welcome")).to_be_visible(timeout=20000)
    expect(container.locator(".header")).to_contain_text(re.compile(r"\w"))

    # 2) "Get Started" entry point (upload/create flow) is present.
    expect(container.locator(".get-start")).to_be_visible()
    expect(page.get_by_text("Start", exact=True)).to_be_visible()

    # 3) Read the four stat cards.
    stats = _read_dashboard_stats(page)
    assert set(stats.keys()) == set(STAT_TO_TAB.keys()), (
        f"Unexpected dashboard cards: {sorted(stats.keys())}"
    )
    for title, value in stats.items():
        assert value >= 0, f"{title} count should be non-negative, got {value}"

    # 4) Each stat number must match its list page's total.
    for title, tab_attr in STAT_TO_TAB.items():
        expected = stats[title]
        getattr(menu, tab_attr).click()
        actual = _list_total(page, expected)
        assert actual == expected, (
            f"{title}: dashboard shows {expected} but list total is {actual}"
        )

    return stats
