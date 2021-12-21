#  Frequently Asked Questions 

## What is Swarm Learning?
Swarm Learning is a decentralized, privacy-preserving Machine Learning framework. This framework utilizes the computing power at, or near, the distributed data sources to run the Machine Learning algorithms that train the models. It uses the security of a blockchain platform to share learnings with peers in a safe and secure manner.

## What are the components of Swarm Learning?

Swarm Learning has 5 types of components that form a network. They are Swarm Learning nodes, Swarm Network nodes, SWCI nodes, SPIRE Server nodes, and License Server nodes.

## What is the License server node?

The License server (apls) node is a special node running the HPE AutoPass license server. It is responsible for validating the licenses
of the Swarm Learning framework. There is typically one instance of this node running in the Swarm.

## What is the SPIRE server node?

SPIRE is a production-ready implementation of the [SPIFFE standard](URL.md#9--httpsspiffeio). It provides a secure identity to workloads. The SPIRE architecture has
two main components &mdash; an agent and a server. The agent is responsible for attesting workloads and managing SPIFFE identities on their behalf.
The server is responsible for issuing the identities. There is typically one instance of the SPIRE server with a simple configuration.

## What is the Sentinel node?

The Sentinel node is a special Swarm Network node. It is responsible for initializing the blockchain network and deploying the smart contracts on the blockchain. For this reason, the Sentinel node should be **the very first Swarm Network node** that is started in the Swarm Learning framework. Once the blockchain network has been initialized, there is no difference between the functioning of the Sentinel node and that of the other Swarm Network nodes.

## How do you know if Swarm Network node started successfully?

Look for following message after executing `run-sn` command to confirm successful starting of Swarm Network node. It might take a few minutes before this message appears. 

`swarm.blCnt : INFO : Starting SWARM-API-SERVER on port :30304 (30304 is the default port).`

This message does not show up if APLS or SPIRE server is not configured correctly.


## How do you run Swarm Learning on CPU?

When you start the Swarm Learning nodes by running ``swarm-learning/bin/run-sl``, to use only the CPU for these nodes, ***do not*** specify the --gpu
parameter while invoking the script. The other swarm learning components like Swarm Network, SWCI, License server, and SPIRE server always run on the CPU. Use ``swarm-learning/bin/run-sl --help`` to get details.

## How do you run Swarm Learning on GPU?

Only the Swarm Learning nodes can run on GPUs. The license server, SPIRE server, SWCI and Swarm Network nodes utilize only the CPUs.

Start the Swarm Learning nodes by running ``swarm-learning/bin/run-sl``. To make these nodes utilize the GPUs on the host system, specify the --gpu
parameter, with the set of GPUs to use as a value, while invoking the script. The set of GPUs to use can be specified by either a
comma-separated list of GPU indexes or, the keyword all. Specifying all makes the container utilize all available GPUs on the host.

Use ``swarm-learning/bin/run-sl --help`` to get details.

> NOTE: Eval version of Swarm Learning with ML platform set to PyTorch(PYT) does not support GPU usage.

## Can you have heterogeneous nodes, with some running on CPU and others on GPU?

Yes, the framework is designed to work seamlessly on heterogeneous hardware. For each Swarm Learning node, you can specify whether it
should run on the GPU or the CPU by either including or leaving out the ``--gpu`` parameter when you invoke ``swarm-learning/bin/run-sl``.

## What network ports does Swarm Learning use? Can they be customized?

Each Swarm Network node requires three network ports for incoming connections from other Swarm Network and Swarm Learning nodes.

1.  One Swarm Network peer to peer communication port, which is meant for peer-to-peer communication using the underlying blockchain
    platform's protocols. By default, port 30303 is used.

2.  One Swarm Network API server port, which is meant for running a REST-based API server on each Swarm Network node. By default, port
    30304 is used.

3.  One Swarm Network file server port, which is meant for running a file server on each Swarm Network node. By default, port 30305 is
    used.

Each Swarm Learning node requires one network port for incoming connections from other Swarm Learning nodes.

1.  A Swarm Learning file server port, which is meant for running a file server on each Swarm Learning node. By default, port 30305 is used.

Each SPIRE Server node requires one network port for incoming connections from other nodes.

1.  A *SPIRE Server API server port,* which is meant for running a gRPC-based API server. By default, port 8081 is used.

Each License Server node requires one network port for incoming connections from other nodes.

1.  A *License Server API server port,* which is meant for running a REST-based API server. By default, port 5814 is used.

SWCI does not expose any port.

The port numbers can be customized by using the corresponding ``swarm-learning/bin/run-sn``, ``swarm-learning/bin/run-sl``, ``swarm-learning/bin/run-spire-server``,
and ``swarm-learning/bin/run-apls`` scripts that are supplied with the Swarm Learning package. Use the --help option on the above scripts to get
exact details.

## Where are the log files?

The system log files are the docker logs. By default, the docker containers that run the APLS license server, SPIRE server, Swarm
Network, and Swarm Learning nodes are not removed after they exit. Log output produced by these containers can be retrieved using the docker
logs command.

For a Swarm Learning node, a subset of the log output is stored with the name ``<program-name>_sw.log``, in the model directory.

The ML program can produce additional log output. To do so, it should be modified to write this output to files in the model directory.

## Do you need sudo/root privileges to run Swarm Learning?

sudo is not required to launch the container, if docker is configured to run as a non-root user. Refer [Manage Docker as a non-root user](URL.md#16-manage-docker-as-a-non-root-user-httpsdocsdockercomengineinstalllinux-postinstallmanage-docker-as-a-non-root-user)

If docker is not configured to run as a non-root user, the scripts will automatically prefix docker commands with sudo. If the user does not have sudo privileges, an error will result.

>**NOTE**: Effective user inside the docker container should be root.

## Can each Swarm Learning node run a different ML program and parameters?

No. The program and parameters should be the same across all the Swarm Learning nodes.

## How do you uninstall Swarm learning?

Use the docker log command to save any container log output that you want to preserve. Use a directory outside the swarm-learning
installation directory. Also, consider cleaning the model directories by removing unnecessary files and subdirectories.

Use the ``swarm-learning/bin/uninstall`` script to uninstall the Swarm Learning package. This script does not accept any command line
parameters. It should run on every node where Swarm Learning package is installed. While running, it stops all Swarm Learning components that
are running on that host, removes the docker container images, and deletes the swarm-learning installation directory.

## Why is blockchain required? Can you use a different blockchain network?

Swarm Learning uses a blockchain network primarily to provide a consistent system state to all the nodes without requiring any central
coordinator.

The current implementation runs an open-source version of Ethereum but, more platforms might be added in the future. At the time of
initialization, the framework spawns its own blockchain network with a custom set of parameter values. Hence it *cannot be replaced* with any
other blockchain network. This applies even when the blockchain platform is a supported one.

## What are the supported machine learning platforms?

Swarm Learning runs on PyTorch 1.5 and Keras (based on TensorFlow 2). Machine learning models are implemented in Python3.

## What models work with swarm learning?

Swarm Learning works with all connectionist machine learning models such as NN, CNN, RNN, and LSTM.

## What are the supported Python packages in Swarm Learning?

We support the following basic packages required for ML - numpy, scipy, matplotlib, opencv-python, pandas, pillow, sklearn.

## Can one add new Python packages in Swarm Learning?

Yes. For any additional support packages to machine learning process, user has to do following.

1. Write a dockerfile to create a local SL image
    - By extending FROM the default SL image (sl-tf or sl-pyt).
    - Add required additional packages
2. Build the local SL image from above dockerfile.
3. If local SL image name differs from default SL image, then update ‘common’ script (inside swarm-learning/bin) and make sure following lines uses local SL image. 
    - slTFImage="${swarmDockerHubAndUser}/sl-tf:${swarmVer}" (or)
    - slPytImage="${swarmDockerHubAndUser}/sl-pyt:${swarmVer}"
4. As usual run the container using run-sl command.

## What happens if a node runs slowly or drops out of the network?

Swarm Learning has a configurable parameter called min_peers, which is the minimum number of nodes essential at each sync step for the model
training to continue. The framework ensures that a node can contribute in a sync step only if it is up to date with the model derived from the
previous sync step.

The scenario of a node running at a slower rate than the others or completely dropping out of the network can lead to two situations:

a.  The number of remaining nodes is greater than or equal to min_peers

b.  The number of remaining nodes is less than min_peers

In the first case where the number of remaining nodes is greater than or equal to min_peers, the training will continue post the sync step with
the remaining nodes. Once the dropped node rejoins the network, it will update its model to the latest one. It will then resume contributing to
model training from the succeeding sync steps.

In case of a slow running node, however, the training will continue with contributions from the remaining nodes. The contributions from the slow
node are merged periodically using a patented logic.

In the case where the number of nodes remaining in the network is less than min_peers, the training will pause at the sync step till the
minimum number is met again. This can occur either when a dropped node rejoins the network or, when a slow node reaches the sync step.

## Can I add new nodes into the network?

Yes. New nodes can be added in the network at any point in the training. Just like a dropped node, a new node will resume model training from the
latest model derived from the last sync step.

## What are the supported merge algorithms? Can I specify a custom merge algorithm?

Swarm Learning uses averaging as the merge algorithm. Currently, users cannot specify the merge algorithm. This will be supported in a later
release.
