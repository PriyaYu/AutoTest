import os
import shutil
from pathlib import Path

from playwright.sync_api import expect

from flows.flow_initiate_signing_request import initiate_signing_request
from flows.flow_view_request import _open_request_view


def multi_document_request(page, pdf_path) -> dict:
    """Create and send a request with TWO documents, then verify the sent
    request's detail view reports two documents."""
    recipient_emails = [e.strip() for e in os.getenv("SIGN_EMAIL", "").split(",") if e.strip()]
    assert recipient_emails, "SIGN_EMAIL must contain at least one recipient"
    recipient = recipient_emails[:1]  # one recipient is enough for a multi-doc check

    # Create a distinct second document (same content, different filename).
    second = Path("/tmp") / f"second_{Path(pdf_path).name}"
    shutil.copy(pdf_path, second)

    _, title = initiate_signing_request(
        page=page, pdf_path=[str(pdf_path), str(second)], recipient_emails=recipient
    )

    # The sent request's detail view should list two documents.
    _open_request_view(page, title)
    drawer = page.locator(".document-sign-drawer.is-view")
    expect(drawer).to_be_visible(timeout=15000)
    expect(drawer.get_by_text("Documents (2)", exact=False).first).to_be_visible(timeout=10000)

    return {"title": title, "documents": 2}
