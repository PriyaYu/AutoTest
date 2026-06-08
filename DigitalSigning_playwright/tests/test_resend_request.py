from flows.flow_login import login
from flows.flow_resend_request import resend_request


def test_resend_request(page) -> None:
    login(page)
    for _ in range(1):
        resend_request(page)
