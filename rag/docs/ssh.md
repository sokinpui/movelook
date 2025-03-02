## 1. Introduction to OpenSSH
OpenSSH (Open Secure Shell) is the leading open-source implementation of the SSH (Secure Shell) protocol, widely used for secure remote login and file transfer over untrusted networks. Developed as part of the OpenBSD project, OpenSSH provides a suite of tools—including ssh, scp, and sftp—for encrypted communication between clients and servers. It is renowned for its security, reliability, and flexibility, making it a standard connectivity tool in both research and operational environments.

Key features of OpenSSH include:

Encryption: Secures all communication using strong cryptographic algorithms.
Authentication: Supports multiple methods, such as passwords, public keys, and multi-factor authentication.
Tunneling: Enables secure transmission of arbitrary data through SSH tunnels.
In this system, OpenSSH logs were collected from a server running in a lab environment over a period exceeding 28 days. These logs capture server activities and interactions, offering a dataset for studying SSH usage patterns, security events, and potential anomalies.

## 2. System Overview
The logs were gathered from an OpenSSH server deployed in a lab setting, reflecting a mix of normal activities—such as user logins and file transfers—and potential security-related events (e.g., failed login attempts).

The logs are stored in a single file, SSH.log, which aggregates all recorded events from the OpenSSH server during this period. This dataset is suitable for analyzing server behavior, detecting security incidents, and mining operational insights.

## 4. Contents of the Logs
OpenSSH logs typically include the following types of information:

Timestamps: Date and time of each event (e.g., 2025-03-02 13:45:12).
Connection Events: Details about client connections, including:
Successful logins (e.g., "Accepted publickey for userX from IP").
Failed login attempts (e.g., "Failed password for userY from IP").
Disconnections (e.g., "Connection closed by IP").
Authentication Details: Methods used (e.g., password, public key) and outcomes.
Errors and Warnings: Issues like "Invalid user," "Connection timeout," or "Permission denied."
Session Activity: Commands executed, file transfers (via scp or sftp), or tunneling events, depending on logging verbosity.

## some sampled line from the log
```
Dec 10 11:00:03 LabSZ sshd[25224]: Failed password for root from 183.62.140.253 port 40454 ssh2
Dec 10 09:18:35 LabSZ sshd[24643]: Failed password for invalid user admin from 103.207.39.16 port 46723 ssh2
Dec 10 09:12:04 LabSZ sshd[24471]: Invalid user user from 103.99.0.122
Dec 10 09:12:09 LabSZ sshd[24473]: error: Received disconnect from 103.99.0.122: 14: No more user authentication methods available. [preauth]
Dec 10 09:11:53 LabSZ sshd[24462]: input_userauth_request: invalid user admin [preauth]
Dec 10 11:00:24 LabSZ sshd[25250]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=183.62.140.253  user=root
Dec 10 10:56:21 LabSZ sshd[24992]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=183.62.140.253  user=root
Dec 10 09:18:54 LabSZ sshd[24649]: Failed password for invalid user nagios1 from 187.141.143.180 port 43647 ssh2
Dec 10 09:19:42 LabSZ sshd[24667]: reverse mapping checking getaddrinfo for customer-187-141-143-180-sta.uninet-ide.com.mx [187.141.143.180] failed - POSSIBLE BREAK-IN ATTEMPT!
Dec 10 09:12:35 LabSZ sshd[24492]: error: Received disconnect from 103.99.0.122: 14: No more user authentication methods available. [preauth]

```
