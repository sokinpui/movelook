def interpre_event_prompt(event):
    return  f"""
## Trace this event:
    {event}

    To trace the event , we need to gather some information.

    - what inforamtion that can get from system logs are required to trace the event?
    - what application logs are required to trace the event?
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
    """

