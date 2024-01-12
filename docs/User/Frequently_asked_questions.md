# <a name="GUID-0F5ACBE9-AC3F-481E-902E-AFD628B6662E"/> Frequently asked questions

## Generic

### <a name="GUID-424453EE-CB1A-4482-8EF8-3A0CA077F67B"/> What is Swarm Learning?

Swarm Learning is a decentralized, privacy-preserving Machine Learning framework. This framework utilizes the computing power at, or near, the distributed data sources to run the Machine Learning algorithms that train the models. It uses the security of a blockchain platform to share learnings with peers in a safe and secure manner.

### <a name="GUID-1811327E-194E-433C-8D7D-2EEF1FB2778C"/> What are the components of Swarm Learning?

Swarm Learning has 4 types of components that form a network. They are Swarm Learning nodes, Swarm Network nodes, SWCI nodes, and SWOP nodes.

### <a name="GUID-BA02577F-B3EF-4D64-8C75-90E6A674CAA9"/> What is the License server node?

The License server \(APLS\) node is a special node running the HPE AutoPass license server. It is responsible for validating the licenses of the Swarm Learning framework. There is typically one instance of this node running in the Swarm.

### How do we resolve license related issues?
User can raise the support ticket through this URL: https://myenterpriselicense.hpe.com/cwp-ui/contact-us.

### <a name="SECTION_TQT_LFS_HSB"/> How do you run Swarm Learning on GPU?

The SL, SN, SWOP, and SWCI nodes utilize only the CPUs. However, the user ML nodes can run on GPUs by using the GPU version of your ML platform \(Keras/PyTorch\) and following the GPU specific instructions of your ML platform. For more information on [starting SL and ML nodes](/docs/Install/Running_Swarm_Learning_using_CLI.md).

