# <a name="GUID-658BD7CB-5200-4597-8035-F3AF7F9EF365"/> Starting Sentinel node

Use the `swarm-learning/scripts/bin/run-sn` script to start Sentinel and Swarm Network \(SN\) nodes. This script accepts the following parameters:

|Parameter name|Description|Default value|
|--------------|-----------|-------------|
|`--host-ip <IP address or DNS name>`| The IP address or DNS name of the host system on which this Swarm Network node is created.<br> |None|
|`--sentinel`| If this flag is passed, this node does the Blockchain initialization and make configuration information ready to be shared with other SN nodes. Also it does not expect sentinel node IP to be passed.<br> If this flag is not passed this node is a regular SN node and needs a sentinel node IP for initialization.<br> | |
|`--sentinel-ip <IP address or FQDN name>`| The IP address or FQDN name of the host system on which the Sentinel Swarm Network node is running. If this parameter is not specified, this Swarm Network node makes itself as the sentinel.<br> |None|
|`--sentinel-api-service<Fully Qualified Domain Name[:port]>`| FQDN and optional port for the Sentinel Swarm Network node's API Service.<br> |None|
|`--sn-api-port <port number>`|The host port for this Swarm Network node's API Server.|None|
|`--sn-api-service <fqdn>:<port number>`|Fully Qualified Domain Name and optional port for this Swarm Network node's API Service.| |
|`--sn-p2p-port <port number>`|The host port for this Swarm Network node's P2P communications.|None|
|`--sn-p2p-service <fqdn>:<port number>`|Fully Qualified Domain Name and optional port for this Swarm Network node's P2P Service.| |
|`-v \<blockchain path on host machine\>:/platform/swarm/SMLNODE`|The host path where user wants to persist blockchain across SN restart.|By default, Blockchain data will not be preserved over SN restart.|
