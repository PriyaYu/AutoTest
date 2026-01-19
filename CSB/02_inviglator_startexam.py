from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_startexam():
    print("🚀 開始考試流程")
    driver = webdriver.Chrome()
    try:
        driver.get("http://10.68.30.118:5004/adp/monitor/347741")
        time.sleep(1)

        # 點選語言切換
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="nav-dropdown-language"]/div/img'))).click()
        time.sleep(0.5)

        # 點選左側選單第 6 項
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="basic-navbar-nav"]/div/div/div/a[6]'))).click()
        time.sleep(1)

        # 點選開始考試按鈕
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div/div[2]/div/div[1]/div[3]/button'))).click()

        # 輸入 START
        input_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div[2]/input')))
        input_box.send_keys("START")

        # 點擊確認按鈕
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div/div[3]/button[2]'))).click()

        print("✅ 成功送出開始考試")
        time.sleep(2)

    except Exception as e:
        print("❌ 錯誤：", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_startexam()