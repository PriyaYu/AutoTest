from flows.flow_create_request_validation import verify_create_request_validation
from flows.flow_login import login


def test_create_request_validation(page) -> None:
    login(page)
    for _ in range(1):
        verify_create_request_validation(page)
