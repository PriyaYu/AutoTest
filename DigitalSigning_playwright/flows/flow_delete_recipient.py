from playwright.sync_api import expect

from flows.flow_edit_recipient import edit_recipient


def delete_recipient(page) -> dict:
    # Chain the full lifecycle: create + edit a recipient, then delete that record.
    contact = edit_recipient(page)
    name = contact["name"]

    # Find the contact's row and open its action menu.
    search_input = page.get_by_role("textbox", name="Search All Contacts")
    search_input.fill(name)
    search_input.press("Enter")

    row = page.locator("tr.vxe-body--row", has=page.get_by_text(name, exact=True))
    expect(row).to_be_visible(timeout=15000)
    row.locator("button.ant-dropdown-trigger").click()

    # Choose Discard, then confirm deletion in the dialog.
    page.get_by_text("Discard", exact=True).click()
    page.get_by_role("button", name="Delete", exact=True).click()

    # Verify the contact no longer exists.
    search_input = page.get_by_role("textbox", name="Search All Contacts")
    search_input.fill(name)
    search_input.press("Enter")
    expect(page.get_by_text(name, exact=True)).to_have_count(0, timeout=15000)

    return contact
