"""main.py

Run the full flow in ONE browser session:
1) Login (manual captcha)
2) Add frequent contacts (1..30)
3) Add drafts (1..30)
4) Add templates (1..5)

Run:
  python3 main.py
"""

import traceback

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from unitScript.login import login
from unitScript.login_validation import login_validation
from unitScript.add_recipient import add_recipients
from unitScript.add_newsent import add_newsent
from unitScript.sign import sign
from config import (
    RUN_DRAFTS,
    RUN_LOGIN,
    RUN_RECIPIENTS,
    RUN_TEMPLATE,
)

from config import SIGN_PASSWORD
#Config area
SIGN_EMAIL = ["zihsyuan0603@gmail.com", "pyu@nexify.com.hk"]
PDF_PATH = "Sequential_Signing_Order_Test.pdf"


def main() -> None:
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        # 1) Login (will pause for captcha)
        if RUN_LOGIN:
            login_validation(driver, wait)
            login(driver, wait)

        # 2) Add recipients (requires logged-in session)
        if RUN_RECIPIENTS:
            add_recipients(driver, wait, start=1, end=5)

        # 3) Add drafts
        if RUN_DRAFTS:
            add_newsent(driver, wait, pdf_path=PDF_PATH, start=1, end=1, IsSequence=False, mode="draft")

        # 4) Add Template
        if RUN_TEMPLATE:
            add_newsent(driver, wait, pdf_path=PDF_PATH, start=1, end=1, IsSequence=False, mode="template")

    except Exception as exc:
        print("\n=== 程式中斷：發生錯誤 ===")
        print(f"錯誤訊息：{exc}")
        traceback.print_exc()
        input("程式中斷，按 Enter 保持瀏覽器開著")
        return

    input("完成，按 Enter 關閉瀏覽器")
    driver.quit()


if __name__ == "__main__":
    main()
