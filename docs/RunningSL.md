# Config parameters

Swarm Learning has a few configuration parameters. See *[Running Swarm Learning](RunningSL.md#Running-Swarm-Learning)* for instructions on specifying these parameters.

## 1. The data directory

This directory contains the training and validation data for the ML program. It can represent any valid directory on the host system to which the current user has read permissions. This directory is mounted on the Swarm Learning container as a read-only bind mount volume under the path ``/platform/swarmml/data``.

## 2. The model directory

This directory contains the ML program that is executed inside the Swarm Learning container. It can also contain data preprocessing 
logic and configuration files for the ML program to use. When the program executes, the output and logs are written to files in this directory. Just like the data directory, this too can represent any valid directory on the host system -- but the current user should  have read and write permissions on this directory. This directory is mounted on the Swarm Learning container in read-write mode under  the path ``/platform/swarmml/model``.

## 3. The ML program to execute

This is the name of the python ML program that should execute inside the Swarm Learning container. This program should be in the model directory.

## 4. IP addresses of the host systems

By default, Swarm Learning uses the host network to connect and communicate with its peers. In this case, the IP addresses represent
the IP addresses or FQDN of the host systems on which the containers are run. Swarm Learning can be configured to use a docker bridge
network also -- in this case, the IP addresses represent the IP addresses or FQDN of the containers themselves.

## 5. Exposed port numbers

Depending on the type of Swarm Learning components that are running on a host, some or all these ports should be opened to allow the Swarm Learning containers to communicate with each other:

    1.  A Swarm Network peer-to-peer port on the hosts running Swarm Network nodes. By default, port 30303 is used.

    2.  A Swarm Network API server port on the hosts running Swarm Network nodes. By default, port 30304 is used.

    3.  A Swarm Network file server port on the hosts running Swarm Network nodes. By default, port 30305 is used.

    4.  A Swarm Learning file server port on the hosts running Swarm Learning nodes. By default, port 30305 is used.

    5.  A SPIRE Server API server port on the hosts running SPIRE Server nodes. By default, port 8081 is used.

    6.  A SPIRE Server Federation port on the hosts running SPIRE Server nodes. By default, the SPIRE Servers do 
        not federate with each other. Federation should be configured by the user.

    7.  A License Server API port on the host running the License Server. By default, port 5814 is used.

## 6. The GPU to use

Swarm Learning can utilize NVIDIA GPUs, if the appropriate drivers and toolkits have been installed. To utilize a GPU, its index number should be passed as a parameter to the Swarm Learning container. GPU indexes start from zero.
> NOTE: Eval version of Swarm Learning with ML platform set to PyTorch(PYT) does not support GPU usage.

## 7. SPIRE Server configuration

The Swarm Network and Swarm Learning nodes use SPIFFE-based X.509 certificates for secure communication. These nodes can interact with any standard SPIRE Server to acquire their SPIFFE IDs and SVIDs. For convenience, a SPIRE Server is provided along with the other components in the Swarm Learning package. This Server accepts any standard SPIRE Server configuration parameter. It also creates two registration entries automatically -- one each for the Swarm Network and Swarm Learning nodes. Assuming the trust domain is swarm.learning, the Server automatically creates these entries:

-   Registration entry for Swarm Learning nodes

        spire-server entry create -parentID
        spiffe://swarm.learning/swarm/sl-agent -spiffeID
        spiffe://swarm.learning/swarm/sl -selector swarm:node-type:sl -dns
        swarm-learning-node

-   Registration entry for Swarm Network nodes

        spire-server entry create -parentID
        spiffe://swarm.learning/swarm/sn-agent -spiffeID
        spiffe://swarm.learning/swarm/sn -selector swarm:node-type:sn -dns
        swarm-network-node

Note the custom selector, swarm. This selector refers to a custom workload attestor plugin that runs inside the Swarm Network and Swarm Learning containers. This plugin is responsible for attesting Swarm Learning workloads.

## 8. SPIRE Agent configuration

The Swarm Network and Swarm Learning nodes run a standard SPIRE Agent process and a custom workload attestor plugin. The agent should be configured to use this plugin by adding this entry to its configuration file:

       WorkloadAttestor "swarm" {
       plugin_checksum =
       "1f4ebd50d3df02bfc101d54d0d799f14357e798d44941ab2ab537f52819884dd"
       plugin_cmd = "/spire/bin/spire-swarm-plugin"
       plugin_data {}
       }

By default, the agent uses join tokens to connect to the server. This can be changed to any other standard mechanism by specifying the details in the agent configuration file or on the command line. The agent accepts all standard options and parameters.

# Running Swarm Learning
| :warning: WARNING                                                                                                    |
|:---------------------------------------------------------------------------------------------------------------------|
|  1. Ensure your network proxy settings are configured correctly and the containers are able to talk to each other.   |
|  2. If you specify `--gpu`, ensure the GPUs are available. 
|  3. `Effective user` inside the docker container should be root. The run scripts below currently ensures this by default.

This is the order to start and run Swarm Learning. As mentioned earlier, the License Server should have been started and the licenses installed.

1.  The SPIRE servers.

2.  The Sentinel node.

3.  The Swarm Network node should be started before any of the associated Swarm Learning nodes are started.

4.  When the training run is completed, stop all the containers by using the stop-swarm script on all nodes.

The scripts in the ``swarm-learning/bin`` directory can be used for starting these components. All scripts requires a bash shell and a Linux environment to run. All start scripts take the following common options for configuring the docker run command that is used to start the container. Note that these options do not apply to the ``swarm-learning/bin/stop-swarm`` script. These options are similar to those of the docker run command.

-   ``--hostname <name>``

    The host name assigned to the component\'s docker container.

    Default: --name, if it is specified; none otherwise

-   ``--name <name>``

    The name assigned to the component\'s docker container.

    Default: None

-   ``--network <network name>``

    The network that the container should belong to.

    Default: docker\'s default bridge network

-   ``--sudo``

    This parameter specifies that *sudo* should be used when invoking docker to create and start containers for the Swarm Learning components.

    *sudo* is not required if the current user has been added to the *docker* group. See [resources](URL.md#16-httpsdocsdockercomengineinstalllinux-postinstallmanage-docker-as-a-non-root-user). 
    If the current user has not been added to the *docker* group and does not have *sudo* privileges, the scripts will return a *permission-denied* error -- it will not create the Swarm Learning components.

    Default: docker commands are prefixed with sudo if the user is not a member of the docker group.

-   ``-d, --detach``

    Run the container in the background.

    Default: A pseudo-terminal is allocated if the launcher has an associated terminal; otherwise, the container is run in the background

-   ``-i, --interactive``

    Keep STDIN open even if not attached to a terminal.

    Default: STDIN is kept open if a pseudo-terminal is allocated; otherwise, it is closed.

-   ``-t, --tty``

    Allocate a pseudo-terminal for the container.

    Default: A pseudo-terminal is allocated if the launcher has an associated terminal; otherwise, the container is run in the background

-   ``-e, --env var=val``

    Set an environment variable inside the container

-   ``--net, --network <network>``

    Connect the container to a network

-   ``-l, --label key=val``

    Set meta data on a container

-   ``-p, --publish host-port:container-port``

    Publish a container\'s port to the host

-   ``-u, --user { name | uid } [ : { group | gid } ]``

    User and group ID to use inside the container

-   ``-v, --volume host-path:container-path``

    Bind mount a volume

-   ``-w, --workdir container-path``

    Working directory inside the container

-   ``--rm``

    Request Docker to automatically remove the container when it exits
    
-   ``--ssh-port <ssh port number>``

    This parameter specifies the port number on which the SSH server is listening. It is optional.It should be specified in a multi-system cluster environment when the 
    SSH servers are not listening on the default SSH port.
    
    Default: 22

-   ``--ssh-user <ssh user name>``

    This parameter specifies the user name to use when establishing an SSH connection. It is optional. When it is not specified, the current user's login name is used.

-   ``-h, --help``
    
    A brief help message.

## Starting the License Server

Use the swarm-learning/bin/run-apls script to start the License Server. See [resources](URL.md#15-autopass-license-server-user-guide-v98-included-with-this-package-distribution), for details of installing and managing licenses using the server.

-   ``--apls-port <port number>``

    The host port to which the License Server API and management port is published.
    
    Default: 5814

## Starting the SPIRE Server

Use the ``swarm-learning/bin/run-spire-server`` script to start the SPIRE Server. See 19 and 20 under [resources](URL.md#19-httpsgithubcomspiffespiretreemaindoc) for configuration details.

## Starting SN nodes

Use the ``swarm-learning/bin/run-sn`` script to start Sentinel and Swarm Network nodes. This script accepts the following parameters:

-   ``--apls-ip=<IP>``

    The IP address or FQDN of the system on which the License Server is running.

    Default: the script attempts to detect whether a License Server is running on the host system. If found, the script uses its IP address.

-   ``--apls-port=<port number>``

    The host port on which the License Server is listening for requests

    Default: 5814

-   ``--apls-docker-name <docker container name>``

     The name of the docker container running the License Server. This is used to retrieve the IP of the License Server, when ``--apls ip`` is not specified.

    Default: none

-   ``--host-ip=<IP>``

    This parameter specifies the IP address of the system on which the Swarm Network node is being started.

    This parameter is required.

-   ``--sentinel-ip=<IP>``

    This parameter specifies the IP address of the system on which the Sentinel node is running. When this script is used to start a Sentinel node, the same IP address should be specified for both the ``--host-ip`` and the ``--sentinel-ip`` parameters. The Sentinel node should be started before any of the other Swarm Network nodes are started.

    This parameter is required.

-   ``--sn-p2p-port=<port number>``

    This parameter specifies the *Swarm Network peer-to-peer port*.

    This parameter is optional. When it is not specified, port 30303 is used as a default value.

-   ``--sn-api-port=<port number>``

    This parameter specifies the *Swarm Network API server port*.

    This parameter is optional. When it is not specified, port 30304 is used as a default value.

-   ``--sn-fs-port=<port number>``

    This parameter specifies the *Swarm Network file server port*.

    This parameter is optional. When it is not specified, port 30305 is used as a default value.

-   ``--sentinel-fs-port=<port number>``

    This parameter specifies the port on which the Sentinel node\'s file server is listening for connections.

    This parameter is optional. When it is not specified, port 30305 is used as a default value. This parameter is not required if the Sentinel node\'s file server is listening for connections on the default port, 30305. If \--sn-fs-port has been used while starting the Sentinel node to change the port on which its file server listens for connections, this parameter should be specified -- the Swarm Network node will not complete its initialization process, if this parameter is omitted.

-   ``-genJoinToken, --gen-join-token``

    Generate a join token that the SPIRE Agent can use to authenticate itself to the SPIRE Server.
    
    >**NOTE: The systems should have been configured with passwordless SSH for this to work.**

-   ``-serverAddress <IP address or DNS name>``

    The IP address or DNS name of the SPIRE server.
    
    Default: None

-   ``--spire-docker-name <docker container name>``

    The name of the docker container running the SPIRE Server. This is used to generate a join token, when ``-genJoinToken`` or ``--gen join-`` token  is specified.

    Default: none

-   ``--help``

    This prints a short message on using the script.

In addition to these, the script accepts all standard SPIRE Agent configuration parameters. See 19 and 20 under [resources](URL.md#19-httpsgithubcomspiffespiretreemaindoc).

## Starting the SL nodes

Use the ``swarm-learning/bin/run-sl`` script to start a Swarm Learning node. Note that this script starts just a single Swarm Learning node at a time. To launch multiple Swarm Learning nodes, you should invoke this script as many times as desired and on the right host systems. This script accepts the following parameters:

-   ``--apls-ip=<IP>``

    The IP address of the system on which the License Server is running.

    Default: the script attempts to detect whether a License Server is  running on the host system. If it finds one, the script uses its IP.

-   ``--apls-port=<port number>``

    The host port on which the License Server is listening for requests

    Default: 5814

-   ``--apls-docker-name <docker container name>``

    The name of the docker container running the License Server. This is used to retrieve the IP of the License Server, when ``--apls -ip`` is not specified.

    Default: none

-   ``--data-dir=<directory path>``

    This parameter specifies the *data directory* for the Swarm Learning node.

-   ``--model-dir=<directory path>``

    This parameter specifies the *model directory* for the Swarm Learning node.

-   ``--model-program=<program name>``

    This parameter specifies the name of the Keras or PyTorch based, Python3 ML program to execute inside the Swarm Learning node. The current user must have the requisite permissions to execute this program.
    
    This parameter is required.

-   ``--host-ip=<IP>``

    This parameter specifies the IP address of the system on which the Swarm Learning node is being started.

    This parameter is required.

-   ``--sn-ip=<IP>``

    This parameter specifies the IP address of the system on which a Swarm Network node is running. This Swarm Network node should have been started before starting the Swarm Learning node. As a part of its initialization, the Swarm Learning node will register itself with this Swarm Network node.

    This parameter is required.

-   ``--sn-api-port=<port number>``

    This parameter specifies the *Swarm Network api server port* that is being used by the Swarm Network node associated with this Swarm Learning node.

    This parameter is optional. When it is not specified, port 30304 is used as a default value.

-   ``--sl-fs-port=<port number>``

    This parameter specifies the Swarm *Learning file server port*.

    This parameter is optional. When it is not specified, port 30305 is used as a default value.

-   ``--sl-platform { PYT | TF }``

    The ML platform to use -- PYT for PyTorch; or TF for TensorFlow

    Default: TensorFlow

-   ``--gpu=<set of GPUs to use>``

    This parameter specifies the GPUs to use. A Swarm Learning node can use multiple GPUs. The set of GPUs to use can be specified in one of two ways:
    
    a.  A comma-separated list of GPU indexes -- GPU indexes start from zero.
    
    b.  `all` -- all GPUs on the system are used.
    
    This parameter is optional. When it is not specified, the Swarm Learning nodes will run on the CPU only and will not use any GPU.
    
    >   NOTE: Eval version of Swarm Learning with ML platform set to PyTorch(PYT) does not support GPU usage.


-   ``-genJoinToken, --gen-join-token``

    Generate a join token that the SPIRE Agent can use to authenticate itself to the SPIRE Server.

    >   **NOTE: The systems should have been configured with passwordless SSH for this to work.**

-   ``-serverAddress <IP address or DNS name>``

    The IP address or DNS name of the SPIRE server.

    Default: None

-   ``--spire-docker-name <docker container name>``

    The name of the docker container running the SPIRE Server. This is  used to generate a join token, when ``-genJoinToken`` or ``--gen- join-`` token is specified.

    Default: none

-   ``--help``

    This prints a short message on using the script.

In addition to these, the script accepts all standard SPIRE Agent configuration parameters. See 19 and 20 under [resources](URL.md#19-httpsgithubcomspiffespiretreemaindoc).

## Starting SWCI nodes

Use the swarm-learning/bin/run-swci to launch SWCI. It shows the swci prompt when it comes up successfully. The user can enter any command from the pre-defined set of commands. It supports a list of well-defined commands that are self-explanatory. There is a built-in online help, that lists all supported commands and further one can drill down and see help for each command``::``

    +-----------------------------------------------------------------------+
    | SWCI:2 > help HELP                                                    |
    |                                                                       |
    | HELP [command:string]                                                 |
    |                                                                       |
    | Help without parameter lists all supported commands.                  |   
    |                                                                       |
    | Help with command name show help content for the specified command.   |
    |                                                                       |
    | SWCI:3 >                                                              | 
    +-----------------------------------------------------------------------+

Typically one should launch the SWCI node, after the SN nodes are started. We can also start the SWCI node after the SPIFFE server is
running, in which case only limited functionality would be available.

The run-swci script accepts the following parameters:

-   ``-config <config file>``

    The path to the configuration file for the SPIRE agent.

    Default: None

-   ``-genJoinToken``

    Generate a join token that the SPIRE agent can use to authenticate  itself to the SPIRE server.

    Default: false, a join token is not generated.

-   ``-serverAddress <IP address or DNS name>``

    The IP address on which the SPIRE server is serving API requests.

    Default: None

-   ``--spire-docker-name <container name>``

    The name of the SPIRE server docker container instance.

    Default: None

-   ``--usr-dir <dir>``

    Host directory that should be used as the user directory by this SWCI node.

    Default: None

-   ``--init-script-name <swci-init file>``

    Name of script file that has SWCI commands to be executed at the start of SWCI.

    This file should be located inside the user directory, at the top-level itself.

    Default: swci-init

In addition to these, the script accepts all standard SPIRE Agent configuration parameters. See [19](URL.md#19-httpsgithubcomspiffespiretreemaindoc) and [20](URL.md#19-httpsgithubcomspiffespiretreemaindoc) under resources.

## Stopping

Use the swarm-learning/bin/stop-swarm script to stop all Swarm Network and Swarm Learning nodes that are running on a host system. Note that this script does not operate across systems. It must be invoked on each host system to stop the Swarm Learning platform completely. [By default: All components except License Server are stopped.]{.ul}

This script accepts the following optional parameters:

-   ``--all``

    Stop all Swarm Learning components running on the system -- Swarm  Network nodes, Swarm Learning nodes, SPIRE Servers and the License Server as well.

-   ``--apls``

    Stop the License Server.

-   ``--spire-server``

    Stop all SPIRE Servers.

-   ``--sl``

     Stop all Swarm Learning nodes, those running with the PyTorch backend as well as those running with the TensorFlow backend.

-   ``--sl-pyt``

    Stop all PyTorch-based Swarm Learning nodes.

-   ``--sl-tf``

    Stop all TensorFlow-based Swarm Learning nodes.

-   ``--sn``

    Stop all Swarm Network nodes.

-   ``--keep``

    This parameter specifies that the docker containers associated with  the Swarm Learning nodes should not be removed after they have  been stopped.

    This parameter is optional. When it is specified, the containers are stopped but not removed. In this case, the Log output from the containers are still available after the script has run. The leftover containers can be removed, either manually or by invoking this script again without the \--keep parameter.

-   ``--sudo``

    This parameter specifies that *sudo* should be used when invoking docker to stop or remove the Swarm Learning nodes.
    
    *sudo* is not required if the current user has been added to the *docker* group. See [resources](URL.md#16-httpsdocsdockercomengineinstalllinux-postinstallmanage-docker-as-a-non-root-user). 
    If the current user has not been added to the docker group and does not have *sudo* privileges, the scripts will return a permission-denied error. It will not stop or remove the Swarm Learning components.

    Default: docker commands are prefixed with sudo if the user is not a  member of the docker group.

-   ``--help``

    This prints a short message on using the script.

## Clean-up

After the Swarm Learning platform has finished execution and has produced the final model, *the host systems should be cleaned up before they can be used to run the framework again*. All docker containers created by previous runs should be stopped and removed. Use the swarm-learning/bin/stop-swarm script to do this. Any log output produced by the containers should be saved before invoking the script as they will not be available after the script is executed.

Output files that have been written to the model directory by previous runs might also require attention. These files are the user\'s
prerogative and responsibility entirely &mdash; the Swarm Learning package does not provide any means for handling these files.
