# <a name="GUID-C1705ADA-8DC5-47D6-B22D-EEDD2F938059"/> Environment variables

The environment variables are passed to containers or added to the environment variable through profile or configuration files. The following environment variables are available to set and modify:

|<strong>Environment variable name</strong>|<strong>Description</strong>|
|------------------------------------------|----------------------------|
|`SWARM_LOOPBACK`|Used to bypass Swarm Learning to help you quickly develop, integrate, and test your model code with Swarm Learning package.If SWARM\_LOOPBACK is set to 'True', then all Swarm functionality will be bypassed, except parameter validation.<br>This can help you to verify and test integration of the model code with Swarm <strong>without spawning any Swarm Learning containers</strong>.<br>|
|`LOGS_DIR`|Sets the directory for Swarm components log, it is set usually by Docker file.|
|`USR_DIR`|Sets the directory for Swarm components, it is set usually by Docker file.|
|`SN_ETH_PORT_EXT`|Sets an Ethernet port for Swarm Network node.|
|`SN_I_AM_SENTINEL`| Sets a Swarm Network node to become the Sentinel node, only when it is set to true.<br> Default value: False<br> |
|`SN_START_MINING`| Starts mining on non-sentinel nodes. \(Optional\)<br> Default value: False<br> |
|`SL_WAIT_FOR_FULL_QUORUM_SECONDS`|Sets maximum time to wait for full quorum before an SL node, designated as leader node, decides to use minPeers nodes.|
|`SWCI_MODE`| Enables SWCIs web interface instead of command line interface. Allowed values are CLI and WEB.<br> Default value: CLI<br> |
|`SWCI_STARTUP_SCRIPT`|This is a default start script of SWCI.|
|`SWCI_WEB_PORT`|Default port on which SWCI-WEB starts server.|
|`SWOP_PROFILE`|Indicates default profile for SWOP.|
|`SWARM_ID_CACERT`|Indicates user CA certificates file.|
|`SWARM_ID_CAPATH`|Indicates user CA certificates directory.|
|`SWARM_ID_CERT`|Indicates user certificates file.|
|`SWARM_ID_KEY`|Indicates user SSH key file.|
|`SWARM_SPIFFE_WORKLOAD_API_SOCKET_PATH`|Used for acquiring a SPIFFE identity. It points to the UNIX domain socket on which the SPIFFE agent is serving the SPIFFE workload API. For more information, [https://spiffe.io/](https://spiffe.io/) |

