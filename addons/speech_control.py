import sys
sys.path.append('./addons')
from addon import *
from speech_helper import *
import speech_recognition as sr # also implicity requires pyaudio

class SpeechControlAddon(Addon):
    def __init__(self, page, modifier = None):
        Addon.__init__(self, page)
        self.modifier = modifier

        self.recognizer = None
        self.microphone = None
        self.stop_listening = None

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

    def process_audio(self, recognizer, audio):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            recognized_speech = recognizer.recognize_google(audio)
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
                elif match_any_expression(["delete logo"], recognized_speech) != None:
                    self.queued_modifications.append("remove_logo")
                    match = match_any_expression(["delete logo"], recognized_speech)
                    self.reset_context()
                elif match_any_expression(["remove navbar"], recognized_speech) != None:
                    number = 1
                    for variable in match[1]:
                        if isinstance(variable, int):
                            number = variable
                            break
                    match = match_any_expression(["remove navbar"], recognized_speech)
                    self.reset_context()
                    self.queued_modifications.append("remove_navbar "+str(number))
                elif match_any_expression(["delete logo (text,round) background", "logo (text,round) background off"], recognized_speech) != None:
                    self.queued_modifications.append("remove_logo_bg")
                    match = match_any_expression(["delete logo (text,round) background", "logo (text,round) background off"], recognized_speech)
                    self.context["object"] = "logo text background"
                elif match_any_expression(["restore logo (text,round) background", "logo (text,round) background on"], recognized_speech) != None:
                    self.queued_modifications.append("restore_logo_bg")
                    match = match_any_expression(["restore logo (text,round) background", "logo (text,round) background on"], recognized_speech)
                    self.context["object"] = "logo text background"
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
                elif match_any_expression(["(make,set) (logo,title) background"], recognized_speech) != None and len(match_any_expression(["(make,set) (logo,title) background"], recognized_speech)[1]) > 0: # constructive modification commands last
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
                    self.context["object"] = "text"
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

                    index = 1
                    # TODO: modify index based on propositions
                    self.queued_modifications.append("add_navbar "+str(index))
                    self.context["object"] = "title "+str(index)

                # processes additional commands
                recognized_speech = None
                if match != None:
                    print("Speech interpretation: "+str(match))
                    if match[2] != None:
                        recognized_speech = match[2]

        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            pass
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))

    def start(self):
        print("Speech control addon started")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # starts listening in the background
        self.stop_listening = self.recognizer.listen_in_background(self.microphone, self.process_audio)
        
    def stop(self):
        print("Speech control addon stopped")
        if self.stop_listening != None: self.stop_listening()
