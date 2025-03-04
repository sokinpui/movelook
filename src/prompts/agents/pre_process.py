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


def filter_logs(event, info_for_tracing, apps, sample):
    return f"""
    # Context
    ## Event to Trace:
    {event}

    ## Tracing Information:
    {info_for_tracing}

    ## Relevant Applications:
    {apps}

    ## sample log entries
    {sample}

    # Your Task
    Generate an Elasticsearch boolean query to search the database for log entries related to the provided event.
    The query should help extract relevant lines from logs stored in the Elasticsearch Database.
    The query should include the necessary patterns to trace the event effectively.
    You should generate boolean query in json format that fit into elasticsearch `search` api.
    there are some sample provided above, you should learn the format instead of focus on the content.

    ### rule in Boolean Query
    Boolean query
    A query that matches documents matching boolean combinations of other queries. The bool query maps to Lucene BooleanQuery. It is built using one or more boolean clauses, each clause with a typed occurrence. The occurrence types are:

    - must : The clause (query) must appear in matching documents and will contribute to the score. Each query defined under a must acts as a logical "AND", returning only documents that match all the specified queries.

    - should : The clause (query) should appear in the matching document. Each query defined under a should acts as a logical "OR", returning documents that match any of the specified queries.

    ## Elasticsearch Query Template
    ```json
    {{
      "query": {{
        "bool": {{
          "must": [
            {{ "match": {{ "content": "<pattern1>" }} }},
          ],
          "should": [
            {{ "match": {{ "content": "<pattern1>" }} }},
          ]
        }}
      }}
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

