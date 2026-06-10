from flows.flow_change_password import change_password
from flows.flow_signup import signup


def test_change_password(page) -> None:
    # Use a fresh throwaway account (like the forgot-password test) so we never
    # touch the main account or fight the last-10 password-history policy.
    email, old_password = signup(page)
    change_password(page, email, old_password)
