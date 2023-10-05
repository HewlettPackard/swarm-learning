# <a name="GUID-C1705ADA-8DC5-47D6-B22D-EEDD2F938059"/> Environment variables

The environment variables are passed to containers or added to the environment variable through profile or configuration files. <br>
<blockquote>

**Note:**

Environment variables starting with a Swarm component name (for example, SN_, SL_) are meant for those particular     components. Environment variables starting without a Swarm component name are meant for all Swarm components. 
  
</blockquote>


The following environment variables are available to set and modify:

|<strong>Environment variable name</strong>|<strong>Description</strong>|
|------------------------------------------|----------------------------|
|`SWARM_LOOPBACK`|Used to bypass Swarm Learning to help you quickly develop, integrate, and test your model code with Swarm Learning package.If SWARM\_LOOPBACK is set to 'True', then all Swarm functionality will be bypassed, except parameter validation.<br>This can help you to verify and test integration of the model code with Swarm <strong>without spawning any Swarm Learning containers</strong>.<br>|
|`LOGS_DIR`|Sets the directory for Swarm components log, it is set usually by Docker file.|
|`USR_DIR`|Sets the directory for Swarm components, it is set usually by Docker file.|
|`SN_ETH_PORT_EXT`|Sets an Ethernet port for Swarm Network node.|
|`SN_I_AM_SENTINEL`| Sets a Swarm Network node to become the Sentinel node, only when it is set to true.<br> Default value: False<br> |
|`SN_START_MINING`| Starts mining on non-sentinel nodes. \(Optional\)<br> Default value: False<br> |
|`SL_MAKE_ME_ADMIN`| Determines whether an SL node can participate in leader election or not. \(Optional\)<br> Default value: True<br> If SL_MAKE_ME_ADMIN is set to ‘False’, the corresponding SL node will not participate in leader election. If user doesn’t want to make a slow node (with less compute power, network band width etc) as a leader, then this can be set to ‘False’. |
|`SL_LEADER_FAILURE_BASE_TIMEOUT`|Sets the minimum timeout value \(in seconds\). If Swarm merging does not happen within this timeout, a new SL leader node is selected. The swarm training continues to run, regardless of SL leader node failures. This timeout will kickin after `min_peers` nodes have completed their local training. <br> Default value: 600 seconds. <br>This variable may need tunning depending on the ML application complexity.|
|`SL_WAIT_FOR_FULL_QUORUM_SECONDS`|Sets the maximum time for an SL leader node to wait for full quorum after minPeers are ready for merge. This parameter lets you to maximize the number of peers participating in the merge process.<br>Default value: 30 secs|
|`SL_RAM_INTENSIVE`|Optimizes the usage of RAM in the SL leader node for coordinate and geometric median merge methods. Unlike mean merge method, coordinate and geometric median merge methods involve memory intensive operations. If SL Leader node has limited hardware \(RAM\) configuration, then merging the intermediate model parameters using the median methods can result in memory issues. For such scenarios, user can set up the SL\_RAM\_INTENSIVE flag to 'False' for merging the model parameters layer by layer. This 'False' option is based on I/O operations and is time consuming, hence the default option is set to 'True'.<br> User can pass this parameter in slenvvars option within SWOP profile. This option can be different for each SL node depending on its hardware capacity. Example: 'slenvvars : \[SL\_RAM\_INTENSIVE : False\]' <br> Default value: True|
|`SWCI_TASK_MAX_WAIT_TIME`|Specifies a maximum timeout value for the completion of a task.<br>This value must be set in minutes, and the default is 120 mins (2 hours).
|`SWCI_MODE`| Enables SWCIs web interface instead of command line interface. Allowed values are CLI and WEB.<br> Default value: CLI<br> |
|`SWCI_STARTUP_SCRIPT`|This is a default start script of SWCI.|
|`SWCI_WEB_PORT`|Default port on which SWCI-WEB starts server.|
|`SWOP_PROFILE`|Indicates default profile for SWOP.|
|`SWOP_KEEP_CONTAINERS`|By default, SL and ML containers spawned by SWOP are removed. This option can be enabled to retain the stopped containers for debugging.<br>Default value: False|
|`SWARM_ID_CACERT`|Indicates user CA certificates file.|
|`SWARM_ID_CAPATH`|Indicates user CA certificates directory.|
|`SWARM_ID_CERT`|Indicates user certificates file.|
|`SWARM_ID_KEY`|Indicates user SSH key file.|
|`SWARM_SPIFFE_WORKLOAD_API_SOCKET_PATH`|Used for acquiring a SPIFFE identity. It points to the UNIX domain socket on which the SPIFFE agent is serving the SPIFFE workload API. For more information, [https://spiffe.io/](https://spiffe.io/) |

