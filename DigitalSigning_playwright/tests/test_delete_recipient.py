from flows.flow_delete_recipient import delete_recipient
from flows.flow_login import login


def test_delete_recipient(page) -> None:
    login(page)
    for _ in range(1):
        delete_recipient(page)
