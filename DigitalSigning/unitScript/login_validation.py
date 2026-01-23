import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config import LOGIN_DEFAULT_EMAIL, LOGIN_DEFAULT_PASSWORD,LOGIN_DEFAULT_CAPTCHA
from locators import (
    LOGIN_URL,
    LOGIN_X_CAPTCHA,
    LOGIN_X_EMAIL,
    LOGIN_X_PASSWORD,
    LOGIN_X_LOGIN,
)


def login_validation(driver, wait, NeedLogout= False, email=LOGIN_DEFAULT_EMAIL, password=LOGIN_DEFAULT_PASSWORD , captcha = LOGIN_DEFAULT_CAPTCHA) -> None:
    print(f"Login with email: {email}")
    
    driver.get(LOGIN_URL)

    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_EMAIL))).send_keys(email)
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_PASSWORD))).send_keys(password+"1")
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_CAPTCHA))).send_keys(captcha)
    login_btn = wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_X_LOGIN)))
    driver.execute_script("arguments[0].click();", login_btn)
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[contains(@class,'ant-message-custom-content') and contains(@class,'ant-message-error')]//span[normalize-space()='Authentication failed']",
            )
        )
    )

    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_EMAIL))).send_keys(email)
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_PASSWORD))).send_keys(password)
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_CAPTCHA))).send_keys(captcha+"1")
    login_btn = wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_X_LOGIN)))
    driver.execute_script("arguments[0].click();", login_btn)
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[contains(@class,'ant-message-custom-content') and contains(@class,'ant-message-error')]//span[normalize-space()='Incorrect Captcha1']",
            )
        )
    )
