# <a name="GUID-E6440875-7663-49AD-B00E-C767A41CB1B6"/> Starting Swarm Learning node

Use the `swarm-learning/scripts/bin/run-sl` script to start a Swarm Learning \(SL\) node. This script accepts the following parameters:

<blockquote>
NOTE:

-   This script starts only one Swarm Learning node at a time. To launch multiple Swarm Learning nodes, you must invoke this script as many times as desired and on appropriate host systems.

-   HPE recommends to use SWOP to automatically launch SL and ML nodes, which is a preferred way. For more information on launching, *HPE Swarm Learning User Guide*.


</blockquote>

|Parameter name|Description|Default value|
|--------------|-----------|-------------|
|`--host-ip <IP address or DNS name>`|The IP address or DNS name of the host system on which this Swarm Network node is created.|None|
|`--sn-ip <IP address or DNS name>`|The IP address or DNS name of the host system on which the Swarm Network node with which this Swarm Learning node must associate, while running.|None|
|`--sn-api-port <port number>`|The host port for this Swarm Network node's API Server.|None|
|`--sn-api-service <fqdn>:<port number>`|Fully Qualified Domain Name for the SN API Service of associated SN node. Here, Port number is optional.| |
|`--sn-docker-name <container name>`|Docker container name for the associated Swarm Network node.|None|
|`--sl-fs-port`|The host port for this Swarm Learning node's File Server.|None|
|`--sl-fs-service <fqdn>:<port number>`|Fully Qualified Domain Name and optional port for this Swarm Learning node's file service.|None |




