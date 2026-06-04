from flows.flow_cancel_delete_request import cancel_delete_request
from flows.flow_login import login


def test_cancel_delete_request(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        cancel_delete_request(page, sample_pdf_path)
