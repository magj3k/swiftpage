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
        self.current_match = None
        self.previously_unmatched_phrase = ""

    def get_current_page(self):
        return self.modifier.generate()

    def reset_context(self):
        self.context = {
            "variables": [],
            "object": None,
            "description": None,
            "color": None,
        }

    def process_match(self, target_phrases, recognized_speech, min_required_variables=0):
        if self.current_match == None:
            self.current_match = match_any_expression(target_phrases, recognized_speech, min_required_variables)
            return self.current_match != None
        return False

    def process_statement(self, recognized_speech):
        iteration = 0
        while recognized_speech != None:
            self.current_match = None
            recognized_speech = extract_context(recognized_speech, self.context)
            print("Speech: " + recognized_speech)

            # all supported phrases and their corresponding actions

            # server commands first
            if self.process_match(["refresh"], recognized_speech):
               self.server_commands.append("refresh")
               
            if self.process_match(["scroll to bottom"], recognized_speech):
                self.server_commands.append("scroll_to_bottom")

            if self.process_match(["scroll to top"], recognized_speech):
                self.server_commands.append("scroll_to_top")

            # destructive modification commands next
            if self.process_match(["reset changes", "clear edits"], recognized_speech):
                self.queued_modifications.append("clear")
                self.reset_context()

            if self.process_match(["clear everything", "start new"], recognized_speech):
                self.queued_modifications.append("whiteout_all")
                self.reset_context()

            if self.process_match(["remove navbar"], recognized_speech):
                number = 1
                for variable in self.current_match[1]:
                    if isinstance(variable, int):
                        number = variable
                        break
                self.reset_context()
                self.queued_modifications.append("remove_navbar "+str(number))

            if self.process_match(["remove section"], recognized_speech):
                number = 1 # TODO, correct number
                for variable in self.current_match[1]:
                    if isinstance(variable, int):
                        number = variable
                        break
                self.reset_context()
                self.queued_modifications.append("remove_section "+str(number))

            if self.process_match(["delete footer"], recognized_speech):
                self.queued_modifications.append("remove_footer")
                self.reset_context()

            if self.process_match(["delete logo (text,round) background", "logo (text,round) background off"], recognized_speech):
                self.queued_modifications.append("remove_logo_bg")
                self.context["object"] = "logo text background"

            if self.process_match(["delete logo"], recognized_speech):
                self.queued_modifications.append("remove_logo")
                self.reset_context()

            if self.process_match(["restore logo (text,round) background", "logo (text,round) background on"], recognized_speech):
                self.queued_modifications.append("restore_logo_bg")
                self.context["object"] = "logo text background"

            if self.process_match(["footer background match logo background"], recognized_speech):
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

            if self.process_match(["logo background match footer background"], recognized_speech):
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

            if self.process_match(["(make,set) (logo,title) (text,round) background"], recognized_speech, 1):
                self.context["object"] = "logo text background"
                color = None
                color_needs_merge = (len(self.current_match[1]) > 0 and "colorneedsmerge" in self.current_match[1])
                for variable in self.current_match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("logo")
                    if ref != None and "rounded-color" in ref[0].metadata:
                        color = merge_colors_hex(color, ref[0].metadata["rounded-color"])
                if color != None:
                    self.queued_modifications.append("title_text_bg_to "+color)

            if self.process_match(["(make,set) (logo,title) background"], recognized_speech, 1):
                self.context["object"] = "logo background"
                color = None
                direction = None
                color_needs_merge = False
                for variable in self.current_match[1]:
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

            if self.process_match(["(make,set) title color"], recognized_speech, 1):
                self.context["object"] = "title"
                color = None
                color_needs_merge = (len(self.current_match[1]) > 0 and "colorneedsmerge" in self.current_match[1])
                for variable in self.current_match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("logo")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("title_color_to "+color)

            if self.process_match(["(make,set) title (to,say)"], recognized_speech, 1):
                self.context["object"] = "title"
                title = self.current_match[1][0].title()
                self.queued_modifications.append("title_to "+title)

            if self.process_match(["(make,set) title"], recognized_speech, 1):
                self.context["object"] = "title"
                color = None
                color_needs_merge = (len(self.current_match[1]) > 0 and "colorneedsmerge" in self.current_match[1])
                for variable in self.current_match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("logo")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("title_color_to "+color)

            if self.process_match(["add logo"], recognized_speech):
                self.queued_modifications.append("add_logo")
                self.context["object"] = "title"

            if self.process_match(["add navbar"], recognized_speech, 1):
                current_page = self.get_current_page()
                index = 1
                proposition = None
                for variable in self.current_match[1]:
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

            if self.process_match(["add section"], recognized_speech):
                current_page = self.get_current_page()
                index = len(current_page.sections)-1 # TODO, correct number
                proposition = None
                for variable in self.current_match[1]:
                    if isinstance(variable, int):
                        # looks up index of numberth navbar
                        number = variable
                        ref = current_page.get_component("section", number)
                        if ref != None:
                            index = ref[1]
                    if proposition == None and (variable in synonyms_dict["above"] or variable in synonyms_dict["before"]):
                        proposition = "above"
                    elif proposition == None and (variable in synonyms_dict["below"] or variable in synonyms_dict["after"]):
                        proposition = "below"
                if proposition == "below" and len(current_page.sections) > index and isinstance(current_page.sections[index], Section):
                    index += 1
                self.queued_modifications.append("add_section "+str(index))
                self.context["object"] = "section "+str(index)

            if self.process_match(["add footer"], recognized_speech):
                self.queued_modifications.append("add_footer")
                self.context["object"] = "footer"

            if self.process_match(["(make,set) footer background"], recognized_speech, 1):
                self.context["object"] = "footer background"
                color = None
                direction = None
                color_needs_merge = False
                for variable in self.current_match[1]:
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

            if self.process_match(["(make,set) footer color"], recognized_speech, 1):
                self.context["object"] = "footer"
                color = None
                color_needs_merge = (len(self.current_match[1]) > 0 and "colorneedsmerge" in self.current_match[1])
                for variable in self.current_match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("footer")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("footer_color_to "+color)

            if self.process_match(["(make,set) footer (to,say)"], recognized_speech, 1):
                self.context["object"] = "footer"
                title = self.current_match[1][0].title()
                self.queued_modifications.append("footer_to "+title)

            if self.process_match(["(make,set) footer"], recognized_speech, 1):
                self.context["object"] = "footer"
                color = None
                color_needs_merge = (len(self.current_match[1]) > 0 and "colorneedsmerge" in self.current_match[1])
                for variable in self.current_match[1]:
                    if color == None and len(variable) > 1 and variable[0] == "#": # indicates a color
                        color = variable
                        break

                if color_needs_merge == True:
                    ref = self.get_current_page().get_component("footer")
                    if ref != None:
                        color = merge_colors_hex(color, ref[0].metadata["text-color"])
                if color != None:
                    self.queued_modifications.append("footer_color_to "+color)

            if self.process_match(["reset footer"], recognized_speech):
                self.queued_modifications.append("reset_footer")
                self.context["object"] = "footer"

            # processes additional commands
            if self.current_match != None:
                print("Speech interpretation: "+str(self.current_match))
                recognized_speech = None
                self.previously_unmatched_phrase = ""
                if self.current_match[2] != None:
                    recognized_speech = self.current_match[2]
            else:
                if self.previously_unmatched_phrase != "" and iteration <= 2:
                    recognized_speech = self.previously_unmatched_phrase + " " + recognized_speech
                else:
                    self.previously_unmatched_phrase = recognized_speech
                    if self.previously_unmatched_phrase == None: self.previously_unmatched_phrase = ""
                    recognized_speech = None

            iteration += 1

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

