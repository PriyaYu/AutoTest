import math

from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from flows.flow_login import login


def _draw_signature(page):
    for _ in range(3):
        canvas = page.locator("canvas").first
        expect(canvas).to_be_visible()
        try:
            box = canvas.bounding_box()
            if not box:
                raise PlaywrightTimeoutError("Canvas bounding box not available")
            centre_x = box["x"] + 220
            centre_y = box["y"] + 150
            page.mouse.move(centre_x, centre_y)
            page.mouse.down()
            # Draw a 5-petal flower using a rose curve.
            for i in range(0, 361, 6):
                angle = math.radians(i)
                radius = 45 * math.cos(5 * angle)
                x = centre_x + radius * math.cos(angle)
                y = centre_y + radius * math.sin(angle)
                page.mouse.move(x, y)
            page.mouse.up()
            return
        except PlaywrightTimeoutError:
            page.wait_for_timeout(500)
    box = canvas.bounding_box()
    centre_x = box["x"] + 220
    centre_y = box["y"] + 150
    page.mouse.move(centre_x, centre_y)
    page.mouse.down()
    for i in range(0, 361, 6):
        angle = math.radians(i)
        radius = 45 * math.cos(5 * angle)
        x = centre_x + radius * math.cos(angle)
        y = centre_y + radius * math.sin(angle)
        page.mouse.move(x, y)
    page.mouse.up()



def _save_signature(page):
    page.get_by_role("button", name="Save").click()
    expect(page.locator("body")).to_contain_text("Upload success")


def test_my_signature(page) -> None:
    login(page)

    print("[DEBUG] Navigate to My Signature")
    page.get_by_text("My Signature").click()
    expect(page.get_by_role("main").get_by_text("My Signature")).to_be_visible()

    replace_btn = page.get_by_text("Replace")
    has_signature = replace_btn.count() > 0 and replace_btn.first.is_visible()

    if has_signature:
        # Start clean so the flow is deterministic.
        print("[DEBUG] Existing signature found; remove first")
        remove_btn = page.get_by_text("Remove")
        expect(remove_btn).to_be_visible()
        remove_btn.click()
        page.get_by_role("button", name="Delete").click()

    print("[DEBUG] Create signature (draw and save)")
    _draw_signature(page)
    _save_signature(page)

    # Replace signature
    print("[DEBUG] Replace signature")
    replace_btn = page.get_by_text("Replace")
    expect(replace_btn).to_be_visible()
    replace_btn.click()
    _draw_signature(page)
    _save_signature(page)

    # Remove and upload new signature
    print("[DEBUG] Remove signature and upload new file")
    remove_btn = page.get_by_text("Remove")
    expect(remove_btn).to_be_visible()
    remove_btn.click()
    page.get_by_role("button", name="Delete").click()

    page.get_by_role("tab", name="UPLOAD").click()
    print("[DEBUG] Upload signature file")
    upload_btn = page.get_by_role("button", name="Upload Signature", exact=True)
    upload_btn.click()
    file_input = page.locator("input[type=\"file\"]").first
    file_input.set_input_files("signature.png")
    _save_signature(page)
