from flows.flow_delete_template import delete_template
from flows.flow_login import login


def test_delete_template(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        delete_template(page, sample_pdf_path)
