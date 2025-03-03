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

    Please analyze the event from multiple perspectives, such as chronological order, application interactions, potential causes, scope of impact,

    \n
    """


def filter_logs(event, info_for_tracing, apps):
    return f"""
    ## Role
    You are a Log Filter Agent in a multi-agent system tasked with generating Elasticsearch search queries to filter system log lines for further analysis.

    ## Input
    - **Event to Trace**: {event}
    - **Tracing Information**: {info_for_tracing}
    - **Relevant Applications**: {apps}

    ## Task
    1. Analyze the typical structure of system log lines based on common conventions (e.g., timestamp, log level, message, metadata fields like user_id or error_code).
    2. Generate keywords or field-specific terms that can filter log lines related to the event `{event}`.
    4. Ensure the query is broad enough to capture context but specific enough to avoid unrelated noise.

    ## naming conventions in the elasticsearch
    logs are organized in different indices based on the application name. For example, logs for the application `app1` are stored in the index `log_app1`.

    use simple match query to filter the logs based on the event, you should only search the given applications

    ## data structure of the logs store in the elasticsearch
    ```
    {{
        content=line,
        line_number=i,
        name=log.name,
        id=log.id,
        timestamp=datetime.now()
    }}
    ```

    ## template of the search query
    ```
    {{
        "query": {{
            "bool": {{
                "should": [
                    {{ "match": {{ "content": "<pattern1>" }} }},
                    {{ "match": {{ "content": "<pattern2>" }} }},
                    .
                    .
                    .
                    {{ "match": {{ "content": "<patternN>" }} }}
                ]
            }}
        }},
    }}
    ```

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

