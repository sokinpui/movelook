class Event:

    event_id = 0

    def __init__(self, event_name : str):
        Event.event_id += 1
        self.id = Event.event_id
        self.name = event_name
        self.description = ""
        self.related_files = []

    def add_description(self, description : str):
        self.description = description

    def to_dict(self) -> dict:
        return self.__dict__

def main():
    pass


if __name__ == "__main__":
    main()

