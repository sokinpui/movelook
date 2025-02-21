
class Event:

    event_id = 0

    def __init__(self, event_name : str):
        self.event_name = event_name
        self.description = None
        Event.event_id += 1
        self.id = Event.event_id

    def add_description(self, description : str):
        self.description = description

class EventsList:
    def __init__(self):
        self.events = []

    def add_event(self, event : Event):
        self.events.append(event)

    def get_file(self, event_id : int = -1, event_name: str = "" ) -> Event | None:
        for event in self.events:
            if event.id == event_id or event.event_name == event_name:
                return event

        return None

    def get_all_events(self) -> list[Event]:
        return self.events

