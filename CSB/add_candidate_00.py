import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#  from selenium.webdriver.chrome.service import Service
#  from webdriver_manager.chrome import ChromeDriverManager
import time

def run_test(index):
    print(f"\n🚀 第 {index+1} 次測試開始")
    driver = webdriver.Chrome()
    try:
        # 第一步：開啟隨機 HKID 頁面
        driver.get("https://pinkylam.me/playground/hkid/")
        time.sleep(1)

        # 點擊「Random HKID」按鈕
        driver.find_element(By.XPATH, '//*[@id="randomHKID"]').click()
        time.sleep(2)

        # 第二步：前往建立 Candidate 頁面
        driver.get("http://10.68.30.118:5004/adp/addCandidate?date=Thu,%2025%20Sep%202025%2003:00:26%20GMT&startTime=Thu,%2025%20Sep%202025%2002:16:00%20GMT&endTime=Thu,%2025%20Sep%202025%2003:26:00%20GMT&timeslotID=468595&index=2&assignSeat=false")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "idPrefix")))
        
        # 第三步：貼上 HKID,聚焦到 idPrefix 輸入框
        input_element = driver.find_element(By.ID, "idPrefix")
        input_element.click()  # 聚焦
        time.sleep(0.5)

        # 貼上剪貼簿內容 (Command + V for macOS)
        ActionChains(driver).key_down(Keys.COMMAND).send_keys("v").key_up(Keys.COMMAND).perform()

        # 第四步：填入中文名（PP）
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div/form/div[4]/div[3]/div[1]/div/div/div[2]/div/div/input').send_keys("NEXIFY")

        # 第五步：填入出生年份（1992）
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div/form/div[4]/div[4]/div[1]/div/div/div[2]/div/div/input').send_keys("1992")

        # 第六步：填入 Email
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div/form/div[4]/div[4]/div[2]/div/div/div[2]/div/div/input').send_keys("shuang@nexify.com.hk")

        # 第七步：填入電話
        driver.find_element(By.ID, "PhoneNumber").send_keys("91234567")

        # 第八步：點擊圖片上傳（模擬點擊圖片按鈕）
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div/form/div[4]/div[4]/div[3]/div/div/div[2]/div/div/img').click()
        time.sleep(1)

        # 第九步：點選一個選項（單選框）- 使用更穩定的 JavaScript 強制點擊
        radio_xpath = '//*[@id="main"]/div/div/div/form/div[5]/div[2]/div[1]/div/div/div[2]/div/div[2]/div/label/span[2]/div'
        radio_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, radio_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", radio_element)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", radio_element)

        # 第十步：送出表單（使用 JavaScript 強制點擊，避免被遮擋）
        submit_xpath = '//*[@id="main"]/div/div/div/form/div[1]/div/div[2]/button[2]'
        submit_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, submit_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)

        # 等待幾秒觀察送出後畫面
        time.sleep(3)

        print("✅ 測試流程完成")

    except Exception as e:
        print("❌ 測試過程中出現錯誤：", e)
        print("⚠️ 請檢查 debug_screen.png 了解錯誤當下畫面")
        traceback.print_exc()

    finally:
        driver.quit()

# 如果要單獨執行就移除註解
#if __name__ == "__main__":
#    run_test(0)
