from addons_dir.addon import *
import speech_recognition as sr # also implicity requires pyaudio

# helper functions
def anyWordInString(words, string):
    for word in words:
        if word in string:
            return True
    return False

def allWordsInString(words, string):
    for word in words:
        if word not in string:
            return False
    return True

class SpeechControlAddon(Addon):
    def __init__(self, page):
        Addon.__init__(self, page)

        self.recognizer = None
        self.microphone = None
        self.stop_listening = None

    def process_audio(self, recognizer, audio):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            recognized_speech = recognizer.recognize_google(audio)
            print("Speech: " + recognized_speech)

            if anyWordInString(["reload", "refresh"], recognized_speech) or allWordsInString(["load", "page"], recognized_speech):
                self.server_commands.append("refresh")
            if allWordsInString(["scroll", "to", "bottom"], recognized_speech) or allWordsInString(["go", "to", "bottom"], recognized_speech) or allWordsInString(["go", "to", "end"], recognized_speech) or allWordsInString(["scroll", "to", "end"], recognized_speech):
                self.server_commands.append("scroll_to_bottom")
            if allWordsInString(["scroll", "to", "top"], recognized_speech) or allWordsInString(["go", "to", "top"], recognized_speech) or allWordsInString(["go", "to", "start"], recognized_speech) or allWordsInString(["scroll", "to", "start"], recognized_speech) or allWordsInString(["scroll", "to", "begin"], recognized_speech) or allWordsInString(["go", "to", "begin"], recognized_speech):
                self.server_commands.append("scroll_to_top")

        except sr.UnknownValueError:
            # print("Speech recognition could not understand audio")
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
        self.stop_listening()

