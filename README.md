a log watching system
this system is separated bythree section

# section 1: log collection
this part will collect the log file and insert them to Elasticsearch database

# section2: scan the collected log for future processing
this part will lookup pattern and store in new index of the same Elasticsearch database

# section3: different module for different purpose of processing
each module(simply a python package) will process according to the data lookup before.
each module inherited from a module class, must implement `run()` and `stop()` method.
each module will wil, define a inherited class `M` in __init__.py
each module should be specified in config.yml, and will load accordingly.
may support individual scan and drop the need of full scan in section2

