Specification for collected data in database, this spec should apply for all databases.

# text data source
- utf8 encded text data source
- store as text file

## data structure in database
- `line number`
- `line content`
- `lenght of line`
- `timestamp`: use datetime object for calculation ease
- `path`: relative path(relative to the root directory that contain all the file source) to the file
