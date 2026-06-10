from flows.flow_change_password_history import change_password_history
from flows.flow_signup import signup


def test_change_password_history(page) -> None:
    # Throwaway account: validate the last-10 password-history policy without
    # touching the main account.
    email, old_password = signup(page)
    change_password_history(page, email, old_password)
