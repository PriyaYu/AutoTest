from flows.flow_dashboard import verify_dashboard
from flows.flow_login import login


def test_dashboard(page) -> None:
    login(page)
    for _ in range(1):
        verify_dashboard(page)
