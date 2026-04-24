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
def page(request):
    with sync_playwright() as p:
        slow_mo = int(os.getenv("SLOW_MO", "500"))
        browser = p.chromium.launch(headless=False, slow_mo=slow_mo)  # 先用 False 方便看畫面
        context = browser.new_context()
        page = context.new_page()
        yield page
        
        # 如果測試失敗了，不要關閉瀏覽器，讓使用者可以檢查畫面
        if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
            import sys
            # 確保不會影響無頭模式 CI 測試，只在有畫面的時候卡住
            if os.getenv("CI") != "true":
                try:
                    from flows.flow_signup import _focus_terminal
                    _focus_terminal()
                    print("\n[DEBUG] Test failed. Browser is left open for inspection. Press Enter in terminal to close it...")
                    input()
                except Exception:
                    pass
        
        context.close()
        browser.close()

# 讓 fixture 可以知道測試結果 (成功或失敗)
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
