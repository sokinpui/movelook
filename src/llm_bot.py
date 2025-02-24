from pydantic import BaseModel, Field

from llm_model import LLMModel
from logger import Logger
from log_file import LogFile
from database import Database
from event import Event

class LLMBot:
    def __init__(self, model : LLMModel, db : Database):
        self.model = model
        self._logger = Logger()

    def get_related_files_for_events(self,
                                    events : list[Event],
                                    files : list[LogFile],
                                    ) -> list[LogFile] | None:
        """
        Find the relation between the files and the events,
        then save to database
        """

        for event in events:
            for file in files:

                class schema(BaseModel):
                    is_related: bool = Field(description="Whether the file is needed to the event")
                    explanation: str = Field(description="The explanation why the file is needed or not")

                with open("./prompt/check_relation.md", "r") as f:
                    prompt = f.read()

                    prompt.replace("{{event}}", event.name)
                    prompt.replace("{{event_description}}", event.description)

                    prompt.replace("{{file}}", file.name)
                    prompt.replace("{{file_description}}", file.description)

                response = self.model.generate(prompt=prompt, schema=schema)
                explanation = response.explanation

                if response.is_related:
                    file.related_events.append(event)
                    event.related_files.append(file)


    def naming_events(self, events : list[Event]) -> list[Event]:
        """
        Naming the events
        """

        class schema(BaseModel):
            name: str = Field(description="a short name for this event")

        for event in events:
            response = self.model.generate(prompt="give this event a short name in 2 to 3 words" + event.description, schema=schema)
            event.name = response.name

        return events


def main():
    pass


if __name__ == "__main__":
    main()
