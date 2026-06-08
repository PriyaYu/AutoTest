from flows.flow_login import login
from flows.flow_multi_document_request import multi_document_request


def test_multi_document_request(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        multi_document_request(page, sample_pdf_path)
