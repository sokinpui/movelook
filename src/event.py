class Event:

    event_id = 0

    def __init__(self, description : str):
        Event.event_id += 1
        self.id = Event.event_id
        self.description = description
        self.related_files = []


    def to_dict(self) -> dict:
        return self.__dict__

def main():
    pass


if __name__ == "__main__":
    main()

