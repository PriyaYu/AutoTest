from playwright.sync_api import expect

from pages.page_initiate_signing_request import InitiateSigningRequestPage


def verify_create_request_validation(page) -> None:
    """Drive the create-request form with invalid input and assert it is
    rejected. Fast and side-effect-free: nothing is uploaded or sent."""
    flow = InitiateSigningRequestPage(page)
    page.wait_for_timeout(1500)

    # Start a new request (resilient against the dashboard upload overlay).
    try:
        flow.start_button.click(timeout=8000)
    except Exception:
        flow.start_button.click(force=True)
    expect(flow.next_button).to_be_visible(timeout=15000)

    # 1) Name and Email are required.
    flow.next_button.click()
    expect(page.get_by_text("Please input your name")).to_be_visible(timeout=10000)
    expect(page.get_by_text("Please input your email")).to_be_visible()

    # 2) Email must be a valid address.
    flow.name_inputs.first.fill("Tester")
    flow.email_inputs.first.fill("not-an-email")
    flow.subject_input.fill("ValidationSubject")
    flow.next_button.click()
    expect(page.get_by_text("Email is invalid")).to_be_visible(timeout=10000)

    # 3) At least one document must be uploaded (valid fields, no upload).
    flow.email_inputs.first.fill("tester@example.com")
    flow.next_button.click()
    expect(page.get_by_text("Please upload at least one document")).to_be_visible(timeout=10000)
