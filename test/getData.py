import os

class LogProcessor:
    def __init__(self, config_file):
        self.config = self.read_config(config_file)
        self.last_read_lines = {}  # Simulating database for last read lines

    def read_config(self, config_file):
        # Simulating reading from a config file (replace with your logic)
        config = {
        #     "log_files": [
        #         {"name": "system.log", "path": "/var/log/", "parser": "regex"},
        #         # ... add more log file configurations as needed
        #     ]
        }
        return config

    def process_logs(self):
        for log_file_config in self.config.get("log_files", []):
            self.process_log_file(log_file_config)

    def process_log_file(self, log_file_config):
        file_path = os.path.join(log_file_config["path"], log_file_config["name"])

        try:
            with open(file_path, 'r') as log_file:
                last_read_line = self.get_last_read_line(log_file_config["name"])
                lines = log_file.readlines()[last_read_line + 1:]

                # Combine all lines into a single string
                all_lines = "".join(lines)

                if all_lines:  # Only store if there are new lines
                    self.store_log_line(log_file_config["name"], all_lines.strip())
                self.update_last_read_line(log_file_config["name"], len(log_file.readlines()) - 1)

        except FileNotFoundError:
            self.reset_last_read_line(log_file_config["name"])

    def get_last_read_line(self, log_file_name):
        return self.last_read_lines.get(log_file_name, -1)

    def update_last_read_line(self, log_file_name, line_number):
        self.last_read_lines[log_file_name] = line_number
        print(f"Updating last read line for {log_file_name} to {line_number}")

    def reset_last_read_line(self, log_file_name):
        self.last_read_lines[log_file_name] = 0
        print(f"Resetting last read line for {log_file_name}")

    def store_log_line(self, log_file_name, log_line):
        # Simulate database storage
        print(f"Storing log lines from {log_file_name}: {log_line}")

# Example usage:
processor = LogProcessor("log_config.json")
processor.process_logs()
