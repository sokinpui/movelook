# start singularity container with elasticsearch

import subprocess
import os
import time

def start_elasticsearch():
    # Define the path for data storage on the host
    host_data_path = "/path/to/your/data"  # Change this to your desired data directory

    # Ensure the host data directory exists
    os.makedirs(host_data_path, exist_ok=True)

    # Singularity command to run Elasticsearch
    singularity_command = [
        "singularity", "exec",
        "--bind", f"{host_data_path}:/usr/share/elasticsearch/data",  # Bind mount for data
        "elasticsearch.sif"
    ]

    # Start Elasticsearch
    process = subprocess.Popen(singularity_command)

    # Allow some time for Elasticsearch to start
    time.sleep(30)  # Adjust the sleep time as needed

    # Check if Elasticsearch is running
    try:
        response = subprocess.check_output(
            ["curl", "-s", "http://localhost:9200"]
        ).decode('utf-8')
        print("Elasticsearch is running:", response)
    except subprocess.CalledProcessError:
        print("Failed to connect to Elasticsearch.")



# Wait for the user to terminate the process
# try:
#     process.wait()
# except KeyboardInterrupt:
#     print("Stopping Elasticsearch...")
#     process.terminate()
