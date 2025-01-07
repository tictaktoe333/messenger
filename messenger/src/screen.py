import os


class Screen:
    def __init__(self):
        self.message = []
        self.command = ""

    def add_message(self, item):
        self.message.append(item)

    def add_command(self, item):
        self.command = item

    def remove_message(self, item):
        if item in self.message:
            self.message.remove(item)

    def get_message(self):
        return self.message.pop()

    def is_empty(self):
        return self.message == [] and self.command == ""

    def reset(self):
        self.message = []
        self.command = ""

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_all(self):
        for item in self.message:
            print(item)
        if self.command:
            print(self.command)
