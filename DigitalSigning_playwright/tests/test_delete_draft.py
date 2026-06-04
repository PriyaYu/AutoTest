from flows.flow_delete_draft import delete_draft
from flows.flow_login import login


def test_delete_draft(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        delete_draft(page, sample_pdf_path)
