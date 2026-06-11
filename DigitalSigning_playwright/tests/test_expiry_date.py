from flows.flow_expiry_date import verify_expiry_date
from flows.flow_login import login


def test_expiry_date(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        verify_expiry_date(page, sample_pdf_path)
