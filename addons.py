import os, sys
from util.elements import *
sys.path.append('./addons')

# import custom addons here
from speech_control import *

class AddonsModifier(object): # loads saved modifications and applies them to current page
    def __init__(self, page):
        self.page = page

        # loads modifications
        self.modifications = []
        self.load_modifications()

    def load_modifications(self):
        self.modifications = []
        if os.path.isfile(".modifications"):
            f = open(".modifications", "r")
            for line in f:
              self.modifications.append(line)

    def generate(self):
        self.load_modifications()

        # all other modifications
        for mod in self.modifications:
            if "title_to" in mod:
                title = mod[9:]
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    logo_row[0].metadata["text"] = title
            elif "remove_logo_bg" in mod:
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    logo_row[0].metadata["rounded"] = "false"
            elif "remove_logo" in mod:
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    self.page.sections = self.page.sections[:logo_row[1]]+self.page.sections[logo_row[1]+1:]
            elif "restore_logo_bg" in mod:
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    logo_row[0].metadata["rounded"] = "true"
            elif "title_color_to" in mod:
                color = mod[15:]
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    logo_row[0].metadata["text-color"] = color
            elif "title_bg_to" in mod:
                color = mod[12:]
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    logo_row[0].metadata["background-colors"] = [color]
            elif "title_bg_left_to" in mod:
                color = mod[17:]
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    if len(logo_row[0].metadata["background-colors"]) == 1:
                        logo_row[0].metadata["background-colors"].append(logo_row[0].metadata["background-colors"][0])
                    logo_row[0].metadata["background-colors"][0] = color
            elif "title_bg_right_to" in mod:
                color = mod[18:]
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    if len(logo_row[0].metadata["background-colors"]) == 1:
                        logo_row[0].metadata["background-colors"].append(logo_row[0].metadata["background-colors"][0])
                    logo_row[0].metadata["background-colors"][1] = color
            elif "title_text_bg_to" in mod:
                color = mod[17:]
                logo_row = self.page.get_component("logo")
                if logo_row != None:
                    logo_row[0].metadata["rounded-color"] = color
            elif "whiteout_all" in mod:
                self.page.sections = []
            elif "add_logo" in mod:
                logo_row = self.page.get_component("logo")
                if logo_row == None:
                    self.page.sections.insert(0, Row("logo", {
                        "text": "My Projects SwiftPage",
                        "rounded": "true",
                        "background-colors": ["#f06d55", "#1a32d5"],
                    }))
            elif "footer_to" in mod:
                text = mod[10:]
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    footer_row[0].metadata["text"] = text
            elif "reset_footer" in mod:
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    footer_row[0].metadata["text"] = ""
            elif "add_footer" in mod:
                footer_row = self.page.get_component("footer")
                if footer_row == None:
                    self.page.sections.append(
                        Row("footer", {})
                    )
            elif "remove_footer" in mod:
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    self.page.sections = self.page.sections[:footer_row[1]]+self.page.sections[footer_row[1]+1:]
            elif "footer_color_to" in mod:
                color = mod[16:]
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    footer_row[0].metadata["text-color"] = color
            elif "footer_bg_to" in mod:
                color = mod[13:]
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    footer_row[0].metadata["background-colors"] = [color]
            elif "footer_bg_left_to" in mod:
                color = mod[18:]
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    if len(footer_row[0].metadata["background-colors"]) == 1:
                        footer_row[0].metadata["background-colors"].append(footer_row[0].metadata["background-colors"][0])
                    footer_row[0].metadata["background-colors"][0] = color
            elif "footer_bg_right_to" in mod:
                color = mod[19:]
                footer_row = self.page.get_component("footer")
                if footer_row != None:
                    if len(footer_row[0].metadata["background-colors"]) == 1:
                        footer_row[0].metadata["background-colors"].append(footer_row[0].metadata["background-colors"][0])
                    footer_row[0].metadata["background-colors"][1] = color
            elif "footer_match_bg" in mod:
                colors = []
                if len(mod) > 18: # extract first color
                    colors.append(mod[16:23])
                if len(mod) > 25: # extract second color
                    colors.append(mod[24:])

                if len(colors) > 0:
                    footer_row = self.page.get_component("footer")
                    if footer_row != None:
                        footer_row[0].metadata["background-colors"] = colors
            elif "logo_match_bg" in mod:
                colors = []
                if len(mod) > 16: # extract first color
                    colors.append(mod[14:21])
                if len(mod) > 23: # extract second color
                    colors.append(mod[22:])

                if len(colors) > 0:
                    logo_row = self.page.get_component("logo")
                    if logo_row != None:
                        logo_row[0].metadata["background-colors"] = colors
            elif "add_navbar" in mod:
                index = int(mod[11:])
                self.page.sections.insert(index, NavBar({
                    "facebook": {"address": "#"},
                    "soundcloud": {"address": "#"},
                    "linkedin": {"address": "#", "color": "#0a4767"},
                    # "unknown": {"address": "#"},
                }))
            elif "remove_navbar" in mod:
                number = int(mod[14:])
                navbar = self.page.get_component("navbar", number)
                if navbar != None:
                    self.page.sections = self.page.sections[:navbar[1]]+self.page.sections[navbar[1]+1:]

        return self.page

class AddonsServer(object): # saves modifications to file
    def __init__(self, page):
        self.page = page

        # maintains copy of modified page
        self.modifier = AddonsModifier(self.page)

        # addons
        self.addons = [
            SpeechControlAddon(page, self.modifier)
        ]

        # modifications saved to disk
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

