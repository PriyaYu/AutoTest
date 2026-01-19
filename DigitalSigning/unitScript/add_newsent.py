import time
from datetime import datetime

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from config import SIGN_EMAIL
from locators import (
    DASHBOARD_URL,
    DASHBOARD_X_ADD_BTN,
    MENU_X_TEMPLATES,
    TEMPLATES_X_NEW_BTN,
    ADD_X_NEXT_BTN,
    ADD_X_SAVE_TEMPLATE_BTN,
    TEMPLATES_X_DRAWER,
    DRAFT_X_SET_SEQUENCE,
    DRAFT_X_SET_SEQUENCE_FALLBACK,
    DRAFT_X_ADD_RECIPIENT_BTN,
    DRAFT_X_SAVE_TO_CONTACT,
    DRAFT_X_SIGNATURE_FIELD_BTN,
    DRAFT_X_SUBJECT,
    TEMPLATES_X_UPLOAD_BTN,
    TEMPLATES_X_UPLOAD_INPUT,
    ADD_X_SENT_BTN,
    ADD_X_SENT_BTN_FALLBACK,
    ADD_X_SENT_CONFIRM_BTN_YES,
    ADD_X_SENT_SUCCESS_MESSAGE_BTN,
    DRAFT_X_POST_MENU_BTN,
    DRAFT_X_POST_MENU_ITEM
)
from unitScript.utils import _click, _upload_pdf


def add_newsent(driver, wait, pdf_path: str, start=1, end=5, IsSequence=False, mode: str = "sent"):
    driver.get(DASHBOARD_URL)
    wait.until(EC.url_contains("dashboard"))
    short_wait = WebDriverWait(driver, 30)
    created_titles = []

    for i in range(start, end + 1):
        if mode == "template":
            _click(driver, wait, MENU_X_TEMPLATES)
            _click(driver, wait, TEMPLATES_X_NEW_BTN)
        else:
            _click(driver, wait, DASHBOARD_X_ADD_BTN)

        _upload_pdf(driver, wait, pdf_path, TEMPLATES_X_DRAWER, TEMPLATES_X_UPLOAD_BTN, TEMPLATES_X_UPLOAD_INPUT)

        if IsSequence:
            try:
                _click(driver, wait, DRAFT_X_SET_SEQUENCE)
            except TimeoutException:
                seq_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, DRAFT_X_SET_SEQUENCE_FALLBACK)))
                driver.execute_script("arguments[0].click();", seq_checkbox)

        total_recipients = len(SIGN_EMAIL)
        date_prefix = datetime.now().strftime("%Y%m%d_%H%M")
        for _ in range(total_recipients - 1):
            _click(driver, wait, DRAFT_X_ADD_RECIPIENT_BTN)
            #try:
            #    _click(driver, wait, DRAFT_X_ADD_RECIPIENT_BTN)
            #except TimeoutException:
            #    add_btn = wait.until(EC.presence_of_element_located((By.XPATH, DRAFT_X_ADD_RECIPIENT_BTN)))
            #    driver.execute_script("arguments[0].click();", add_btn)

        recipients = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.recipient-draggable"))
        )
        for idx, recipient in enumerate(recipients[:total_recipients], start=1):
            name = recipient.find_element(By.CSS_SELECTOR, "input#form_item_name")
            name.clear()
            name.send_keys(f"Recipient_{date_prefix}_-{idx}")

            email = recipient.find_element(By.CSS_SELECTOR, "input#form_item_email")
            email.clear()
            email.send_keys(SIGN_EMAIL[idx - 1])

            role = recipient.find_element(By.CSS_SELECTOR, "input#form_item_role")
            role.clear()
            role.send_keys(f"Recipient_JT_{date_prefix}_-{idx}")

        #save_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, DRAFT_X_SAVE_TO_CONTACT)))
        #driver.execute_script("arguments[0].click();", save_checkbox)

        subject = wait.until(EC.visibility_of_element_located((By.XPATH, DRAFT_X_SUBJECT)))
        subject.clear()
        if mode == "draft":
            title = f"Draft_{date_prefix}"
            subject.send_keys(title)
        elif mode == "template":
            title = f"Template_{date_prefix}"
            subject.send_keys(title)
        else:
            if IsSequence:
                title = f"SequenceSigning_{date_prefix}"
                subject.send_keys(title)
            else:
                title = f"ParallelSigning_{date_prefix}"
                subject.send_keys(title)

        created_titles.append(title)

        doc_ready_xpath = "//section[contains(@class,'doc-list')]//div[contains(@class,'one-doc')]"

        if mode == "draft":
            wait.until(EC.presence_of_element_located((By.XPATH, doc_ready_xpath)))
            _click(driver, wait, ADD_X_NEXT_BTN)
            menu_btn = wait.until(EC.visibility_of_element_located((By.XPATH, DRAFT_X_POST_MENU_BTN)))
            ActionChains(driver).move_to_element(menu_btn).perform()
            try:
                menu_item = short_wait.until(EC.presence_of_element_located((By.XPATH, DRAFT_X_POST_MENU_ITEM)))
            except TimeoutException:
                ActionChains(driver).move_to_element(menu_btn).perform()
                menu_item = wait.until(EC.presence_of_element_located((By.XPATH, DRAFT_X_POST_MENU_ITEM)))
            driver.execute_script("arguments[0].click();", menu_item)
                
        elif mode == "template":
            save_btn = wait.until(EC.presence_of_element_located((By.XPATH, ADD_X_SAVE_TEMPLATE_BTN)))
            driver.execute_script("arguments[0].click();", save_btn)
        
        else:
            wait.until(EC.presence_of_element_located((By.XPATH, doc_ready_xpath)))
            _click(driver, wait, ADD_X_NEXT_BTN)
            signature_buttons = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, DRAFT_X_SIGNATURE_FIELD_BTN))
            )
            for btn in signature_buttons[:total_recipients]:
                driver.execute_script("arguments[0].click();", btn)

            try:
                _click(driver, wait, ADD_X_SENT_BTN)
            except TimeoutException:
                sent_btn = wait.until(EC.presence_of_element_located((By.XPATH, ADD_X_SENT_BTN_FALLBACK)))
                driver.execute_script("arguments[0].click();", sent_btn)

            confirm_btn = short_wait.until(
                EC.presence_of_element_located((By.XPATH, ADD_X_SENT_CONFIRM_BTN_YES))
            )
            driver.execute_script("arguments[0].click();", confirm_btn)

            success_btn = short_wait.until(
                EC.presence_of_element_located((By.XPATH, ADD_X_SENT_SUCCESS_MESSAGE_BTN))
            )
            driver.execute_script("arguments[0].click();", success_btn)
            try:
                wait.until(EC.invisibility_of_element_located((By.XPATH, TEMPLATES_X_DRAWER)))
            except TimeoutException:
                pass

    return created_titles
