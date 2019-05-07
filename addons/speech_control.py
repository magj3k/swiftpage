import time
import threading
import sys
sys.path.append('./addons')
from addon import *
from speech_helper import *
from util.elements import *
import speech_recognition as sr # also implicity requires pyaudio

class SpeechControlAddon(Addon):
    def __init__(self, page, modifier = None):
        Addon.__init__(self, page)
        self.modifier = modifier

        self.recognizer = None
        self.microphone = None
        self.stop_listening = None

        self.console_mode = True

        self.context = {}
        self.reset_context()

    def get_current_page(self):
        return self.modifier.generate()

    def reset_context(self):
        self.context = {
            "variables": [],
            "object": None,
            "description": None,
            "color": None,
        }

    def process_statement(self, recognized_speech):
        while recognized_speech != None:
            match = None
            recognized_speech = extract_context(recognized_speech, self.context)
            print("Speech: " + recognized_speech)

            if match_expression("refresh", recognized_speech) != None: # server commands first
                self.server_commands.append("refresh")
                match = match_expression("refresh", recognized_speech)
            elif match_expression("scroll to bottom", recognized_speech) != None:
                self.server_commands.append("scroll_to_bottom")
                match = match_expression("scroll to bottom", recognized_speech)
            elif match_expression("scroll to top", recognized_speech) != None:
                self.server_commands.append("scroll_to_top")
                match = match_expression("scroll to top", recognized_speech)
            elif match_any_expression(["reset changes", "clear edits"], recognized_speech) != None: # destructive modification commands next
                self.queued_modifications.append("clear")
                match = match_any_expression(["reset changes", "clear edits"], recognized_speech)
                self.reset_context()
            elif match_any_expression(["clear everything", "start new"], recognized_speech) != None:
                self.queued_modifications.append("whiteout_all")
                match = match_any_expression(["clear everything", "start new"], recognized_speech)
                self.reset_context()
            elif match_any_expression(["remove navbar"], recognized_speech) != None:
                number = 1
                match = match_any_expression(["remove navbar"], recognized_speech)
                for variable in match[1]:
                    if isinstance(variable, int):
                        number = variable
                        break
                self.reset_context()
                self.queued_modifications.append("remove_navbar "+str(number))
            elif match_any_expression(["delete footer"], recognized_speech) != None:
                self.queued_modifications.append("remove_footer")
                match = match_any_expression(["delete footer"], recognized_speech)
                self.reset_context()
            elif match_any_expression(["delete logo (text,round) background", "logo (text,round) background off"], recognized_speech) != None:
                self.queued_modifications.append("remove_logo_bg")
                match = match_any_expression(["delete logo (text,round) background", "logo (text,round) background off"], recognized_speech)
                self.context["object"] = "logo text background"
            elif match_any_expression(["delete logo"], recognized_speech) != None:
                self.queued_modifications.append("remove_logo")
                match = match_any_expression(["delete logo"], recognized_speech)
                self.reset_context()
            elif match_any_expression(["restore logo (text,round) background", "logo (text,round) background on"], recognized_speech) != None:
                self.queued_modifications.append("restore_logo_bg")
                match = match_any_expression(["restore logo (text,round) background", "logo (text,round) background on"], recognized_speech)
                self.context["object"] = "logo text background"
            elif match_any_expression(["footer background match logo background"], recognized_speech) != None: # constructive modification commands last
                match = match_any_expression(["footer background match logo background"], recognized_speech)
                self.context["object"] = "footer"

                footer_ref = self.get_current_page().get_component("footer")
                logo_ref = self.get_current_page().get_component("logo")
                if footer_ref != None and logo_ref != None:
                    colors_string = ""
                    if len(logo_ref[0].metadata["background-colors"]) > 0:
                        for i in range(len(logo_ref[0].metadata["background-colors"])):
                            colors_string += logo_ref[0].metadata["background-colors"][i].strip("\n")
                            if i < len(logo_ref[0].metadata["background-colors"])-1:
                                colors_string += " "
                    else:
                        colors_string = "#ffffff"
                    self.queued_modifications.append("footer_match_bg "+colors_string)
            elif match_any_expression(["logo background match footer background"], recognized_speech) != None: # constructive modification commands last
                match = match_any_expression(["logo background match footer background"], recognized_speech)
                self.context["object"] = "logo"

                footer_ref = self.get_current_page().get_component("footer")
                logo_ref = self.get_current_page().get_component("logo")
                if footer_ref != None and logo_ref != None:
                    colors_string = ""
                    if len(footer_ref[0].metadata["background-colors"]) > 0:
                        for i in range(len(footer_ref[0].metadata["background-colors"])):
                            colors_string += footer_ref[0].metadata["background-colors"][i].strip("\n")
                            if i < len(footer_ref[0].metadata["background-colors"])-1:
                                colors_string += " "
                    else:
                        colors_string = "#ffffff"
                    self.queued_modifications.append("logo_match_bg "+colors_string)
            elif match_any_expression(["(make,set) (logo,title) (text,round) background"], recognized_speech) != None and len(match_any_expression(["(make,set) (logo,title) (text,round) background"], recognized_speech)[1]) > 0:
                match = match_any_expression(["(make,set) (logo,title) (text,round) background"], recognized_speech)
                self.context["object"] = "logo text background"
                color = None
                color_needs_merge = (len(match[1]) > 0 and "colorneedsmerge" in match[1])
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("logo")
                    if ref != None and "rounded-color" in ref[0].metadata:
                        color = merge_colors_hex(color, ref[0].metadata["rounded-color"])
                if color != None:
                    self.queued_modifications.append("title_text_bg_to "+color)
            elif match_any_expression(["(make,set) (logo,title) background"], recognized_speech) != None and len(match_any_expression(["(make,set) (logo,title) background"], recognized_speech)[1]) > 0:
                match = match_any_expression(["(make,set) (logo,title) background"], recognized_speech)
                self.context["object"] = "logo background"
                color = None
                direction = None
                color_needs_merge = False
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                    if direction == None and len(variable) > 1 and variable in synonyms_dict["left"]: # indicates a left direction
                        direction = "left"
                    if direction == None and len(variable) > 1 and variable in synonyms_dict["right"]: # indicates a right direction
                        direction = "right"
                    if variable == "colorneedsmerge":
                        color_needs_merge = True

                if color != None:
                    # merges color with reference if possible & necessary
                    ref = self.get_current_page().get_component("logo")
                    if color_needs_merge == True and ref != None:
                        if direction == "left":
                            color = merge_colors_hex(color, ref[0].metadata["background-colors"][0])
                        elif direction == "right":
                            if len(ref[0].metadata["background-colors"]) > 1:
                                color = merge_colors_hex(color, ref[0].metadata["background-colors"][1])
                            else:
                                color = merge_colors_hex(color, ref[0].metadata["background-colors"][0])
                        else:
                            color = merge_colors_hex(color, ref[0].metadata["background-colors"][0])

                    # sets new color
                    if direction != None:
                        self.queued_modifications.append("title_bg_"+direction+"_to "+color)
                    else:
                        self.queued_modifications.append("title_bg_to "+color)
            elif match_expression("(make,set) title color", recognized_speech) != None and len(match_expression("(make,set) title color", recognized_speech)[1]) > 0:
                match = match_expression("(make,set) title color", recognized_speech)
                self.context["object"] = "title"
                color = None
                color_needs_merge = (len(match[1]) > 0 and "colorneedsmerge" in match[1])
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("logo")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("title_color_to "+color)
            elif match_expression("(make,set) title (to,say)", recognized_speech) != None and len(match_expression("(make,set) title (to,say)", recognized_speech)[1]) > 0:
                match = match_expression("(make,set) title (to,say)", recognized_speech)
                self.context["object"] = "title"
                title = match[1][0].title()
                self.queued_modifications.append("title_to "+title)
            elif match_expression("(make,set) title", recognized_speech) != None and len(match_expression("(make,set) title", recognized_speech)[1]) > 0:
                match = match_expression("(make,set) title", recognized_speech)
                self.context["object"] = "title"
                color = None
                color_needs_merge = (len(match[1]) > 0 and "colorneedsmerge" in match[1])
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("logo")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("title_color_to "+color)
            elif match_any_expression(["add logo"], recognized_speech) != None:
                self.queued_modifications.append("add_logo")
                match = match_any_expression(["add logo"], recognized_speech)
                self.context["object"] = "title"
            elif match_any_expression(["add navbar"], recognized_speech) != None:
                match = match_any_expression(["add navbar"], recognized_speech)
                current_page = self.get_current_page()

                index = 1
                proposition = None
                for variable in match[1]:
                    if isinstance(variable, int):
                        # looks up index of numberth navbar
                        number = variable
                        ref = current_page.get_component("navbar", number)
                        if ref != None:
                            index = ref[1]
                    if proposition == None and (variable in synonyms_dict["above"] or variable in synonyms_dict["before"]):
                        proposition = "above"
                    elif proposition == None and (variable in synonyms_dict["below"] or variable in synonyms_dict["after"]):
                        proposition = "below"
                if proposition == "below" and len(current_page.sections) > index and isinstance(current_page.sections[index], NavBar):
                    index += 1
                self.queued_modifications.append("add_navbar "+str(index))
                self.context["object"] = "navbar "+str(index)
            elif match_any_expression(["add footer"], recognized_speech) != None:
                self.queued_modifications.append("add_footer")
                match = match_any_expression(["add footer"], recognized_speech)
                self.context["object"] = "footer"
            elif match_any_expression(["(make,set) footer background"], recognized_speech) != None and len(match_any_expression(["(make,set) footer background"], recognized_speech)[1]) > 0:
                match = match_any_expression(["(make,set) footer background"], recognized_speech)
                self.context["object"] = "footer background"
                color = None
                direction = None
                color_needs_merge = False
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                    if direction == None and len(variable) > 1 and variable in synonyms_dict["left"]: # indicates a left direction
                        direction = "left"
                    if direction == None and len(variable) > 1 and variable in synonyms_dict["right"]: # indicates a right direction
                        direction = "right"
                    if variable == "colorneedsmerge":
                        color_needs_merge = True

                if color != None:
                    # merges color with reference if possible & necessary
                    ref = self.get_current_page().get_component("footer")
                    if color_needs_merge == True and ref != None:
                        if direction == "left":
                            color = merge_colors_hex(color, ref[0].metadata["background-colors"][0])
                        elif direction == "right":
                            if len(ref[0].metadata["background-colors"]) > 1:
                                color = merge_colors_hex(color, ref[0].metadata["background-colors"][1])
                            else:
                                color = merge_colors_hex(color, ref[0].metadata["background-colors"][0])
                        else:
                            color = merge_colors_hex(color, ref[0].metadata["background-colors"][0])

                    # sets new color
                    if direction != None:
                        self.queued_modifications.append("footer_bg_"+direction+"_to "+color)
                    else:
                        self.queued_modifications.append("footer_bg_to "+color)
            elif match_expression("(make,set) footer color", recognized_speech) != None and len(match_expression("(make,set) footer color", recognized_speech)[1]) > 0:
                match = match_expression("(make,set) footer color", recognized_speech)
                self.context["object"] = "footer"
                color = None
                color_needs_merge = (len(match[1]) > 0 and "colorneedsmerge" in match[1])
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("footer")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("footer_color_to "+color)
            elif match_expression("(make,set) footer (to,say)", recognized_speech) != None and len(match_expression("(make,set) footer (to,say)", recognized_speech)[1]) > 0:
                match = match_expression("(make,set) footer (to,say)", recognized_speech)
                self.context["object"] = "footer"
                title = match[1][0].title()
                self.queued_modifications.append("footer_to "+title)
            elif match_expression("(make,set) footer", recognized_speech) != None and len(match_expression("(make,set) footer", recognized_speech)[1]) > 0:
                match = match_expression("(make,set) footer", recognized_speech)
                self.context["object"] = "footer"
                color = None
                color_needs_merge = (len(match[1]) > 0 and "colorneedsmerge" in match[1])
                for variable in match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("footer")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("footer_color_to "+color)

            # processes additional commands
            recognized_speech = None
            if match != None:
                print("Speech interpretation: "+str(match))
                if match[2] != None:
                    recognized_speech = match[2]

    def process_audio(self, recognizer, audio):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            recognized_speech = recognizer.recognize_google(audio)
            self.process_statement(recognized_speech)

        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            pass
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))

    def console_prompt(self):
        while True:
            time.sleep(1.25)
            typed_speech = input("\nWhat would you like SwiftPage to do? ")
            self.process_statement(typed_speech)

    def start(self):
        print("Speech control addon started")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        if self.console_mode == False:
            # starts listening in the background
            self.stop_listening = self.recognizer.listen_in_background(self.microphone, self.process_audio)
        else:
            t1 = threading.Thread(target=self.console_prompt)
            t1.start()
        
    def stop(self):
        print("Speech control addon stopped")
        if self.stop_listening != None: self.stop_listening()

