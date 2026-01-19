# add_recipient.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators import (
    DASHBOARD_URL,
    MENU_X_FREQUENTCONTACTS,
    RECIPIENT_X_ADD_BTN,
    RECIPIENT_X_EMAIL,
    RECIPIENT_X_JOB,
    RECIPIENT_X_MODAL,
    RECIPIENT_X_NAME,
    RECIPIENT_X_OK,
)
from unitScript.utils import _click

def add_recipients(driver, wait, start=1, end=30):
    driver.get(DASHBOARD_URL)
    _click(driver, wait, MENU_X_FREQUENTCONTACTS)
    wait.until(EC.url_contains("frequent-contacts"))

    for i in range(start, end + 1):
        wait.until(EC.element_to_be_clickable((By.XPATH, RECIPIENT_X_ADD_BTN))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, RECIPIENT_X_NAME))).send_keys(f"recipient{i}")
        wait.until(EC.visibility_of_element_located((By.XPATH, RECIPIENT_X_EMAIL))).send_keys("zihsyuan0603@gmail.com")
        wait.until(EC.visibility_of_element_located((By.XPATH, RECIPIENT_X_JOB))).send_keys(f"recipient JT{i}")
        wait.until(EC.visibility_of_element_located((By.XPATH, RECIPIENT_X_MODAL)))
        ok_btn = wait.until(EC.element_to_be_clickable((By.XPATH, RECIPIENT_X_OK)))
        driver.execute_script("arguments[0].click();", ok_btn)
