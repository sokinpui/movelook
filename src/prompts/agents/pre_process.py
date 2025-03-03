def interpre_event_prompt(event, files):

    # get the unique value only
    applications = set([file.belongs_to for file in files])

    return  f"""
    ## Trace this event:
    {event}

    To trace the event , we need to gather some information.

    - what inforamtion from the logs should be pay attention to trace the event?
    - what are the applications that are related to the event?

    ## application in the system
    {applications}

    ## your task

    you must choose the most relevant information from the logs that can be used to trace the event, and the applications that are related to the event.
    \n
    """


def filter_logs(event, message):
    return f"""
    ## Trace this event:
    {event}

    ## insight from other agents
    {message}

    ## Your Task
    with reference to some system logs sample, you will know the format, structure of the line in the logs. You should learn the general format of the logs instead of focusing the content

    Then, you need to generate some keyword that can be used to filter the logs line that help tracing the event, the filtered lines will be further analysis by another agents

    ## search query
    the databsae is using elasticsearch, and access by python api
    \n
    """

def main():
    from new_collector import NewCollector

    dir = "../../../log"
    collector = NewCollector(dir=dir)
    files = collector.collect_logs(dir)

    event = "The system is down"

    print(interpre_event_prompt(event, files))

if __name__ == "__main__":
    main()

