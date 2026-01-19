from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_checkin():
    print("🚀 開始 Check-in 測試")
    driver = webdriver.Chrome()
    try:
        driver.get("http://10.68.30.118:5004/adp/monitor/130006")
        time.sleep(1)

        # 切換語系
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="nav-dropdown-language"]/div/div[2]'))).click()
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="basic-navbar-nav"]/div/div/div/a[5]'))).click()
        time.sleep(1)

        # 選擇場次
        select = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="uncontrolled-tab-example-tabpane-Attendance"]/div[1]/div[1]/select')))
        select.click()
        option = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="uncontrolled-tab-example-tabpane-Attendance"]/div[1]/div[1]/select/option[14]')))
        option.click()
        time.sleep(1)

        # 複製第一位考生 HKID
        hkid_td = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="uncontrolled-tab-example-tabpane-Attendance"]/div[2]/div/table/tbody/tr[1]/td[1]')))
        hkid_value = hkid_td.text.strip()

        # 點擊 Checkin 按鈕
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[2]/button'))).click()

        # 貼上 HKID
        hkid_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[1]/div[1]/div[1]/div/div/div[2]/div/div/input')))
        hkid_input.click()
        time.sleep(0.5)
        hkid_input.send_keys(hkid_value)

        # 點擊確認按鈕
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div[3]/button[2]'))).click()
        print("✅ Check-in 測試成功")

        time.sleep(2)

    except Exception as e:
        print("❌ 測試中發生錯誤：", e)
    finally:
        driver.quit()
