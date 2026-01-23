class Dialog:
    def __init__(self, page):
        self.page = page

    @property
    def yes_button(self):
        return self.page.get_by_role("button", name="Yes")

    @property
    def ok_button(self):
        return self.page.get_by_role("button", name="Ok")
