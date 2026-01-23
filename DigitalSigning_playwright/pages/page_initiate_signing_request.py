from pages.page_menu import Menu


class InitiateSigningRequestPage:
    def __init__(self, page):
        self.page = page
        self.menu = Menu(page)

    @property
    def start_button(self):
        return self.page.get_by_text("Start", exact=True)

    @property
    def add_template_button(self):
        return self.page.get_by_role("button", name="Add Template")

    @property
    def upload_button(self):
        return self.page.get_by_role("button", name="Upload", exact=True)

    @property
    def file_input(self):
        return self.page.locator("input[type=\"file\"]")

    @property
    def name_inputs(self):
        return self.page.locator("#form_item_name")

    @property
    def email_inputs(self):
        return self.page.locator("#form_item_email")

    @property
    def role_inputs(self):
        return self.page.locator("#form_item_role")

    @property
    def new_recipient_button(self):
        return self.page.get_by_role("button", name="New Recipient")

    @property
    def subject_input(self):
        return self.page.get_by_role("textbox", name="* Subject")

    @property
    def save_as_template_button(self):
        return self.page.get_by_role("button", name="Save as Template")

    @property
    def search_all_contacts_input(self):
        return self.page.get_by_role("textbox", name="Search All Contacts")

    @property
    def next_button(self):
        return self.page.get_by_role("button", name="Next")

    @property
    def set_sequence_checkbox(self):
        return self.page.get_by_role("checkbox", name="Set signing order View")

    @property
    def signature_field_buttons(self):
        return self.page.get_by_role("button", name="Signature Field")

    @property
    def send_button(self):
        return self.page.get_by_role("button", name="Send")

    @property
    def confirm_yes_button(self):
        return self.page.get_by_role("button", name="Yes")

    @property
    def ok_button(self):
        return self.page.get_by_role("button", name="Ok")
