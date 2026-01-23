import os
import sys
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from unitScript.login import login
from unitScript.add_recipient import add_recipients
from unitScript.add_newsent import add_newsent
from unitScript.sign import sign
from unitScript.utils import _click
from locators import DASHBOARD_URL, MENU_X_ALL
from config import SIGN_EMAIL, SIGN_PASSWORD
PDF_PATH = os.path.join(PROJECT_ROOT, "Sequential_Signing_Order_Test.pdf")


def confirm_title_absent(driver, wait, title: str) -> bool:
    driver.get(DASHBOARD_URL)
    wait.until(EC.url_contains("dashboard"))
    _click(driver, wait, MENU_X_ALL)
    row_xpath = (
        "//tr[.//div[contains(@class,'title') and normalize-space(text())="
        f"'{title}']]"
    )
    return len(driver.find_elements(By.XPATH, row_xpath)) == 0


def sign_sequence_with_checks(driver, wait, title: str) -> None:
    for idx, signer_email in enumerate(SIGN_EMAIL):
        for check_email in SIGN_EMAIL[idx + 1 :]:
            login(driver, wait, NeedLogout=True, email=check_email, password=SIGN_PASSWORD)
            absent = confirm_title_absent(driver, wait, title)
            print(f"[check] {check_email} sees title: {'NO' if absent else 'YES'}")
        login(driver, wait, NeedLogout=True, email=signer_email, password=SIGN_PASSWORD)
        sign(driver, wait, title=title, IsSequence=True)


def main() -> None:
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        # Add New Sent - Sequence
        login(driver, wait)
        sequence_titles = add_newsent(
            driver, wait, pdf_path=PDF_PATH, start=1, end=1, IsSequence=True, mode="sent"
        )

        # Sign - Sequence
        for email in SIGN_EMAIL:
            login(driver, wait, NeedLogout=True, email=email, password=SIGN_PASSWORD)
            sign(driver, wait, title=sequence_titles[-1], IsSequence=True)

        # Add New Sent - Sequence
        login(driver, wait)
        sequence_titles = add_newsent(
            driver, wait, pdf_path=PDF_PATH, start=1, end=1, IsSequence=True, mode="sent"
        )          

        # Sign - Wrong Sequence
        if sequence_titles:
            sign_sequence_with_checks(driver, wait, sequence_titles[-1])

    except Exception as exc:
        print(f"錯誤訊息：{exc}")
        traceback.print_exc()
        input("程式中斷，按 Enter 保持瀏覽器開著")
        return

    input("完成，按 Enter 關閉瀏覽器")
    driver.quit()


if __name__ == "__main__":
    main()
