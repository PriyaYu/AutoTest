import os
import sys
import traceback
import random

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from unitScript.login import login
from unitScript.add_newsent import add_newsent
from unitScript.sign import sign
from config import REVIEWEE_EMAIL,REVIEWER_EMAIL,SIGN_EMAIL, SIGN_PASSWORD
PDF_PATH = os.path.join(PROJECT_ROOT, "Sequential_Signing_Order_Test.pdf")


def main() -> None:
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        login(driver, wait, NeedLogout= False, email = REVIEWEE_EMAIL)
        parallel_titles = add_newsent(
            driver, wait, pdf_path=PDF_PATH, start=1, end=1, IsSequence=False, mode="sent"
        )

        for email in random.sample(REVIEWER_EMAIL, k=len(REVIEWER_EMAIL)):
            login(driver, wait, NeedLogout= True, email=email)
            input("pause")
        #    sign(driver, wait, title=parallel_titles[-1] if parallel_titles else None, IsSequence=False)

    except Exception as exc:
        print(f"錯誤訊息：{exc}")
        traceback.print_exc()
        input("程式中斷，按 Enter 保持瀏覽器開著")
        return

    input("完成，按 Enter 關閉瀏覽器")
    driver.quit()


if __name__ == "__main__":
    main()
