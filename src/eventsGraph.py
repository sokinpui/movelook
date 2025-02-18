

class EventGraph:
    """
    events and file are nodes in the graph,
    if an event is related to a file, there is an edge between the event and the file,
    which mean the file is required to monitor the event
    """

    def __init__(self):
        self.graph = {}

    def add_event(self, event : str):
        if event not in self.graph:
            self.graph[event] = []

    def add_file(self, event : str, files : list):
        if event in self.graph:
            for file in files:
                if file not in self.graph[event]:
                    self.graph[event].append(file)


