from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from pages.page_initiate_signing_request import InitiateSigningRequestPage

def test_add_draft(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(5):
        _, title = initiate_signing_request(
            page=page,
            pdf_path=sample_pdf_path,
            mode="draft"
        )
        flow = InitiateSigningRequestPage(page)
        flow.search_all_contacts_input.click()
        flow.search_all_contacts_input.fill(title)
        flow.search_all_contacts_input.press("Enter")
        expect(page.get_by_text(title)).to_be_visible()
