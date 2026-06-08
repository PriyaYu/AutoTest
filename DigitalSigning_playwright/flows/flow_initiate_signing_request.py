import os
from datetime import datetime

from playwright.sync_api import expect

from pages.page_initiate_signing_request import InitiateSigningRequestPage


def initiate_signing_request(
    page,
    pdf_path,
    recipient_emails=None,
    IsSequence=False,
    mode=None,
    save_to_fc=None,
):
    flow = InitiateSigningRequestPage(page)
    if recipient_emails is None:
        raw_emails = os.getenv("SIGN_EMAIL", "")
        recipient_emails = [email.strip() for email in raw_emails.split(",") if email.strip()]
    if not recipient_emails:
        raise ValueError("SIGN_EMAIL is required and must contain at least one email")
    date_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
    if mode == "draft":
        title = f"Draft_{date_prefix}"
        flow.start_button.click()
    elif mode == "template":
        title = f"Template_{date_prefix}"
        flow.menu.templates_tab.click()
        flow.add_template_button.click()
    else:
        title_prefix = "SequenceSigning" if IsSequence else "ParallelSigning"
        title = f"{title_prefix}_{date_prefix}"
        flow.start_button.click()


    # A) 直接設定 input（較穩、較快）。pdf_path 可為單一路徑或多個路徑（多文件請求）。
    # 每次 set_input_files 會「新增」一份文件，所以逐一上傳並等待份數到位。
    # Upload is async (~several seconds); waiting before continuing avoids the
    # "Please upload at least one document" error on save/send.
    paths = list(pdf_path) if isinstance(pdf_path, (list, tuple)) else [pdf_path]
    for idx, single_path in enumerate(paths, start=1):
        flow.file_input.set_input_files(str(single_path))
        expect(page.locator(".one-doc")).to_have_count(idx, timeout=60000)
    # B) 人類操作路徑（點 Upload 開視窗，再選檔）
    # with page.expect_file_chooser() as fc:
    #     flow.upload_button.click()
    # fc.value.set_files(str(pdf_path))


    if IsSequence:
        flow.set_sequence_checkbox.check()

    for _ in range(len(recipient_emails) - 1):
        flow.new_recipient_button.click()

    for idx, email in enumerate(recipient_emails, start=1):
        flow.name_inputs.nth(idx - 1).fill(f"{email}_Recipient")
        flow.email_inputs.nth(idx - 1).fill(email)
        flow.role_inputs.nth(idx - 1).fill(f"Recipient_JT_{date_prefix}_-{idx}")

    # Optionally tick each recipient's "Save to Frequent Contact" checkbox.
    if save_to_fc:
        for idx, want in enumerate(save_to_fc):
            if want:
                checkbox = flow.save_to_fc_checkboxes.nth(idx)
                checkbox.check(force=True)
                expect(checkbox).to_be_checked()

    flow.subject_input.fill(title)

    if mode == "template":
        flow.save_as_template_button.click()
        return page, title    
    
    flow.next_button.click()

    for idx in range(len(recipient_emails)):
        flow.signature_field_buttons.nth(idx).click()

    if mode == "draft":
        page.locator(".ant-drawer-extra > .css-7rjeeh").click()
        page.get_by_text("Save to Draft").click()
        expect(page.locator("body")).to_contain_text("Save to draft success")
        return page, title

    
    flow.send_button.click()
    flow.confirm_yes_button.click()
    flow.ok_button.click()

    return page, title
