import os
import re
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from pages.page_dialog import Dialog
from pages.page_menu import Menu
from flows.flow_mail_check import confirm_mail_received


def sign_by_title(page, title: str, signer_email: str = None) -> None:
    expect(Menu(page).all_tab).to_be_visible()
    Menu(page).all_tab.click()

    wait_timeout = float(os.getenv("SIGN_TITLE_WAIT_TIMEOUT", "60"))
    wait_interval = float(os.getenv("SIGN_TITLE_WAIT_INTERVAL", "5"))
    row = None
    deadline = time.time() + wait_timeout
    while time.time() < deadline:
        row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
        if row.count() > 0:
            break
        page.reload()
        Menu(page).all_tab.click()
        time.sleep(wait_interval)

    if row is None or row.count() == 0:
        raise ValueError(f"Sign button not found for title: {title}")

    sign_button = row.get_by_role("button", name="Sign").first
    sign_button.scroll_into_view_if_needed()

    sign_page = page
    try:
        with page.expect_popup(timeout=3000) as popup_info:
            sign_button.click()
        sign_page = popup_info.value
        sign_page.wait_for_load_state("domcontentloaded")
    except PlaywrightTimeoutError:
        # No popup opened; continue on the same page.
        sign_page = page

    unsigned_locator = sign_page.locator("div.resize-drag").filter(
        has=sign_page.locator("div.name", has_text="Click to sign")
    )
    had_unsigned = False
    while unsigned_locator.count() > 0:
        had_unsigned = True
        print(f"[DEBUG] found unsigned fields: {unsigned_locator.count()}")
        target = unsigned_locator.first
        target.scroll_into_view_if_needed()

        signature_modal = sign_page.get_by_label("Create Your Signature")
        sign_button = signature_modal.get_by_role("button", name="Sign").first
        for attempt in range(2):
            target.click()
            try:
                expect(signature_modal).to_be_visible(timeout=3000)
                break
            except AssertionError:
                if attempt == 1:
                    raise

        expect(sign_button).to_be_visible()
        sign_button.click()

        if sign_page.get_by_text("Please draw your signature").first.is_visible():
            print("[DEBUG] need draw signature")
            print("[DEBUG] drawing on signature canvas")
            canvas = signature_modal.locator("canvas").first
            box = canvas.bounding_box()
            start_x = box["x"] + 10
            start_y = box["y"] + 10
            sign_page.mouse.move(start_x, start_y)
            sign_page.mouse.down()
            # Draw a simple name-like stroke pattern.
            name = "Alex"
            x = start_x
            y = start_y
            for idx, ch in enumerate(name):
                x += 25
                y += -8 if idx % 2 == 0 else 10
                sign_page.mouse.move(x, y)
            sign_page.mouse.up()
            sign_button = signature_modal.get_by_role("button", name="Sign").first
            expect(sign_button).to_be_visible()
            sign_button.click(force=True)

        sign_page.get_by_label("Create Your Signature").wait_for(state="hidden")

    print(f"[DEBUG] had_unsigned: {had_unsigned}")
    if had_unsigned:
        confirm_button = sign_page.get_by_role("button", name="Confirm")
        confirm_button.click()
        dialog = Dialog(sign_page)
        dialog.yes_button.click()
        expect(sign_page.get_by_text("SUBMISSION SUCCESS")).to_be_visible()
        dialog.ok_button.click()
    # Verify status is Completed for current signer in All tab (with retry).
    status_timeout = float(os.getenv("SIGN_STATUS_WAIT_TIMEOUT", "60"))
    status_interval = float(os.getenv("SIGN_STATUS_WAIT_INTERVAL", "5"))
    deadline = time.time() + status_timeout
    while True:
        expect(Menu(page).all_tab).to_be_visible()
        Menu(page).all_tab.click()
        status_row = page.locator("tr", has=page.get_by_text(title, exact=True)).first
        expect(status_row).to_be_visible()
        if status_row.get_by_text("Completed").first.is_visible():
            break
        row_text = status_row.inner_text()
        match = re.search(r"Waiting\s+for\s+(\d+)\s+others?", row_text, re.IGNORECASE)
        if match:
            print(f"[DEBUG] waiting for {match.group(1)} others")
            sender_email = os.getenv("LOGIN_DEFAULT_EMAIL", "")
            if sender_email and signer_email != sender_email:
                confirm_mail_received("A signer has completed the document", recipient=sender_email)
            return
        if time.time() >= deadline:
            raise ValueError(f"Status not Completed for title: {title}")
        page.reload()
        time.sleep(status_interval)

    # Completed: no mail required here.
