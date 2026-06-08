from flows.flow_change_password import change_password
from flows.flow_login import login


def test_change_password(page) -> None:
    login(page)
    for _ in range(1):
        change_password(page)
