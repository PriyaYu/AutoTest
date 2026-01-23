import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

@pytest.fixture
def sample_pdf_path():
    repo_root = Path(__file__).resolve().parent
    return repo_root / "data" / "Sequential_Signing_Order_Test.pdf"

@pytest.fixture
def page():
    with sync_playwright() as p:
        slow_mo = int(os.getenv("SLOW_MO", "500"))
        browser = p.chromium.launch(headless=False, slow_mo=slow_mo)  # 先用 False 方便看畫面
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
