from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from pages.page_initiate_signing_request import InitiateSigningRequestPage
from pages.page_menu import Menu


def _ensure_on_templates(page):
    """Navigate to the Templates page, getting past the dashboard's upload
    drop-zone overlay which can intercept the first menu click after login."""
    menu = Menu(page)
    for _ in range(3):
        try:
            menu.templates_tab.click(timeout=8000)
            return
        except Exception:
            page.wait_for_timeout(1500)
    menu.templates_tab.click(force=True)


def _open_template_row(page, title):
    search = page.get_by_role("textbox", name="Search All Contacts")
    search.fill(title)
    search.press("Enter")
    row = page.locator("tr.vxe-body--row", has=page.get_by_text(title, exact=True))
    expect(row).to_be_visible(timeout=15000)
    return row


def edit_template(page, pdf_path) -> dict:
    flow = InitiateSigningRequestPage(page)

    # Move off the dashboard first so its upload overlay can't block the menu
    # click that initiate_signing_request performs.
    _ensure_on_templates(page)

    # Seed a fresh template so the edit flow has a deterministic target.
    _, original_title = initiate_signing_request(page=page, pdf_path=pdf_path, mode="template")
    new_title = f"{original_title}_Edited"

    # Open the template's action menu and choose Edit.
    flow.menu.templates_tab.click()
    row = _open_template_row(page, original_title)
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Edit").first.click()

    # Rename the template (subject) and save. Saving updates the existing
    # template in place rather than creating a duplicate.
    subject = page.locator("#form_item_subject")
    expect(subject).to_be_visible(timeout=15000)
    subject.fill(new_title)
    flow.save_as_template_button.click()

    # Verify the rename persisted: new title present, old title gone.
    flow.menu.templates_tab.click()
    search = page.get_by_role("textbox", name="Search All Contacts")
    search.fill(new_title)
    search.press("Enter")
    expect(page.get_by_text(new_title, exact=True).first).to_be_visible(timeout=15000)

    search.fill(original_title)
    search.press("Enter")
    expect(page.get_by_text(original_title, exact=True)).to_have_count(0, timeout=15000)

    return {"original": original_title, "new": new_title}
