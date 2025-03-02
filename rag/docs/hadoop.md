# Document: Introduction to Hadoop and Log Analysis System

## 1. Introduction to Hadoop
Hadoop is an open-source big data processing framework developed by the Apache Software Foundation (https://hadoop.apache.org). It is designed to handle the distributed processing of large datasets across clusters of computers using simple programming models. Hadoop's architecture is built on two core components:
- **Hadoop Distributed File System (HDFS):** A distributed file system that provides high-throughput access to application data.
- **MapReduce:** A programming model and processing engine for distributed computation.

## 2. System Overview
The logs analyzed in this system are generated from a Hadoop cluster consisting of five machines, each equipped with an Intel(R) Core(TM) i7-3770 CPU and 16GB of RAM. The cluster collectively provides 46 cores for distributed processing. Two testing applications were executed on this cluster to generate logs:
1. **WordCount:** A standard MapReduce example included with Hadoop. It processes input files and counts the occurrences of each word.
2. **PageRank:** A MapReduce-based algorithm commonly used by search engines to rank web pages based on their link structure.

## 3. Log Collection and Structure
The logs are organized in a hierarchical directory structure typical of Hadoop’s logging system. Each log file corresponds to a container, which is a unit of execution in Hadoop’s YARN (Yet Another Resource Negotiator) framework. The structure follows this pattern:

```
hadoop/
  application_<application_id>/
    container_<application_id>_<attempt_id>_<container_id>.log
```

### Key Components of the Log File Names:
- **application_<application_id>:** A unique identifier for each application run (e.g., `application_1445087491445_0005`).
- **container_<application_id>_<attempt_id>_<container_id>:** Identifies the specific container tasked with executing a portion of the application. For example:
  - `container_1445087491445_0005_01_000007.log` indicates container `000007` of the first attempt (`01`) of application `1445087491445_0005`.

### Collected Logs:
The dataset includes logs from multiple application runs, such as:
- `application_1445087491445_0005` with containers like `container_1445087491445_0005_01_000007.log`.
- `application_1445062781478_0018` with containers like `container_1445062781478_0018_02_000001.log`.
- And many more, spanning various application IDs and container instances.

In total, the dataset comprises logs from over 50 distinct application runs, with hundreds of container logs capturing the execution details of WordCount and PageRank under different conditions.

## 5. Contents of the Logs
Hadoop logs typically include the following types of information:
- **Timestamps:** When events occurred during execution.
- **Log Levels:** Debug, Info, Warn, Error, or Fatal messages indicating the severity of events.
- **Task Execution Details:** Information about MapReduce tasks, such as task start/stop times, input/output data sizes, and task status (success or failure).
- **Error Messages:** Details about exceptions, failures, or resource issues (e.g., disk full errors, network timeouts).
- **System Metrics:** CPU usage, memory consumption, and network activity logged by YARN and HDFS components.

For example, logs from a "machine down" scenario might include entries indicating a lost node, task reassignment, or job failure, while "disk full" logs might show I/O exceptions or task aborts.

## some sampled line from the log
```
2015-10-18 18:06:40,108 INFO [RMCommunicator Allocator] org.apache.hadoop.ipc.Client: Retrying connect to server: msra-sa-41:8030. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=10, sleepTime=1000 MILLISECONDS)
2015-10-18 18:08:07,504 WARN [LeaseRenewer:msrabi@msra-sa-41:9000] org.apache.hadoop.ipc.Client: Address change detected. Old: msra-sa-41/10.190.173.170:9000 New: msra-sa-41:9000
2015-10-18 18:10:04,855 WARN [LeaseRenewer:msrabi@msra-sa-41:9000] org.apache.hadoop.ipc.Client: Address change detected. Old: msra-sa-41/10.190.173.170:9000 New: msra-sa-41:9000
2015-10-18 18:04:05,127 INFO [AsyncDispatcher event handler] org.apache.hadoop.mapreduce.v2.app.speculate.DefaultSpeculator: ATTEMPT_START task_1445144423722_0020_m_000007
2015-10-18 18:10:27,544 WARN [RMCommunicator Allocator] org.apache.hadoop.ipc.Client: Address change detected. Old: msra-sa-41/10.190.173.170:8030 New: msra-sa-41:8030
2015-10-18 18:03:55,939 INFO [AsyncDispatcher event handler] org.apache.hadoop.mapreduce.v2.app.speculate.DefaultSpeculator: ATTEMPT_START task_1445144423722_0020_m_000005
2015-10-18 18:07:50,238 ERROR [RMCommunicator Allocator] org.apache.hadoop.mapreduce.v2.app.rm.RMContainerAllocator: ERROR IN CONTACTING RM.
2015-10-18 18:06:22,045 WARN [LeaseRenewer:msrabi@msra-sa-41:9000] org.apache.hadoop.ipc.Client: Address change detected. Old: msra-sa-41/10.190.173.170:9000 New: msra-sa-41:9000
2015-10-18 18:07:06,219 WARN [LeaseRenewer:msrabi@msra-sa-41:9000] org.apache.hadoop.hdfs.LeaseRenewer: Failed to renew lease for [DFSClient_NONMAPREDUCE_1537864556_1] for 128 seconds.  Will retry shortly ...
2015-10-18 18:06:44,156 WARN [LeaseRenewer:msrabi@msra-sa-41:9000] org.apache.hadoop.hdfs.LeaseRenewer: Failed to renew lease for [DFSClient_NONMAPREDUCE_1537864556_1] for 106 seconds.  Will retry shortly ...
```
