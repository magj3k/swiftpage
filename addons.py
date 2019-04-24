import os

# import custom addons here
# import addons._

class AddonsModifier(object): # loads saved modifications and applies them to current page
    def __init__(self, page):
        self.page = page

        # loads modifications
        self.modifications = []
        if os.path.isfile(".modifications"):
            f = open(".modifications", "r")
            for line in f:
              self.modifications.append(line)

    def generate(self):
        return self.page

class AddonsServer(object): # saves modifications to file
    def __init__(self, page):
        self.page = page
        self.addons = []

        self.modifications_string = ""
        if os.path.isfile(".modifications"):
            f = open(".modifications", "r")
            self.modifications_string = f.read()

    def on_update(self):
        mods_to_add = ""
        for addon in self.addons:
            modifications_string = addon.get_modifications()
            mods_to_add = mods_to_add + "\n" + modifications_string

        if mods_to_add != "" and len(mods_to_add) > 3:
            # saves modifications to disk
            self.modifications_string = self.modifications_string + "\n" + mods_to_add
            mod_file = open(".modifications","w") 
            mod_file.write(self.modifications_string)
            mod_file.close() 

class Addon(object): # can be subclassed to create custom addons
    def __init__(self, page):
        self.page = page
        self.queued_modifications = []

    def get_modifications(self): # each modification should be a string
        modification_string = ""
        for i in range(len(self.queued_modifications)):
            mod = self.queued_modifications[i]
            if i == 0:
                modification_string =  modification_string + mod
            else:
                modification_string =  modification_string + "\n" + mod

        self.queued_modifications = []
        return modification_string

