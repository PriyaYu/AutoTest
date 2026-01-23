from datetime import datetime

from playwright.sync_api import expect

from pages.page_menu import Menu


def add_recipient(page) -> None:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    alias = f"zihsyuan0603+{timestamp}"
    name = alias
    email = f"{alias}@gmail.com"
    job_title = f"JH_{alias}"
    search_term = name

    if "/ds#/frequent-contacts" not in page.url:
        Menu(page).frequent_contacts_tab.click()
    page.get_by_role("button", name="Add Recipient").click()
    page.get_by_role("textbox", name="* Name").fill(name)
    page.get_by_role("textbox", name="* Email").fill(email)
    page.get_by_role("textbox", name="Job Title").fill(job_title)
    page.get_by_role("button", name="Save").click()

    search_input = page.get_by_role("textbox", name="Search All Contacts")
    search_input.fill(search_term)
    search_input.press("Enter")

    expect(page.get_by_text(name, exact=True)).to_be_visible()
