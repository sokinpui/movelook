# System Documentation

## Overview

This document provides a comprehensive overview of the logging and data processing system designed for managing logs with Elasticsearch. The system consists of multiple components, each responsible for specific tasks, including log collection, pattern extraction, action handling, data cleaning, and configuration management.

## Components

### 1. Configuration Checker (`config_checker.py`)

This module validates the configuration file for the system. It checks for required keys and validates the naming conventions for patterns defined in the configuration.

**Key Functions:**
- `validate_name(name)`: Validates the name according to specified criteria (length, characters, prefixes).
- `validate_config(config)`: Checks the integrity and completeness of the configuration.
- `config_checker()`: Loads and validates the YAML configuration file.

### 2. Timer (`timer.py`)

This utility module provides a timer class to facilitate repetitive tasks at specified intervals.

**Key Functions:**
- `Timer`: Class that manages the scheduling of functions to be executed at regular intervals.
- `set_function(function, *args, **kwargs)`: Assigns a function to be run by the timer.
- `start()`: Starts the timer.
- `stop()`: Stops the timer.

### 3. Elasticsearch Startup (`start_elasticsearch.py`)

This module handles the startup of an Elasticsearch instance using Singularity.

**Key Functions:**
- `start_elasticsearch()`: Initiates the Elasticsearch container and checks if it's running.

### 4. Action Handler (`action_handler.py`)

This module manages actions based on logs collected from Elasticsearch. It queries the logs and performs actions based on predefined patterns.

**Key Functions:**
- `check_messages()`: Queries Elasticsearch for messages and processes them.
- `handle_action(message)`: Executes specific actions based on the message content.

### 5. Data Cleaner (`data_cleaner.py`)

This module manages the cleanup of old logs from Elasticsearch.

**Key Functions:**
- `BufferManager`: Class that manages the movement of data between indices.
- `move_data(source, dest)`: Moves data older than a retention period from one index to another.

### 6. Pattern Extractor (`pattern_extractor.py`)

This module extracts patterns from logs based on defined regex expressions.

**Key Functions:**
- `Extractor`: Class that periodically searches for defined regex patterns in logs.
- `regex_search()`: Searches logs for defined patterns and stores results in separate indices.

### 7. Elasticsearch Client (`es_client.py`)

This module manages the connection to the Elasticsearch instance as a singleton.

**Key Functions:**
- `get_instance()`: Returns the single instance of the Elasticsearch client.

### 8. Log Collector (`log_collector.py`)

This module collects logs from specified directories and inserts them into Elasticsearch.

**Key Functions:**
- `Collector`: Class that reads logs from files and sends them to Elasticsearch.
- `process()`: Reads log files, processes new lines, and updates markers.

### 9. Main Script (`main.py`)

This is the entry point of the system, coordinating the startup of all components.

**Key Functions:**
- Initializes and starts timers for each component.
- Calls configuration checker and Elasticsearch startup functions.

## Configuration File

The configuration file is a YAML file located at `$HOME/.config/ml/config.yml`. It should contain the following sections:

- **database**: Configuration details for database connectivity.
- **collector**: Settings for the log collector, including the directory to scan.
- **patterns**: Regex patterns to extract from logs.
- **actions**: Actions to be performed based on log messages.
- **cleaner**: Settings for data retention and cleanup.
- **extractor**: Settings for the pattern extractor.

### Example Configuration

```yaml
database:
  host:
    scheme: "http"
    host: "localhost"
    port: 9200
collector:
  directory: "/path/to/logs"
patterns:
  regex:
    - name: "error_pattern"
      pattern: "ERROR .*"
      action: "log_warning"
actions:
  - action: "log_warning"
cleaner:
  interval: 30
  index: "buffer_index"
extractor:
  interval: 60
```

## Running the System

1. Ensure that Elasticsearch is installed and accessible.
2. Configure the `config.yml` file with appropriate settings.
3. Run the main script:
   ```bash
   python main.py
   ```

## Logging

Logging is configured to record system activities. The log level can be adjusted in the `action_handler.py` module.

## Dependencies

- Python 3.x
- `elasticsearch` Python package
- `PyYAML` for YAML parsing

## Conclusion

This system efficiently collects, processes, and manages logs using Elasticsearch. Each component is modular, allowing for easy updates and maintenance. Ensure to validate configurations and monitor the system’s performance regularly.
