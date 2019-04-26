import os
from elements import *

# import custom addons here
# from addons._ import *
from addons_dir.speech_control import *

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
        logo_row = self.page.get_first("logo")
        navbar = self.page.get_first("navbar")

        # all other modifications
        components_to_delete = []
        for mod in self.modifications:
            if "title_to" in mod:
                title = mod[9:]
                if logo_row != None:
                    logo_row[0].metadata["text"] = title
            if "remove_logo_bg" in mod:
                if logo_row != None:
                    logo_row[0].metadata["rounded"] = "false"
            if "restore_logo_bg" in mod:
                if logo_row != None:
                    logo_row[0].metadata["rounded"] = "true"
            if "remove_navbar" in mod:
                if navbar != None:
                    components_to_delete.append(navbar[1])
            if "restore_navbar" in mod:
                if navbar != None:
                    while navbar[1] in components_to_delete:
                        components_to_delete.remove(navbar[1])

        # deletes elements from page
        for i in components_to_delete:
            comp_index = len(self.page.sections)-2-i
            del self.page.sections[comp_index]

        return self.page

class AddonsServer(object): # saves modifications to file
    def __init__(self, page):
        self.page = page
        self.addons = [
            SpeechControlAddon(page)
        ]

        self.modifications_string = ""
        if os.path.isfile(".modifications"):
            f = open(".modifications", "r")
            self.modifications_string = f.read()
        self.server_commands = []

        # starts all addons
        for addon in self.addons:
            addon.start()

    def get_server_commands(self):
        commands = self.server_commands[:]
        self.server_commands = []
        return commands

    def on_update(self):
        mods_to_add = ""
        queued_clear = False
        for addon in self.addons:
            modifications_string = addon.get_modifications()
            mods_to_add = mods_to_add + "\n" + modifications_string
            server_cmds = addon.get_server_commands()
            if len(server_cmds) > 0:
                self.server_commands.extend(server_cmds)

        # for clearing all modifications
        if "clear" in mods_to_add:
            queued_clear = True
            mods_to_add = ""
            self.modifications_string = ""

        if (mods_to_add != "" and len(mods_to_add) > 3) or queued_clear == True:
            self.server_commands.append("refresh")

            # saves modifications to disk
            self.modifications_string = self.modifications_string + "\n" + mods_to_add
            mod_file = open(".modifications","w") 
            mod_file.write(self.modifications_string)
            mod_file.close()

