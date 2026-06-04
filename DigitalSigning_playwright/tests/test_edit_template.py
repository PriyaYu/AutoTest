from flows.flow_edit_template import edit_template
from flows.flow_login import login


def test_edit_template(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        edit_template(page, sample_pdf_path)
