from flows.flow_change_full_name import change_full_name
from flows.flow_login import login


def test_change_full_name(page) -> None:
    login(page)
    for _ in range(1):
        change_full_name(page)
