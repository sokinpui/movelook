# Container usage
 the database engine is created inside the container, the data is stored outside the container

## MAC-Docker
we use `colima` as docker host, so `colima` will first be created, and then `docker`.

`colima` should have at least `4GBB` of memory in order to run the `Elasticsearch` smoothly.

# Database naming rule
## log collecting
the log are group by subdirectory, every log under this subdirectory will be collected and store in the same index of name `log_<subdirectory>`

## Data Struct of collected log
- `content`: a line of the log
- `id`: the id of the log
- `line_number`: the line number of the log in the log file
- `name`: the name of the log file
- `timestamp`: the timestamp of the log collected

### Example
```python
{
  "content": [
    "Jan  6 08:29:58 LabSZ sshd[22503]: Did not receive identification string from 185.165.29.69\n"
  ],
  ],
  "id": [
    6
  ],
  "line_number": [
    644779
  ],
  "name": [
    "/Users/mac/work/ml/log/ssh/SSH.log"
  ],
  "timestamp": [
    "2025-03-04T13:46:19.476Z"
  ],
}
```

## Agent
One of the Agent `PreProcessAgent` will filter relvant line of the log and create a virtual copy of the line, which is store in index `pre_process_<event.id>`

event is managed by the `Event` model, which incoming event will given a unique id.
