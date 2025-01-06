class Screen:
    def __init__(self):
        self.q = []

    def add(self, item):
        self.q.append(item)

    def remove(self, item):
        if item in self.q:
            self.q.remove(item)

    def get(self):
        return self.q.pop()

    def is_empty(self):
        return self.q == []

    def reset_buffer(self):
        self.q = []

    def print_all(self):
        while not self.is_empty():
            print(self.q.pop())
