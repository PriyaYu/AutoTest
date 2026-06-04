from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from pages.page_initiate_signing_request import InitiateSigningRequestPage


def _open_draft_row(page, title, attempts: int = 3):
    """Find the draft's row. The draft list loads asynchronously, so we wait
    patiently for the filtered result instead of reloading on every miss
    (reloading mid-load just restarts the load). Reload only as a bounded
    last resort in case the draft is still propagating to the list."""
    search = page.get_by_role("textbox", name="Search Draft")
    expect(search).to_be_visible(timeout=15000)
    page.wait_for_timeout(2000)  # let the draft list settle before the first search
    row = page.locator("tr.vxe-body--row", has=page.get_by_text(title, exact=True))
    for attempt in range(attempts):
        search.fill(title)
        search.press("Enter")
        # Poll for the result to load — no reload.
        for _ in range(20):
            page.wait_for_timeout(1000)
            if row.count() > 0:
                expect(row.first).to_be_visible(timeout=10000)
                return row.first
        if attempt < attempts - 1:
            page.reload()
            InitiateSigningRequestPage(page).menu.drafts_tab.click()
            page.wait_for_timeout(3000)
    raise AssertionError(f"Draft not found for title: {title}")


def delete_draft(page, pdf_path) -> dict:
    flow = InitiateSigningRequestPage(page)

    # Seed a fresh draft to delete.
    _, title = initiate_signing_request(page=page, pdf_path=pdf_path, mode="draft")

    # Open the draft's action menu and choose Discard.
    flow.menu.drafts_tab.click()
    row = _open_draft_row(page, title)
    row.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown-menu-item", has_text="Discard").first.click()

    # Confirm deletion in the dialog.
    page.get_by_role("button", name="Delete", exact=True).click()

    # Verify the draft no longer exists.
    search = page.get_by_role("textbox", name="Search Draft")
    search.fill(title)
    search.press("Enter")
    page.wait_for_timeout(2000)
    expect(page.get_by_text(title, exact=True)).to_have_count(0, timeout=15000)

    return {"title": title}
