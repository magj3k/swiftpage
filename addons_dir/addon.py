

class Addon(object): # can be subclassed to create custom addons
    def __init__(self, page):
        self.page = page
        self.queued_modifications = []
        self.server_commands = []

    def start(self):
        print("Addon started")

    def stop(self):
        print("Addon stopped")

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

    def get_server_commands(self):
        commands = self.server_commands[:]
        self.server_commands = []
        return commands
