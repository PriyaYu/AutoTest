from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from pages.page_menu import Menu


def check_signing_completed(page, title: str) -> None:
    if not title:
        raise ValueError("title is required but not set")

    expect(Menu(page).all_tab).to_be_visible()
    Menu(page).all_tab.click()

    search_box = page.get_by_role("textbox", name="Search All")
    search_box.fill(title)
    search_box.press("Enter")

    expect(page.locator("tbody")).to_contain_text("Completed")
    row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
    expect(row).to_be_visible()
    row.get_by_role("button", name="View").click()
    expect(page.locator("body")).to_contain_text("Complete")
    page.get_by_role("button", name="Close").click()
    expect(row.get_by_role("button", name="Download")).to_be_visible()
