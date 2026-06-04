from flows.flow_login import login
from flows.flow_view_request import view_request


def test_view_request(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        view_request(page, sample_pdf_path)
