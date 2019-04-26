from addons_dir.addon import *
from addons_dir.speech_helper import *
import speech_recognition as sr # also implicity requires pyaudio

class SpeechControlAddon(Addon):
    def __init__(self, page):
        Addon.__init__(self, page)

        self.recognizer = None
        self.microphone = None
        self.stop_listening = None

        self.context = {
            "variables": [],
            "object": None,
            "description": None,
        }

    def process_audio(self, recognizer, audio):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            recognized_speech = recognizer.recognize_google(audio)
            while recognized_speech != None:
                matches = []
                print("Speech: " + recognized_speech)

                # server commands first
                match = match_expression("refresh", recognized_speech)
                if match != None:
                    self.server_commands.append("refresh")
                    matches.append(match[:])

                match = match_expression("scroll to bottom", recognized_speech)
                if match != None:
                    self.server_commands.append("scroll_to_bottom")
                    matches.append(match[:])

                match = match_expression("scroll to top", recognized_speech)
                if match != None:
                    self.server_commands.append("scroll_to_top")
                    matches.append(match[:])

                # destructive modification commands next
                match = match_any_expression(["reset changes", "clear everything", "start again"], recognized_speech)
                if match != None:
                    self.queued_modifications.append("clear")
                    matches.append(match[:])

                match = match_any_expression(["delete logo text background", "logo text background off"], recognized_speech)
                if match != None:
                    self.queued_modifications.append("remove_logo_bg")
                    matches.append(match[:])

                match = match_any_expression(["restore logo (text,round) background", "logo (text,round) background on"], recognized_speech)
                if match != None:
                    self.queued_modifications.append("restore_logo_bg")
                    matches.append(match[:])

                # constructive modification commands last
                match_bg = match_any_expression(["(make,set) (logo,title) background"], recognized_speech)
                if match_bg != None and len(match_bg[1]) > 0:
                    for variable in match_bg[1]:
                        if len(variable) > 1 and variable[0] == "#": # indicates a color
                            self.queued_modifications.append("title_bg_to "+variable)
                            matches.append(match_bg[:])
                            break

                match = match_any_expression(["(make,set) (logo,title) (text,round) background"], recognized_speech)
                if match != None and len(match[1]) > 0:
                    for variable in match[1]:
                        if len(variable) > 1 and variable[0] == "#": # indicates a color
                            self.queued_modifications.append("title_text_bg_to "+variable)
                            matches.append(match[:])
                            break

                match = match_expression("set title (to,say)", recognized_speech)
                match_color_a = match_expression("(make,set) title", recognized_speech)
                match_color_b = match_expression("(make,set) title color", recognized_speech)
                if match_color_b != None and len(match_color_b[1]) > 0:
                    for variable in match_color_b[1]:
                        if len(variable) > 1 and variable[0] == "#": # indicates a color
                            self.queued_modifications.append("title_color_to "+variable)
                            matches.append(match_color_b[:])
                            break
                elif match != None and len(match[1]) > 0:
                    title = match[1][0].title()
                    self.queued_modifications.append("title_to "+title)
                    matches.append(match[:])
                elif match_bg == None and match_color_a != None and len(match_color_a[1]) > 0:
                    for variable in match_color_a[1]:
                        if len(variable) > 1 and variable[0] == "#": # indicates a color
                            self.queued_modifications.append("title_color_to "+variable)
                            matches.append(match_color_a[:])
                            break

                # processes additional commands
                recognized_speech = None
                for match in matches:
                    print("Speech interpretation: "+str(match))
                    if match[2] != None:
                        recognized_speech = match[2]
                        break

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

