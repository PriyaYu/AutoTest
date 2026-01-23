class LoginPage:
    def __init__(self, page):
        self.page = page

    @property
    def email_input(self):
        return self.page.get_by_role("textbox", name="Enter your email address")

    @property
    def password_input(self):
        return self.page.locator("input[type=\"password\"]")

    @property
    def captcha_input(self):
        return self.page.get_by_role("textbox", name="Enter the text")

    @property
    def sign_in_button(self):
        return self.page.get_by_text("Sign In", exact=True)

    def fill_email(self, email):
        self.email_input.fill(email)
        return self

    def fill_password(self, password):
        self.password_input.fill(password)
        return self

    def fill_captcha(self, captcha):
        self.captcha_input.fill(captcha)
        return self

    def submit(self):
        self.sign_in_button.click()
        return self.page
