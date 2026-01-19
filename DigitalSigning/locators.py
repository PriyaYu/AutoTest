from config import WEBSITE_URL

LOGIN_URL = WEBSITE_URL + "/ds#/login"
DASHBOARD_URL = WEBSITE_URL + "/ds#/dashboard"

LOGIN_X_EMAIL = "//*[@id='ds-app']/div/section/input"
LOGIN_X_PASSWORD = "//*[@id='ds-app']/div/section/span/input"
LOGIN_X_CAPTCHA = "//*[@id='ds-app']/div/section/div[7]/input"
LOGIN_X_LOGIN = "//*[@id='ds-app']/div/section/div[8]"

MENU_X_DASHBOARD = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Dashboard']]"
MENU_X_TEMPLATES = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Templates']]"
MENU_X_DRAFTS = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Drafts']]"
MENU_X_FREQUENTCONTACTS = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Frequent Contacts']]"
MENU_X_MYSIGNATURE = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='My Signature']]"
MENU_X_ALL = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='All']]"
MENU_X_SENT = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Sent']]"
MENU_X_INBOX = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Inbox']]"
MENU_X_WAITINGFOROTHERS = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Waiting for Others']]"
MENU_X_EXPIRINGSOON = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Expiring Soon']]"
MENU_X_COMPLETED = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Completed']]"
MENU_X_REVIEW = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Review']]"
MENU_X_DELETED = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Deleted']]"
MENU_X_LOGOUT = "//*[@id='ds-app']//aside//ul//li[.//span[normalize-space()='Logout']]"

DASHBOARD_X_ADD_BTN = "#ds-app > section > section > section > main > section > section.get-start > div.body > div.body-item.sign-start > div > div.body-item-title > div"

RECIPIENT_X_ADD_BTN = "//*[@id='ds-app']/section/section/section/main/div/div[2]/button"
RECIPIENT_X_NAME = "//*[@id='form_item_name']"
RECIPIENT_X_EMAIL = "//*[@id='form_item_email']"
RECIPIENT_X_JOB = "//*[@id='form_item_job']"
RECIPIENT_X_MODAL = "//div[contains(@class,'ant-modal')][last()]"
RECIPIENT_X_OK = RECIPIENT_X_MODAL + "//button[contains(@class,'ant-btn-primary')]"

TEMPLATES_X_NEW_BTN = "//*[@id='ds-app']/section/section/section/main/div/div[2]/button/span"
TEMPLATES_X_DRAWER = "//div[contains(@class,'ant-drawer') and contains(@class,'ant-drawer-open')]"
TEMPLATES_X_UPLOAD_BTN = TEMPLATES_X_DRAWER + "//button[contains(@class,'upload-btn')]"
TEMPLATES_X_UPLOAD_INPUT = TEMPLATES_X_DRAWER + "//input[@type='file']"

DRAFT_X_SET_SEQUENCE = "/html/body/div[5]/div/div[2]/div/div/div[2]/section/div/div[2]/div[2]/div/section/div[1]/label/span[1]/input"
DRAFT_X_SET_SEQUENCE_FALLBACK = ("//label[.//span[contains(normalize-space(),'Sequence') or contains(normalize-space(),'Sequential') or contains(normalize-space(),'signing order') or contains(normalize-space(),'Signing Order')]]//input")
DRAFT_X_NAME = "//*[@id='form_item_name']"
DRAFT_X_EMAIL = "//*[@id='form_item_email']"
DRAFT_X_SUBJECT = "//*[@id='form_item_subject']"
DRAFT_X_SAVE_TO_CONTACT = "//*[@id='form_item_saveToFrequenctContact']"
DRAFT_X_ADD_RECIPIENT_BTN = ("//div[contains(@class,'ant-drawer') and contains(@class,'ant-drawer-open')]"
                             "//section[contains(@class,'add-recipients-container')]"
                             "//button[.//span[normalize-space()='New Recipient']]")
DRAFT_X_SIGNATURE_FIELD_BTN = ("//div[contains(@class,'ant-drawer') and contains(@class,'ant-drawer-open')]"
                               "//section[contains(@class,'document-tools')]"
                               "//section[contains(@class,'signing')]"
                               "//span[contains(@class,'signature-field')]")

DRAFT_X_POST_MENU_BTN = ( "//div[contains(@class,'ant-drawer-extra')]//button[contains(@class,'ant-dropdown-trigger')]")
DRAFT_X_POST_MENU_ITEM = (
    "//div[contains(@class,'ant-dropdown') and not(contains(@style,'display: none'))]"
    "//span[normalize-space()='Save to Draft']"
)

ADD_X_NEW_RECIPIENT = "//*[@id='form_item_role']"
ADD_X_SAVE_TEMPLATE_BTN = (TEMPLATES_X_DRAWER + "//div[contains(@class,'drawer-footer')]//span[normalize-space()='Save as Template']/ancestor::button[1]")
ADD_X_NEXT_BTN = (TEMPLATES_X_DRAWER + "//div[contains(@class,'drawer-footer')]//button[.//span[normalize-space()='Next']]")
ADD_X_SENT_BTN = (
    "//div[contains(@class,'ant-drawer') and contains(@class,'ant-drawer-open')]"
    "//div[contains(@class,'drawer-footer')]//button[.//span[normalize-space()='Send']]"
)
ADD_X_SENT_BTN_FALLBACK = ("//button[.//span[normalize-space()='Sent' or normalize-space()='Send'] or normalize-space()='Sent' or normalize-space()='Send']")
ADD_X_SENT_CONFIRM_BTN_YES = (
    "//div[contains(@class,'ant-modal') and contains(@class,'ant-modal-wrap')]"
    "//button[.//span[normalize-space()='Yes' or normalize-space()='Confirm' or normalize-space()='OK']]"
)
ADD_X_SENT_SUCCESS_MESSAGE_BTN = ("//div[contains(@class,'ant-modal')][.//div[contains(@class,'ant-result-success')]]//button[.//span[normalize-space()='Ok']]")
