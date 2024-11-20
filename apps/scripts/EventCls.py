class Event:
    def __init__(self):
        self.listeners = []

    def subscribe(self, listener):
        if listener not in self.listeners:
            self.listeners.append(listener)

    def unsubscribe(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def notify(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)