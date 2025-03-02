## 1. Introduction to OpenStack
OpenStack (https://www.openstack.org) is an open-source cloud operating system designed to manage large pools of compute, storage, and networking resources in a data center. Developed by a global community and maintained by the OpenStack Foundation, it provides a flexible and scalable platform for building private and public clouds. OpenStack is composed of multiple interoperable services, such as:

Nova: Computes resource management for virtual machines.
Neutron: Networking services for connectivity and routing.
Cinder: Block storage management.
Swift: Object storage for unstructured data.

## 2. System Overview
The logs in this dataset were generated on CloudLab, a flexible, scientific infrastructure tailored for cloud computing research. CloudLab provides a testbed for deploying and experimenting with cloud systems like OpenStack under controlled conditions. The dataset includes logs from an OpenStack deployment simulating both normal operations and abnormal scenarios with injected failures.

The logs are divided into three files:

openstack_normal1.log: Logs from a normal operational run.
openstack_normal2.log: Additional logs from a second normal operational run.
openstack_abnormal.log: Logs from runs with injected failures to simulate abnormal conditions.
This combination of normal and abnormal logs enables the study of system behavior under various states, supporting anomaly detection and fault diagnosis.

## 3. Log Collection and Structure
The dataset consists of three log files:

openstack_normal1.log: Captures events from a stable OpenStack deployment without disruptions.
openstack_normal2.log: Provides a second set of logs from normal operations, potentially under different workloads or configurations.
openstack_abnormal.log: Contains logs from runs where failures were deliberately injected.

### Log File Characteristics:
Source: Generated from an OpenStack deployment on CloudLab, though specific hardware details (e.g., number of nodes, CPU, RAM) are not provided here.
Format: OpenStack logs are typically plain text, with each line including a timestamp, log level, service name (e.g., nova, neutron), and message.
Naming Convention: The files are labeled to distinguish normal (normal1, normal2) and abnormal (abnormal) conditions.

## scenarios
The logs reflect two primary conditions:
1. Normal Operations: Represented by openstack_normal1.log and openstack_normal2.log, these logs capture typical OpenStack activities, such as:
Virtual machine creation and deletion.
Network configuration and traffic routing.
Storage volume attachments and data operations. These runs establish a baseline for system performance and behavior.

2. Abnormal Operations with Failure Injection: Represented by openstack_abnormal.log, these logs include data from scenarios where failures were introduced. Possible failure types (inferred from common OpenStack testing practices) might include:
Compute Node Failure: Shutting down a Nova compute node.
Network Disruption: Disconnecting Neutron networking services or simulating packet loss.
Storage Failure: Making Cinder or Swift storage unavailable (e.g., disk full, service crash).

5. Contents of the Logs
OpenStack logs typically contain the following types of information:

Service Identifiers: Names of OpenStack components (e.g., nova-scheduler, neutron-server, cinder-volume).
Timestamps: Date and time of each event (e.g., 2025-03-02 14:30:15.789).
Log Levels: INFO, WARNING, ERROR, or DEBUG, indicating the severity or purpose of the message.
Event Details: Actions like VM provisioning, network port binding, or storage volume mounting.
Errors and Exceptions: Failures such as "Instance failed to spawn," "Network unreachable," or "Volume attachment failed."
