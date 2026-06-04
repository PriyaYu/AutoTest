from playwright.sync_api import expect

from flows.flow_edit_template import edit_template, _open_template_row
from pages.page_initiate_signing_request import InitiateSigningRequestPage


def delete_template(page, pdf_path) -> dict:
    flow = InitiateSigningRequestPage(page)

    # Chain the lifecycle: create + edit a template, then delete it.
    info = edit_template(page, pdf_path)
    title = info["new"]

    # Open the template's action menu and choose Discard.
    flow.menu.templates_tab.click()
    row = _open_template_row(page, title)
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Discard").first.click()

    # Confirm deletion in the dialog.
    page.get_by_role("button", name="Delete", exact=True).click()

    # Verify the template no longer exists.
    search = page.get_by_role("textbox", name="Search All Contacts")
    search.fill(title)
    search.press("Enter")
    expect(page.get_by_text(title, exact=True)).to_have_count(0, timeout=15000)

    return info
