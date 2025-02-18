class Event:
    cls_id = 0


    def __init__(self, description : str ):
        self.id = Event.cls_id
        Event.cls_id += 1

        self.description = description

class EventList:
    def __init__(self):
        self.events = []

    def add_event(self, event : Event):
        self.events.append(event)

    def get_event(self, id : int):
        for event in self.events:
            if event.id == id:
                return event
        return None

    def get_all_events(self):
        return self.events
