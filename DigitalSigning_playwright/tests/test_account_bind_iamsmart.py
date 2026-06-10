import os
from playwright.sync_api import expect

from flows.flow_login import login
from flows.flow_iamsmart import (
    register_iamSmart,
    login_with_iam_smart,
    logout_from_profile_menu,
    ensure_iamsmart_unregistered,
)

def test_iam_smart_binding_flow(page) -> None:
    password = os.getenv("LOGIN_DEFAULT_PASSWORD", "")
    login(page, force_login=True)
    # Start from a clean state: if the account is already bound, unbind first.
    ensure_iamsmart_unregistered(page)
    register_iamSmart(page, action="register", password=password)
    logout_from_profile_menu(page)
    login_with_iam_smart(page)
    register_iamSmart(page, action="unregister")
