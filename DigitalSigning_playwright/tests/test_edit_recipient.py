from flows.flow_edit_recipient import edit_recipient
from flows.flow_login import login


def test_edit_recipient(page) -> None:
    login(page)
    for _ in range(1):
        edit_recipient(page)
