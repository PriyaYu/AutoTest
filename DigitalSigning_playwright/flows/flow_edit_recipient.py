import os
from datetime import datetime

from playwright.sync_api import expect

from flows.flow_add_recipient import add_recipient


def edit_recipient(page) -> dict:
    # Seed a fresh recipient so the edit flow has a deterministic target to act on.
    contact = add_recipient(page)
    original_name = contact["name"]

    # New values to apply during the edit.
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_name = f"Edited_{timestamp}"
    email_domain = os.getenv("SIGNUP_EMAIL_DOMAIN", "nexify.com.hk")
    new_email = f"{new_name}@{email_domain}"
    new_job_title = f"JH_Edited_{timestamp}"

    # Find the freshly created contact's row and open it for editing.
    search_input = page.get_by_role("textbox", name="Search All Contacts")
    search_input.fill(original_name)
    search_input.press("Enter")

    row = page.locator("tr.vxe-body--row", has=page.get_by_text(original_name, exact=True))
    expect(row).to_be_visible(timeout=15000)
    row.get_by_role("button", name="Edit").click()

    # Update Name, Email and Job Title, then save the change.
    name_input = page.locator("#form_item_name")
    expect(name_input).to_be_visible(timeout=15000)
    name_input.fill(new_name)
    page.locator("#form_item_email").fill(new_email)
    page.locator("#form_item_job").fill(new_job_title)
    page.get_by_role("button", name="Save").click()

    # Re-search by the new name and verify all edited values persisted on the row.
    search_input = page.get_by_role("textbox", name="Search All Contacts")
    search_input.fill(new_name)
    search_input.press("Enter")

    row = page.locator("tr.vxe-body--row", has=page.get_by_text(new_name, exact=True))
    expect(row).to_be_visible(timeout=15000)
    expect(row.get_by_text(new_email, exact=True)).to_be_visible(timeout=15000)
    expect(row.get_by_text(new_job_title, exact=True)).to_be_visible(timeout=15000)

    # Reverse check: the old name should no longer match any contact.
    search_input = page.get_by_role("textbox", name="Search All Contacts")
    search_input.fill(original_name)
    search_input.press("Enter")
    expect(page.get_by_text(original_name, exact=True)).to_have_count(0, timeout=15000)

    contact.update({"name": new_name, "email": new_email, "job_title": new_job_title})
    return contact
