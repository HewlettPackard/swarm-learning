# <a name="GUID-22BEDDA1-E98D-4722-A2AC-EB69DBF2E97B"/> Starting SWOP nodes

Use the `swarm-learning/scripts/bin/run-swop` script to start SWOP nodes. This script accepts the following parameters:

|Parameter name|Description|Default value|
|--------------|-----------|-------------|
|`--usr-dir <dir>`\(Mandatory Parameter\)<br>| Host directory that should be used as the user directory by this SWOP node.<br> | |
|`--profile-file-name <swop-profile file>`\(Mandatory Parameter\)<br>|This file should be located inside the user directory, at the top-level itself.| |
|`--sn-ip <IP address or DNS name>`<br>|The IP address or DNS name of the host system with which this SWOP node must associate with the respective Swarm Network node.|None|
|`--sn-api-port <port number>`<br>|The host port for this Swarm Network node's API Server.|None|
|`--sn-api-service <fqdn>:<port number>`<br>|Fully Qualified Domain Name for the SN API Service of associated SN node. Here, Port number is optional.|None|
