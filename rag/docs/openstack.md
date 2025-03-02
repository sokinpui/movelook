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


## some sample line from the log
```
nova-compute.log.1.2017-05-16_13:55:31 2017-05-16 00:09:40.190 2931 INFO nova.virt.libvirt.imagecache [req-addc1839-2ed5-4778-b57e-5854eb7b8b09 - - - - -] image 0673dd71-34c5-4fbb-86c4-40623fbe45b4 at (/var/lib/nova/instances/_base/a489c868f0c37da93b76227c91bb03908ac0e742): in use: on this node 1 local, 0 on other nodes sharing this instance storage
nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:10:39.366 25746 INFO nova.osapi_compute.wsgi.server [req-93ec4346-3e60-4997-8a32-420bab0a390f 113d3a99c3da401fbd62cc2caa5b96d2 54fadb412c4e40cdbaed9335e4c35a9e - - -] 10.11.10.1 "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1" status: 200 len: 1874 time: 0.1886330
nova-compute.log.1.2017-05-16_13:55:31 2017-05-16 00:05:45.547 2931 INFO nova.virt.libvirt.imagecache [req-addc1839-2ed5-4778-b57e-5854eb7b8b09 - - - - -] Active base files: /var/lib/nova/instances/_base/a489c868f0c37da93b76227c91bb03908ac0e742
nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:07:37.513 25746 INFO nova.osapi_compute.wsgi.server [req-0013db4a-a7f2-4013-a135-314a1fbb97e8 113d3a99c3da401fbd62cc2caa5b96d2 54fadb412c4e40cdbaed9335e4c35a9e - - -] 10.11.10.1 "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1" status: 200 len: 1893 time: 0.2449338
nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:14:19.065 25746 INFO nova.osapi_compute.wsgi.server [req-78eed036-ab3e-4482-b5e2-e1e06c5f0951 113d3a99c3da401fbd62cc2caa5b96d2 54fadb412c4e40cdbaed9335e4c35a9e - - -] 10.11.10.1 "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1" status: 200 len: 1583 time: 0.1864619
nova-compute.log.1.2017-05-16_13:55:31 2017-05-16 00:05:50.114 2931 WARNING nova.virt.libvirt.imagecache [req-addc1839-2ed5-4778-b57e-5854eb7b8b09 - - - - -] Unknown base file: /var/lib/nova/instances/_base/a489c868f0c37da93b76227c91bb03908ac0e742
nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:07:11.370 25776 INFO nova.metadata.wsgi.server [-] 10.11.21.132,10.11.10.1 "GET /latest/meta-data/security-groups HTTP/1.1" status: 200 len: 123 time: 0.0007679
nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:14:47.215 25795 INFO nova.metadata.wsgi.server [-] 10.11.21.143,10.11.10.1 "GET /latest/meta-data/block-device-mapping/root HTTP/1.1" status: 200 len: 124 time: 0.0009151
nova-compute.log.1.2017-05-16_13:55:31 2017-05-16 00:05:08.737 2931 INFO nova.virt.libvirt.driver [req-d20b3fad-09d8-47c2-81f2-8b392fdbfbd5 113d3a99c3da401fbd62cc2caa5b96d2 54fadb412c4e40cdbaed9335e4c35a9e - - -] [instance: ae3a1b5d-eec1-45bb-b76a-c59d83b1471f] Deletion of /var/lib/nova/instances/ae3a1b5d-eec1-45bb-b76a-c59d83b1471f_del complete
nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:04:25.372 25788 INFO nova.metadata.wsgi.server [req-ffe3e7b2-f553-4460-aa21-9f437d384256 - - - - -] 10.11.21.128,10.11.10.1 "GET /openstack/2013-10-17/vendor_data.json HTTP/1.1" status: 200 len: 124 time: 0.2238111
```
