
from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_login import login
from pages.page_initiate_signing_request import InitiateSigningRequestPage


def test_add_template(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        _, title = initiate_signing_request(
            page=page,
            pdf_path=sample_pdf_path,
            mode="template",
        )
        flow = InitiateSigningRequestPage(page)
        flow.menu.templates_tab.click()
        flow.search_all_contacts_input.click()
        flow.search_all_contacts_input.fill(title)
        flow.search_all_contacts_input.press("Enter")
        expect(page.get_by_text(title)).to_be_visible()
