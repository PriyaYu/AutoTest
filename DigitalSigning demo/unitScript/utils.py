from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def _click(driver, wait, selector: str) -> None:
    by = By.CSS_SELECTOR if " > " in selector or selector.strip().startswith("body") else By.XPATH
    el = wait.until(EC.element_to_be_clickable((by, selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    driver.execute_script("arguments[0].click();", el)


def _upload_pdf(driver, wait, pdf_path: str, drawer_xpath: str, upload_btn_xpath: str, upload_input_xpath: str) -> None:
    file_path = Path(pdf_path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    wait.until(EC.visibility_of_element_located((By.XPATH, drawer_xpath)))
    wait.until(EC.visibility_of_element_located((By.XPATH, upload_btn_xpath)))
    file_inputs = driver.find_elements(By.XPATH, upload_input_xpath)
    if not file_inputs:
        file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    if file_inputs:
        file_inputs[0].send_keys(str(file_path))
        return

    raise RuntimeError("No file input found for upload. The upload dialog might be native.")
