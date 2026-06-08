from flows.flow_login import login
from flows.flow_save_to_frequent_contact import save_to_frequent_contact


def test_save_to_frequent_contact(page, sample_pdf_path) -> None:
    login(page)
    for _ in range(1):
        save_to_frequent_contact(page, sample_pdf_path)
