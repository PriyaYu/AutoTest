import time
from datetime import datetime

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from locators import (
    MENU_X_ALL,
    TEMPLATES_X_DRAWER,
    ADD_X_SENT_CONFIRM_BTN_YES,
    ADD_X_SENT_SUCCESS_MESSAGE_BTN
)
from unitScript.utils import _click


def sign(driver, wait, title=None, IsSequence=False):
    wait.until(EC.url_contains("dashboard"))
    short_wait = WebDriverWait(driver, 5)
    _click(driver, wait, MENU_X_ALL)
    short_wait = WebDriverWait(driver, 10)


    row_xpath = (
        "//tr[.//div[contains(@class,'title') and normalize-space(text())="
        f"'{title}']]"
    )
    row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
    sign_btn_xpath = ".//button[.//span[normalize-space(text())='Sign']]"
    sign_btn = None
    for attempt in range(2):
        sign_btns = row.find_elements(By.XPATH, sign_btn_xpath)
        if sign_btns:
            sign_btn = sign_btns[0]
            break
        if attempt == 0:
            driver.refresh()
            wait.until(EC.url_contains("dashboard"))
            _click(driver, wait, MENU_X_ALL)
            row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
    if sign_btn is None:
        raise TimeoutException(f"Sign button not found for title: {title}")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_btn)
    wait.until(EC.element_to_be_clickable(sign_btn)).click()

    unsigned_xpath = (
        "//div[contains(@class,'resize-drag')]"
        "//div[contains(@class,'name') and normalize-space(text())='Click to sign']"
    )
    modal_sign_xpath = (
        "//div[contains(@class,'ant-modal') and contains(@class,'ant-modal-wrap')]"
        "//button[.//span[normalize-space(text())='Sign']]"
    )
    modal_wrap_xpath = "//div[contains(@class,'ant-modal') and contains(@class,'ant-modal-wrap')]"
    draw_signature_msg_xpath = "//div[contains(@class,'ant-message')]//span[normalize-space(text())='Please draw your signature']"
    signature_canvas_css = "canvas[data-v-66a0d92e]"

    input("Paused. Press Enter to continue...")

    had_unsigned = False
    while True:
        try:
            unsigned_targets = short_wait.until(
                EC.presence_of_all_elements_located((By.XPATH, unsigned_xpath))
            )
        except TimeoutException:
            unsigned_targets = []

        if not unsigned_targets:
            break

        had_unsigned = True
        try:
            target = unsigned_targets[0]
            container = target.find_element(By.XPATH, "./ancestor::div[contains(@class,'resize-drag')]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
            try:
                sign_hotspot = container.find_element(By.CSS_SELECTOR, "div.sign-btn")
            except Exception:
                sign_hotspot = target
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_hotspot)
            driver.execute_script("arguments[0].click();", sign_hotspot)
            sign_btn = wait.until(EC.element_to_be_clickable((By.XPATH, modal_sign_xpath)))
            sign_btn.click()
            if driver.find_elements(By.XPATH, draw_signature_msg_xpath):
                canvas = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, signature_canvas_css)))
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(canvas, 10, 10).click_and_hold()
                actions.move_by_offset(40, 10)
                actions.move_by_offset(40, -10)
                actions.move_by_offset(40, 15)
                actions.release()
                actions.perform()
                sign_btn = wait.until(EC.element_to_be_clickable((By.XPATH, modal_sign_xpath)))
                sign_btn.click()
            short_wait.until(EC.invisibility_of_element_located((By.XPATH, modal_wrap_xpath)))
        except StaleElementReferenceException:
            continue

    if not had_unsigned or not unsigned_targets:
        print("沒有未簽欄位，點擊 Confirm")
        confirm_xpath = (
            f"{TEMPLATES_X_DRAWER}"
            "//div[contains(@class,'drawer-footer')]//button[.//span[normalize-space()='Confirm']]"
        )
        _click(driver, wait, confirm_xpath)
        
        confirm_btn = short_wait.until(
            EC.presence_of_element_located((By.XPATH, ADD_X_SENT_CONFIRM_BTN_YES))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)

        success_btn = short_wait.until(
            EC.presence_of_element_located((By.XPATH, ADD_X_SENT_SUCCESS_MESSAGE_BTN))
        )
        driver.execute_script("arguments[0].click();", success_btn)
