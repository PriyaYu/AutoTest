class Menu:
    def __init__(self, page):
        self.page = page

    def menu_item(self, name: str):
        return self.page.get_by_role("menuitem", name=name)

    @property
    def dashboard_tab(self):
        return self.menu_item("Dashboard")

    @property
    def templates_tab(self):
        return self.menu_item("Templates")

    @property
    def drafts_tab(self):
        return self.menu_item("Drafts")

    @property
    def frequent_contacts_tab(self):
        return self.menu_item("Frequent Contacts")

    @property
    def my_signature_tab(self):
        return self.menu_item("My Signature")

    @property
    def all_tab(self):
        return self.menu_item("All")

    @property
    def sent_tab(self):
        return self.menu_item("Sent")

    @property
    def inbox_tab(self):
        return self.menu_item("Inbox")

    @property
    def waiting_for_others_tab(self):
        return self.menu_item("Waiting for Others")

    @property
    def expiring_soon_tab(self):
        return self.menu_item("Expiring Soon")

    @property
    def completed_tab(self):
        return self.menu_item("Completed")

    @property
    def review_tab(self):
        return self.menu_item("Review")

    @property
    def deleted_tab(self):
        return self.menu_item("Deleted")

    @property
    def logout_tab(self):
        return self.menu_item("Logout")
