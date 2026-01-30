from flows.flow_add_recipient import add_recipient
from flows.flow_login import login


def test_add_recipient(page) -> None:
    login(page)
    for _ in range(1):
        add_recipient(page)
