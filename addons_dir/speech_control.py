from addons_dir.addon import *

class SpeechControlAddon(Addon):
    def __init__(self, page):
        Addon.__init__(self, page)

    def start(self):
        print("Speech control addon started")