import os
from datetime import datetime

from playwright.sync_api import expect

from pages.page_menu import Menu


def add_recipient(page) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    base_alias = os.getenv("RECIPIENT_ALIAS_BASE", "")
    alias = f"{base_alias}+{timestamp}"
    name = alias
    email_domain = os.getenv("SIGNUP_EMAIL_DOMAIN", "gmail.com")
    email = f"{alias}@{email_domain}"
    job_title = f"JH_{alias}"
    search_term = name

    if "/#/frequent-contacts" not in page.url:
        Menu(page).frequent_contacts_tab.click()
    page.get_by_role("button", name="Add Recipient").click()
    page.get_by_role("textbox", name="* Name").fill(name)
    page.get_by_role("textbox", name="* Email").fill(email)
    page.get_by_role("textbox", name="Job Title").fill(job_title)
    page.get_by_role("button", name="Save").click()

    # The contact list can lag right after saving, so retry the search a few
    # times instead of relying on a single long wait.
    search_input = page.get_by_role("textbox", name="Search All Contacts")
    result = page.get_by_text(name, exact=True)
    for attempt in range(3):
        search_input.fill(search_term)
        search_input.press("Enter")
        try:
            expect(result).to_be_visible(timeout=10000)
            break
        except AssertionError:
            if attempt == 2:
                raise
            search_input.fill("")
            search_input.press("Enter")

    return {"name": name, "email": email, "job_title": job_title}
