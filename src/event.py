class Event:

    event_id = 0

    def __init__(self, event_name : str):
        self.name = event_name
        self.description = None
        Event.event_id += 1
        self.id = Event.event_id
        self.related_files = []

    def add_description(self, description : str):
        self.description = description

    def to_dict(self) -> dict:
        return self.__dict__

def main():
    event1 = Event("Sample Event")
    events_list = EventsList()
    events_list.add_event(event1)
    events_list.add_event(Event("Another Event"))
    events_list.add_event(Event("Yet Another Event"))
    events_list.add_event(Event("One More Event"))
    events_list.add_event(Event("Last Event"))


    for event in events_list.get_all_events():
        print(event.to_dict())


if __name__ == "__main__":
    main()