For Nvidia GPUS, you can set `--gpus` under `usrcontaineropts` section of the SWOP profile. For more information, see [https://docs.docker.com/config/containers/resource_constraints/#gpu](https://docs.docker.com/config/containers/resource_constraints/#gpu).
If you are starting the SL and ML nodes by using the `run-sl` script, then the GPUs can be specified as appropriate environment variables by using `--ml-e` option.

For AMD GPUs, you can set `usercontaineropts` and/or `usrenvvars` section of the SWOP profile. For more information, see [SWOP profile schema](/docs/User/SWOP_profile_schema.md).
If you are starting the SL and ML nodes by using the `run-sl` script, then the GPUs can be specified as appropriate parameters as specified in the [User machine learning container parameters](/docs/Install/Running_Swarm_Learning_using_CLI.md#-user-machine-learning-container-parameters). For more information on User machine learning container parameters, see [User machine learning container parameters](/docs/Install/Running_Swarm_Learning_using_CLI.md#-user-machine-learning-container-parameters).

### <a name="SECTION_F32_J1Y_CTB"/> What all GPUs are supported ?

Currently SWOP framework is designed to start ML nodes on Nvidia GPUs and AMD GPUs. In the future other GPUs may be supported.

### How can you determine if AMD GPUs are allocated for local training?

You can check for Cuda/Gpu availability from your application code.

**PyTorch:**<br>
torch.cuda.is_available()<br>
https://pytorch.org/docs/stable/generated/torch.cuda.is_available.html

**In TensorFlow:**<br>
tensorflow.test.is_gpu_available()<br>
https://www.tensorflow.org/api_docs/python/tf/test/is_gpu_available

### What are the additional steps to be followed to enable GPU access for local training?

The additional steps to enable GPUs for local training are as follows:<br> </br>
    1. Build the user container to enable GPU access in it. Use base image as tensorflow-gpu or Nvidia image with PyTorch
    installed on it as applicable to ML platform.<br> </br>
    2. Update SWOP profile `usrcontaineropts` (or) provide run-scripts options as applicable to Nvidia or AMD.<br> </br>
    3. Create application code to access GPU.

### <a name="SECTION_NHW_PFS_HSB"/> Can you have heterogeneous ML nodes, with some running on CPU and others on GPU?

Yes.

Each ML node by default runs on CPU. If you want to run on GPUs, specify it in the `usrcontaineropts` section in the SWOP profile.

### <a name="SECTION_LXB_TLD_VSB"/> Can you run multiple concurrent Model Trainings in the same Swarm Network?

Yes, it is supported only in the enterprise version. You can even run one training session using Keras and another using PyTorch.

You need different training contracts specified in the ML programs via `Swarmcallback` API.

If you are using SWOP to launch concurrent training, you need to have separate SWOP nodes each watching a different taskrunner, which is specified in their SWOP profiles.

Concurrent model training uses the same Swarm SN network across different model trainings, sharing the blockchain.

If you are using SLM-UI, then you need to create different projects for each model training. You must create a new
taskrunner and training contract in SLM-UI and use the same in the SWOP profile and ML program respectively, for each
project.

You need to spawn the SWOP nodes and execute the RUN-SWARM type task using the respective taskrunners of each
project.

### <a name="SECTION_HH5_KNP_NSB"/> What is the IP address used in the run scripts?

By default, Swarm Learning framework uses a Docker bridge network. For improved isolation, users can even use a user-defined (custom) bridge network.

The `--host-ip` and `slhostip` IP addresses in the run scripts and the SWOP profile are the "IP addresses" of the host machine, where the respective containers are running. If user-defined docker bridge network is used, one can even use the FQDN of the host system.

While using the user-defined bridge network, the options `--ip` for run-scripts and `ip` field of `slnetworkopts` in SWOP profile are the IP addresses of the container (not host IP). This case is specific to the reverse proxy examples or scenarios where user wants to use fixed IP address for containers.

### <a name="SECTION_RVM_DGS_HSB"/> Where are the log files?

The system log files are the docker logs. By default, the docker containers that run the SN, SL, ML, SWOP, and SWCI nodes are not removed after they exit. Log output produced by these containers can be retrieved using the docker logs command.

For a SL node, a subset of the log output is stored with the name `<program-name>_sw.log`, in the model directory.

The ML program can produce additional log output. To do so, it should be modified to write this output to files in the model directory.

### <a name="SECTION_IZQ_TFS_HSB"/> What network ports does Swarm Learning use? Can they be customized?

Each SN node requires two network ports for incoming connections from other SN, SL, SWCI, and SWOP nodes.

-   One SN to SN peer to peer communication port - is meant for peer-to-peer communication using the underlying blockchain platform’s protocols. By default, port 30303 is used.

-   One SN API server port - is meant for running a REST-based API server on each SN node. By default, port 30304 is used.


Each SL node requires one network port for incoming connections from other SL nodes.

-   A SL file server port - is meant for running a file server on each SL node. By default, port 30305 is used.


Each License Server node requires one network port for incoming connections from other nodes.

-   A License Server API server port - is meant for running a REST-based API server. By default, port 5814 is used.


\(Optional\) A SWCI API server port - is used by the SWCI node to run a REST-based API service. By default, port 30306 is used.

The port numbers can be customized by using the corresponding `swarm-learning/bin/run-sn`, `swarm-learning/bin/run-sl`, and `swarm-learning/bin/run-swci` scripts that are supplied with the Swarm Learning package. Use the `–help` option on the above scripts to get exact details.

For configuring the license server API port, see *AutoPass License Server User Guide*.

### <a name="SECTION_ICX_GGS_HSB"/> Do you need sudo/root privileges to run Swarm Learning?

`sudo` is not required to launch the container, if docker is configured to run as a non-root user. Refer Manage Docker as a non-root user If docker is not configured to run as a non-root user, the scripts will automatically prefix docker commands with `sudo`. If the user does not have `sudo` privileges, an error will result.

<blockquote>
  
NOTE: Effective user inside the docker container should be root.

</blockquote>

### <a name="SECTION_SVG_MGS_HSB"/> How do you uninstall Swarm learning?

Use the docker log command to save any container log output that you want to preserve. Use a directory outside the Swarm Learning installation directory. Also, consider cleaning the model directories by removing unnecessary files and sub-directories.

Use the `swarm-learning/bin/uninstall` script to uninstall the Swarm Learning package. This script does not accept any command line parameters. It should run on every node where Swarm Learning package is installed. While running, it stops all Swarm Learning components that are running on that host, removes the docker container images, and deletes the Swarm Learning installation directory.

## Swarm Network (SN) node

### <a name="SECTION_O5D_S2S_HSB"/> What is the Sentinel node?

The Sentinel node is a special Swarm Network node. It is responsible for initializing the blockchain network and deploying the smart contracts on the blockchain. For this reason, the Sentinel node should be the very first Swarm Network node that is started in the Swarm Learning framework. Once the blockchain network has been initialized, there is no difference between the functioning of the Sentinel node and that of the other Swarm Network nodes.

### <a name="SECTION_ZKR_V2S_HSB"/> How do you know if Swarm Network node started successfully?

Look for following message after executing `run-sn` command to confirm successful starting of Swarm Network node. It might take a few minutes before this message appears.

`swarm.blCnt : INFO : Starting SWARM-API-SERVER on port :30304` \(30304 is the default port\).

This message does not show up if APLS server is not configured correctly.


### <a name="GUID-902F3923-84A9-4572-96D6-CDDD081D1544"/> What are the possible reasons for "unable to contact API server"?

A swarm container could be unable to reach an SN node for several reasons.

1.  SN is not running. To confirm, check the Docker running state of the SN container.

2.  SN node can be reached via SN container FQDN only in a single host custom bridge network. But for all other scenarios, IP address of the host machine must be used. Ensure the correctness of `--sn-ip` and `--sn-api-port` parameters.

3.  Ensure that SN-API-port is allowed in your firewall settings. User can check this by running `sudo ufw status`. If the SN-API-port is not in the list, then add it by using `sudo ufw allow <SN-API-port>`. The same configuration is applicable for all other Swarm ports. Ignore this step if the `ufw status` is inactive, as this state allows all ports.

4.  If the certificates get expired, then the other swarm components including non-sentinel SN are not able to reach SN. User can check the expiry date of their certificates and update them accordingly.


### <a name="SECTION_L5P_RCK_1TB"/> How many SLs can connect with a SN?

It depends on several factors like, the available system resources, the ML algorithm complexity, how often it does parameter merging and so on.

On a Proliant XL Gen 9 system with 8 Xeon CPUs and 32 GB memory HPE has tested and found up to 16 SLs could connect with 1 SN, when running a MNIST training with 100 epochs.

HPE recommends starting up to 4 SLs to 1 SN and scale it up slowly if needed.

### <a name="SECTION_VH1_YND_VSB"/> When you start SWCI, you do not specify any IP/name for SN. How does it know which SN to connect to?

SWCI is designed to work with several swarm networks at once. Therefore, you can create a context and switch to that context to execute commands. Each context identifies which SN the SWCI must connect to.

### <a name="SECTION_IWC_RGS_HSB"/> Why is blockchain required? Can you use a different blockchain network?

Swarm Learning uses a blockchain network primarily to provide a consistent system state to all the nodes without requiring any central coordinator.

The current implementation runs an open-source version of Ethereum but, more platforms might be added in the future. At the time of initialization, the framework spawns its own blockchain network with a custom set of parameter values. Hence it cannot be replaced with any other blockchain network. This applies even when the blockchain platform is a supported one.

## Where is the blockchain stored on SN container?

By default, blockchain is stored in the `/platform/swarm/SMLNODE` path inside SN containers. Blockchain is not preserved by default. To preserve it, user have to mount `/platform/swarm/SMLNODE` on a persistent volume on the host while starting SN. For more information, see `Starting Sentinel node` section in `HPE Swarm Learning Installation and Configuration Guide`.

## <a name="SECTION_DX2_VGS_HSB"/> What are the supported machine learning platforms?

Swarm Learning supports Python3 based Machine Learning models that uses PyTorch and Keras \(based on TensorFlow 2\).

### <a name="SECTION_WGJ_WGS_HSB"/> What models work with swarm learning?

Currently, Swarm Learning works only with **parametric** machine learning models. For example, NN, CNN, RNN, LSTM, and many more. Its also supports Transfer Learning \(models which includes mix of trainable and non-trainable parameters\).

Support for other ML models is part of Swarm roadmap.

### <a name="SECTION_JNJ_YGS_HSB"/> What are the supported Python packages in ML node?

Any Python package can be used to build the ML container.

If SWOP framework is used, packages must be specified in the build-task definition file.

### <a name="GUID-0B47942A-ACC0-4A7C-A9D6-F838BDAB7201"/> What is the guidance on minPeers in the application vs "WITH PEERS in the assign run task"?

`minPeers` specifies the minimum number of ML peers \(quorum\) that must be available \(and able to communicate to each other\) to continue the Swarm training. Otherwise, the Swarm training gets blocked indefinitely.

`WITH peersNeeded` in the `assign task` is used to start the number of SL, ML pairs using the SWOP framework. Also, this count is used to decide the overall status of the task.

`WITH peersNeeded` in the `assign task` must be equal to or greater than the `minPeers`. It can be closer to the total number of ML peers in the Swarm training.

### <a name="SECTION_PXX_LHS_HSB"/> What happens if a node runs slowly or drops out of the network?

Swarm Learning has a configurable parameter called `minPeers`, which is the minimum number of nodes essential at each sync step for the model training to continue. The framework ensures that a node can contribute in a sync step only if it is up to date with the model derived from the previous sync step.

The scenario of a node running at a slower rate than the others or completely dropping out of the network can lead to two situations:

-   The number of remaining nodes is greater than or equal to `min_peers`.

-   The number of remaining nodes is less than `min_peers`.


In the first case where the number of remaining nodes is greater than or equal to min_peers, the training will continue post the sync step with the remaining nodes. Once the dropped node rejoins the network, it will update its model to the latest one. It will then resume contributing to model training from the succeeding sync steps.

In case of a slow running node, however, the training will continue with contributions from the remaining nodes. The contributions from the slow node are merged periodically using a patented logic.

In the case where the number of nodes remaining in the network is less than min_peers, the training will pause at the sync step till the minimum number is met again. This can occur either when a dropped node rejoins the network or, when a slow node reaches the sync step.

### <a name="SECTION_UFF_RHS_HSB"/> Can I add new nodes into the network?

Yes. New nodes can be added in the network at any point in the training. Just like a dropped node, a new node will resume model training from the latest model derived from the last sync step.

### <a name="SECTION_FW4_SHS_HSB"/> What are the supported merge methods? Can I specify a custom merge method?

Swarm Learning uses weighted mean as the default merge method. User can specify one of the merge methods such as
mean, coordinate wise median, and geometric wise median. Currently, users cannot specify the merge algorithm. This will be supported in a later release.

### How to choose the suitable merge method among mean, coordinate median and geometric median methods?
User must consider this merge method as one of the Swarm hyper parameters and expected to experiment with it. Mean is
the default merge method. It works well for most of the use cases. HPE recommends you to try coordinate median and
geometric median methods under the following circumstances.<br>
• The coordinate or geometric median merge methods are recommended for scenarios where model is relatively
complex and takes longer duration to run each epoch. For such complex models, the rate at which the model
converges over epochs is better in median-based merge methods. If user has the flexibility to run ML model for higher
number of epochs, then all the merge methods may give similar results.<br>
• The strong bias nature of the datasets tends to have non-uniform weights and biases in the intermediate models
across ML nodes. For such biased datasets, coordinate median and geometric median methods are known to perform
better than the mean method.<br>
For more information, see `Merge Methods in Swarm Learning Whitepaper`.

### Before enabling Swarm Learning, how to confirm the standalone user application has no issues and runs?

Run the user container with `SWARM_LOOPBACK` set to `TRUE`, this bypasses Swarm Learning to help you quickly develop, integrate, and test your model code with Swarm Learning package. If your code runs to completion and saves the local model it would indicate that the ML application may not have any issues.

If `SWARM_LOOPBACK` is set to TRUE, all Swarm functionality is bypassed, except parameter validation.

This can help you to verify and test integration of the model code with Swarm without spawning any Swarm Learning
containers.

### How to run user container as non-root?

By default, when user ML container is run through SWOP or using the `run-sl` script, the user ML container is run with current user's UID and GID of the host machine. If the current user on the host is non-root, the user container also runs as non-root.

### <a name="SECTION_X3S_HLL_XWB"/> How to mount data/example/file to ML container if “Swarm install directory" or "source file path” is different across hosts?

SWOP profile supports mounts with private data. If the installation path or any file path is different across hosts, then `privatedata` field of SWOP profile can be used to mount. User can specify different values for`privatedata` field specific to each ML container. Mount target path is in the `PrivateContent` field in the run task definition. It is the same for all ML containers, and hence ML applications can access these files in the same manner.

### <a name="SECTION_R2V_KGS_HSB"/> Can each Swarm Learning node run a different ML program and parameters?

No. The program and parameters should be the same across all the Swarm Learning nodes.

## Swarm management

### What are the supported SWCI commands?

SWCI has a built-in inline help, that lists all supported commands and further one can see help for each command.

For Example,

```
SWCI:0 > HELP
    ASSIGN TASK
    CD
    CREATE CONTEXT
    CREATE CONTRACT
    …

SWCI:1 > HELP CREATE CONTRACT
    CREATE CONTRACT <TrainingContractName : string>
Registers the specified SL Training Contract into the Swarm Learning Network.

```
### How to debug error with command “ASSIGN TASK TO TASKRUNNER”? 

Use SWCI command “GET TASKRUNNER STATUS” to know the overall status of the TASK execution.

One can also use “GET TASKRUNNER PEER STATUS” to display the status for the individual SWOP PEERs that are listening on this TASKRUNNER.

-   For RUN_SWARM task type, the status summary reports SWOP node UID, Number of SL PEERs this SWOP has spawned, and list of all SL node information \(UID, Status, Description\). For all other types of tasks, the status summary reports SWOP node status \(UID, Status, Description\).
-   If there are failed PEERs, using its node UID, one can identify the container name/id from ‘LIST NODES’ command. With container name/id, user can debug the error with docker logs command.

## Swarm Learning Management UI (SLM-UI)

### What is a concept of SLM-UI project?
Project in SLM-UI is a logical representation of a particular Swarm training. Projects help to view deployment topology and monitor the progress for the given Swarm training. They define what all Swarm nodes (and associated host nodes) a training will run, the model being used, the x.509 certificates, SWOP and Task yaml files for a particular training. Multiple Projects can be defined in a single instance of SLM-UI.

Project artifacts are created under the `swarm-learning/slm-ui/projects/<project number>` automatically once the project is saved.

### How can user monitor training progress?
In Project Nodes under Projects tab, the system displays all running swarm nodes associated with the project, loss, model metric (for example, accuracy) and overall training progress for each SL-ML node pair. User can hover over the mouse on progress bar to view the total number of epochs and the total number of completed epochs.

### When do we need to create multiple task runners and contracts (Training contracts)?
If you are running concurrent Swarm training, you need to create multiple task runners and contracts. If you are running a single training, the default task runner and contract would be good enough.

### How to start SLM-UI manually?
1. Run `<swarm-learning>/slm-ui/scripts/run-postgres -pw" supersecretpassword"`.<br>
(`supersecretpassword` is a default database password. User can change this default database password using
external tools like pgAdmin).
2. Then, run `<swarm-learning>/slm-ui/scripts/run-slm-ui -pw" supersecretpassword"`.

### What are the limitations of SLM-UI?
Currently, SLM-UI works if you use Docker container runtime. SLM-UI does not work if you are running Podman container
runtime on the host.<br>
If you are using reverse proxy setup, you cannot use SLM-UI.<br>
If you are using SPIRE based certificates, you cannot use SLM-UI.

