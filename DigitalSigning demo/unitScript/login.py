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


def login(driver, wait, NeedLogout= False, email=LOGIN_DEFAULT_EMAIL, password=LOGIN_DEFAULT_PASSWORD , captcha = LOGIN_DEFAULT_CAPTCHA) -> None:
    print(f"Login with email: {email}")
    
    #if NeedLogout:
        #driver.delete_all_cookies()
        #time.sleep(5)
        #user_menu_xpath = "//*[@id='ds-app']/section/header/section/div[3]"
        #logout_xpath = (
        #    "//div[contains(@class,'ant-dropdown') and contains(@class,'ant-dropdown-placement-bottomRight')]"
        #    "//li[@role='menuitem' and @data-menu-id='3']"
        #)
        #dropdown_xpath = (
        #    "//div[contains(@class,'ant-dropdown') and contains(@class,'ant-dropdown-placement-bottomRight')]"
        #)
        #user_menu = wait.until(EC.element_to_be_clickable((By.XPATH, user_menu_xpath)))
        #user_menu.click()
        #wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
        #logout_item = wait.until(EC.presence_of_element_located((By.XPATH, logout_xpath)))
        #driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", logout_item)
        #driver.execute_script("arguments[0].click();", logout_item)
        #here 

    driver.delete_all_cookies()
    time.sleep(5)

    driver.get(LOGIN_URL)
    driver.refresh()
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_EMAIL))).send_keys(email)
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_PASSWORD))).send_keys(password)
    wait.until(EC.visibility_of_element_located((By.XPATH, LOGIN_X_CAPTCHA))).send_keys(captcha)

    login_btn = wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_X_LOGIN)))
    driver.execute_script("arguments[0].click();", login_btn)
    #wait.until(EC.url_changes(LOGIN_URL))
    #wait.until(lambda d: "login" not in d.current_url)
