from addon import *

class SpeechControlAddon(Addon):
    def __init__(self, page, modifier = None):
        Addon.__init__(self, page)
        self.modifier = modifier

    def start(self):
        print("Speech control addon started")