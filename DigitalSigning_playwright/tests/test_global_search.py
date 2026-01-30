from playwright.sync_api import expect

from flows.flow_login import login


def test_global_search(page) -> None:
    login(page)
    search = page.get_by_role("textbox", name="Search")
    expect(search).to_be_visible()
    search.click()
    search.fill("2026")
    search.press("Enter")
    expect(page.get_by_text("Search")).to_be_visible()
