


class AddonsModifier(object): # loads saved modifications and applies them to current page
    def __init__(self, page):
        self.page = page

    def generate(self):
        return self.page

class AddonsServer(object): # saves modifications to file
    def __init__(self, create_page_filename):
        self.create_page_filename = create_page_filename
        self.addons = []

    def on_update(self):
        for addon in self.addons:
            addon.get_modifications()

class Addon(object):
    def __init__(self, page):
        self.page = page

    def get_modifications(self):
        return None