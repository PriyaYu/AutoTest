import os
import time

from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from pages.page_initiate_signing_request import InitiateSigningRequestPage

def test_add_draft(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        _, title = initiate_signing_request(
            page=page,
            pdf_path=sample_pdf_path,
            mode="draft"
        )
        flow = InitiateSigningRequestPage(page)
        flow.menu.drafts_tab.click()
        search_box = page.get_by_role("textbox", name="Search Draft")
        expect(search_box).to_be_visible()
        search_box.click()
        search_box.fill(title)
        search_box.press("Enter")

        wait_timeout = float(os.getenv("SEARCH_WAIT_TIMEOUT", "30"))
        wait_interval = float(os.getenv("SEARCH_WAIT_INTERVAL", "2"))
        deadline = time.time() + wait_timeout
        while True:
            if page.get_by_text(title).count() > 0:
                expect(page.get_by_text(title)).to_be_visible()
                break
            if time.time() >= deadline:
                raise ValueError(f"Draft not found for title: {title}")
            page.reload()
            flow.menu.drafts_tab.click()
            search_box = page.get_by_role("textbox", name="Search Draft")
            expect(search_box).to_be_visible()
            search_box.fill(title)
            search_box.press("Enter")
            time.sleep(wait_interval)
