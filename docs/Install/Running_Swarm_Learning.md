# <a name="GUID-5B830FEE-C3BE-491B-AD36-638BBC19638D"/> Running Swarm Learning using CLI

<blockquote>
TIP:

Before you start running the following commands, HPE recommends you to read the *HPE Swarm Learning User Guide* to understand about the architecture of Swarm Learning, how these nodes work, how model training happens, and so on.

For examples of how to provide options to the various run commands, see the *Examples* chapter in *HPE Swarm Learning User Guide*.

</blockquote>

<blockquote>
IMPORTANT:

-   Ensure that network proxy settings are configured correctly and the containers are able to communicate to each other.

-   Ensure that Docker is configured to run as a non-root user by adding your current user ID as part of the Docker group.

-   Ensure that the system time is synchronized across the systems by using NTP.


</blockquote>

Start and run Swarm Learning in the following order. Make sure that License Server is started and the licenses are installed.

1.  The Sentinel Node

2.  Start the Swarm Network node before starting any of the associated Swarm Learning nodes.

3.  After the training is completed, stop all the containers using the script `stop-swarm` on all nodes.


The scripts in the `swarm-learning/bin` directory is used to start these components. To run the scripts, a bash shell and a Linux environment is required.

<blockquote>
NOTE: The default directory where Swarm Learning is installed is `/opt/hpe/swarm-learning`. If the user has changed the default installation directory, all the run commands can be found in that location.

</blockquote>

All start scripts take the following common options for configuring the Docker run command that is used to start the container.

<blockquote>
NOTE: These options do not apply to the `swarm-learning/bin/stop-swarm` script. These options are similar to those of the Docker run command.

</blockquote>

|Parameter name|Description|Default value|
|--------------|-----------|-------------|
|`--hostname <name>`|The host name assigned to the docker container.|`--name`, if it is specified. Otherwise, Docker assigns a host name.|
|`--name <name>`|The name assigned to the docker container.|Docker assigns a random name to the container.|
|`--network <network name>`|The docker network that the container should belong to.|Docker's default bridge network.|
|`--pull`|Pull the docker image from its repository before running it.| False, the image is not pulled from its repository, if it is already available locally<br> |
|`--sudo`|Prefix the Docker commands with "sudo".| False, if the current user belongs to the docker group; true otherwise.<br> |
|`-d, --detach`|Run the container in the background.| A pseudo-terminal is allocated if the launcher has an associated terminal; otherwise, the container is run in the background<br> |
|`-i, --interactive`|Keep STDIN open even if not attached to a terminal.| STDIN is kept open if a pseudo-terminal is allocated to the container; otherwise, it is closed.<br> |
|`-t, --tty`|Allocate a pseudo-terminal for the container.| A pseudo-terminal is allocated if the launcher has an associated terminal; otherwise, the container is run in the background.<br> |
|`-e, --env var=val`|Set an environment variable inside the container.| |
|`-l, --label key=val`|Set metadata on a container.| |
|`-p, --publish host-port:container-port`|Publish a container port to the host.| |
|<code>-u, --user { name &vert; uid } [ : { group &vert; gid } ]</code>|User and group ID to use inside the container.| |
|`-v, --volume host-path:container-path`|Bind mount a volume.| |
|`-w, --workdir container-path`|Working directory inside the container.| |
|`--dns`|The IP address of the custom DNS server. If there are more than one custom DNS servers, then for each DNS, repeat the same argument with different IP address.| |
|`--rm`|Request Docker to automatically remove the container when it exits.| |
|`-h, --help`|This \(helpful\) message.| |
|`--primary-apls-ip <IP address or DNS name>`|The IP address on which the primary Autopass License Server is serving license requests.|None|
|`--secondary-apls-ip <IP address or DNS name>`|The IP address on which the secondary Autopass License Server is serving license requests.|None|
|`--primary-apls-port <port numberw>`|The port number on which the primary Autopass License Server is serving license requests.|5814|
|`--secondary-apls-port <port number>`|The port number on which the secondary Autopass License Server is serving license requests.|The value assigned to --primary-apls-port|
|`--apls-pdf <path to license PD file>`|The path to the license PD file to be used.|None|
|`--cacert <path to certificates file>`|The path to the file containing the list of CA certificates.|None|
|`--capath <path to certificates directory>`|The path to the directory containing CA certificate files.|None|
|`--cert <path to certificate file>`|The path to the certificate file that provides the component's ID.|None|
|`--key <path to key file>`|The path to the private key file corresponding to the certificate.|None|
|`--socket-path <SPIFFE Workload API socket>`|Path, volume or container hosting the socket on which the SPIFFE Agent serves the Workload API.|None|
|`--host-ip <IP address or DNS name>`\(Mandatory parameter\)<br>|The IP address or DNS name of the host system on which this Swarm Learning node is created.| |
|`--sn-ip <IP address or DNS name>`|The IP address or DNS name of the host system on which the Swarm Network \(SN\) node with which this Swarm Learning node must associate, is running.| |
|`--sn-api-port <port number>`|Host port for the API Server of the associated Swarm Network node|30304|
|`--sn-api-service <fqdn>:<port number>`|Fully Qualified Domain Name for the SN API Service of associated SN node. Here, Port number is optional.| |
|`--sl-fs-port <port number>`|Host port for this Swarm Learning node's File Server.|30305|
|`--sl-fs-service <fqdn>:<port number>`|Fully Qualified Domain Name and optional port for this Swarm Learning node's file service.|None |


