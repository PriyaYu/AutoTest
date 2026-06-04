import re
from datetime import datetime

from playwright.sync_api import expect

from pages.page_menu import Menu


def _open_edit_dialog(page):
    """Open My Profile info via the top-right user menu, click Edit, and return
    the (dialog, username_input) of the 'Edit Username' modal."""
    page.locator(".user-wrap").first.click()
    page.get_by_text("My Profile info", exact=False).first.click()
    expect(page).to_have_url(re.compile("my-profile-info"))
    page.get_by_role("button", name="Edit").first.click()

    dialog = page.get_by_role("dialog", name="Edit Username")
    expect(dialog).to_be_visible(timeout=15000)
    username = dialog.get_by_placeholder("Enter new username")
    expect(username).to_be_visible(timeout=15000)
    return dialog, username


def _read_current_name(page) -> str:
    dialog, username = _open_edit_dialog(page)
    name = username.input_value().strip()
    dialog.get_by_role("button", name="Cancel").click()
    expect(dialog).to_be_hidden(timeout=15000)
    return name


def _set_name(page, new_name: str):
    dialog, username = _open_edit_dialog(page)
    username.fill(new_name)
    dialog.get_by_role("button", name="Save").click()
    # Wait for the modal to fully close before touching the rest of the page.
    expect(dialog).to_be_hidden(timeout=15000)
    page.wait_for_timeout(500)


def _assert_welcome_contains(page, name: str):
    Menu(page).dashboard_tab.click()
    expect(page.locator(".dashboard-container .welcome")).to_contain_text(name, timeout=20000)


def _sanitize(name: str) -> str:
    """The username field only accepts letters, numbers and underscores. The
    stored name may contain other characters (e.g. 'CHAN, Dai Dai'), so collapse
    any invalid run into a single underscore for a valid restore target. This is
    idempotent: once restored, the sanitized name re-sanitizes to itself."""
    sanitized = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")
    return sanitized or "QA_TestUser"


def change_full_name(page) -> dict:
    # Capture the current name. The original may contain characters the edit
    # field rejects, so we restore to a sanitized (valid) equivalent.
    original = _read_current_name(page)
    assert original, "Could not read the current full name"
    restore_target = _sanitize(original)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_name = f"QA_AutoTest_{timestamp}"

    # Change to the new name and verify it shows up on the dashboard greeting.
    _set_name(page, new_name)
    _assert_welcome_contains(page, new_name)

    # Restore the (sanitized) original name and verify the greeting reverts.
    _set_name(page, restore_target)
    _assert_welcome_contains(page, restore_target)

    return {"original": original, "new": new_name, "restored": restore_target}