## <a name="SECTION_R43_RBD_JSB"/> User machine learning container parameters

|Parameter name|Description|
|--------------|-----------|
|`--ml-image <ML image name>`\(Optional parameter\)<br>|Name of the User's Machine Learning image.|
|`--ml-entrypoint <entrypoint>`\(Optional parameter\)<br>|Entry point to the Machine Learning container.|
|`--ml-cmd <command>`\(Optional parameter\)<br>|Command to the Machine Learning container.|
|`--ml-w <directory path>`\(Optional parameter\)<br>|Working directory of the Machine Learning container.|
|`--ml-name <container name>`\(Optional parameter\)<br>|Name of the Machine Learning container.|
|`--ml-v <host-path:container-path>`\(Optional parameter\)<br>|Bind mount a volume for the Machine Learning container.|
|`--ml-e <environmental-variable-name=value>`\(Optional parameter\)<br>|To pass environmental variable to the Machine Learning container.|
|`--ml-user <uid:gid> -`\(Optional parameter\)<br>|The access privilege with which the ML container needs to be spawned on the host.<br>If `--ml-user` is not provided, then ML container would be spawned with current host user’s `uid:gid`.<br>If only `uid` of the host user is provided, then ML container would be spawned with specified host user’s `uid` and primary `gid`.<br> If `uid:gid` of the host user is provided, then ML container would be spawned with specified host user’s `uid:gid`.|
|**For AMD GPUs, one may need to use the following parameters:**|Refer for more details: https://developer.amd.com/resources/rocm-learning-center/deep-learning/| 
|`--ml-device`|Expose host devices to the container, as a list of strings.|None|
|`--ml-ipc`|Sets the IPC mode for the container.|None|
|`--ml-shm-size`|Size of `/dev/shm` (for example, 1G).|None|
|`--ml-group-add`|List of additional group names and/or IDs that the container process will run as.|None|
|`--ml-cap-add`|Add kernel capabilities.|None|
|`--ml-security-opt`|A list of string values to customize labels for MLS systems, such as SELinux.|None|
|`--ml-privileged`|Provides extended privileges to this container.|None|

Also see:

   -   [Starting Sentinel node](Starting_Sentinel_node.md)
   -   [Starting Swarm Learning node](Starting_Swarm_Learning_node.md)
   -   [Starting SWCI nodes](Starting_SWCI_nodes.md)
   -   [Starting SWOP nodes](Starting_SWOP_nodes.md)
   -   [Stopping Swarm Learning node](Stopping_Swarm_Learning_node.md)
   -   [Uninstalling the Swarm Learning package](Uninstalling_the_Swarm_Learning_package.md)
