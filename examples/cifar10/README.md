CIFAR-10
=========

This example runs CIFAR-10 [1] on the Swarm Learning platform. It uses Tensorflow as the backend.

The code for this example has been modified to run on a Swarm Learning platform.

This example uses cifar10 dataset distributed along with tensorflow package. The ML program, after conversion to Swarm Learning, is in `swarm-learning/examples/cifar10/model` and is called `cifar10.py`. It contains a tiny ML model for the purpose of showing steps of converting ML code to Swarm Learning. 

This example shows the Swarm training of Keras based CIFAR-10 model using two Machine Learning (ML) nodes. It also shows how ML environment can be built manually using run-sl command and how Swarm training can be launched without Swarm Command Interface (SWCI) or Swarm Operator (SWOP) nodes. Here `scripts/bin/run-sl` script is used to spawn each ML node to run CIFAR-10 model as a "sidecar" container of each Swarm Learning (SL) node.



## Cluster Setup

The cluster setup for this example uses 2 hosts, as shown in the figure below:  
- host-1: 172.1.1.1  
- host-2: 172.2.2.2  

|![cifar-10-cluster-setup](../figs/cifar-10-cluster-setup.png)|
|:--:|
|<b>Figure 1: Cluster setup for the CIFAR-10 example</b>|

1. This example uses one Swarm Network (SN) node. **sn1** is the name of the docker container that runs on host 172.1.1.1.  
2. Two Swarm Learning (SL) and two Machine Learning (ML) nodes are manually spawned by running the `run-sl` script. Swarm training gets invoked once ML nodes are started. Name of the SL nodes that runs as container are **sl1** and **sl2**. Name of the ML nodes that runs as container are **ml1** and **ml2**.  
3. sl1 and ml1 pair runs on host 172.1.1.1, whereas sl2 and ml2 pair runs on host 172.2.2.2.  
4. Example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.



## Running the CIFAR-10 example

1. *On both host-1 and host-2*:  
   cd to `swarm-learning` folder (i.e. parent to examples directory)
   ```
   cd swarm-learning
   ```

2. *On both host-1 and host-2*:  
   Create a temporary `workspace` directory and copy `cifar10` example and `gen-cert` utility there.
   ```
   mkdir workspace
   cp -r examples/cifar10 workspace/
   cp -r examples/utils/gen-cert workspace/cifar10/
   ```

3. *On both host-1 and host-2*:  
   Run the `gen-cert` utility to generate certificates for each Swarm component using the command: `gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`  
   *On host-1*:  
   ```
   ./workspace/cifar10/gen-cert -e cifar10 -i 1
   ```  
   *On host-2*:  
   ```
   ./workspace/cifar10/gen-cert -e cifar10 -i 2
   ```

4. *On both host-1 and host-2*:  
   Share the CA certificates between the hosts as follows –  
   *On host-1*:  
   ```
   scp host-2:<PATH>workspace/cifar10/cert/ca/capath/ca-2-cert.pem workspace/cifar10/cert/ca/capath
   ```  
   *On host-2*:  
   ```
   scp host-1:<PATH>workspace/cifar10/cert/ca/capath/ca-1-cert.pem workspace/cifar10/cert/ca/capath
   ```

5. *On both host-1 and host-2*:  
   Copy SwarmLearning wheel file inside build context and build docker image for ML that contains environment to run Swarm training of user models.  
   ```
   cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl workspace/cifar10/ml-context/
   docker build -t user-ml-env-tf2.7.0 workspace/cifar10/ml-context
   ```
6. *On both host-1 and host-2*: 
   Declare and assign values to the variables like APLS_IP, SN_IP, HOST_IP and ports. The values mentioned here are for understanding purpose only. Use appropriate values as per your swarm network.
    ```
    APLS_IP=172.1.1.1
    SN_IP=172.1.1.1
    HOST_1_IP=172.1.1.1
    HOST_2_IP=172.2.2.2
    SN_API_PORT=30304
    SN_P2P_PORT=30303
    SL_1_FS_PORT=16000
    SL_2_FS_PORT=17000
    ```
   
8. *On host-1*:  
   Run Swarm Network node (sentinel node)
   ```  
   ./scripts/bin/run-sn -d --rm --name=sn1 --host-ip=${HOST_1_IP} --sentinel --sn-api-port=${SN_API_PORT}      \
   --key=workspace/cifar10/cert/sn-1-key.pem --cert=workspace/cifar10/cert/sn-1-cert.pem                       \
   --capath=workspace/cifar10/cert/ca/capath --apls-ip=${APLS_IP}
   ```
   Use the docker logs command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:  
   `swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304`

8. *On host-1*:  
   Run Swarm Learning node and Machine Learning node (as a "sidecar"): Set the proxy server as appropriate, as the ML program needs to download the CIFAR dataset.
   ```
   ./scripts/bin/run-sl -d --name=sl1 --host-ip=${HOST_1_IP} --sn-ip=${SN_IP} --sn-api-port=${SN_API_PORT}            \
   --sl-fs-port=${SL_1_FS_PORT} --key=workspace/cifar10/cert/sl-1-key.pem --cert=workspace/cifar10/cert/sl-1-cert.pem   \
   --capath=workspace/cifar10/cert/ca/capath --ml-image=user-ml-env-tf2.7.0 --ml-name=ml1                               \
   --ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cifar10.py                                                   \
   --ml-v=workspace/cifar10/model:/tmp/test/model --ml-e MODEL_DIR=model --ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2         \
   --ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> --apls-ip=${APLS_IP}
   ```

9. *On host-2*:  
   Run Swarm Learning node and Machine Learning node (as a "sidecar"): Set the proxy server as appropriate, as the ML program needs to download the CIFAR dataset.
   ```
   ./scripts/bin/run-sl -d --name=sl2 --host-ip=${HOST_2_IP} --sn-ip=${SN_IP} --sn-api-port=${SN_API_PORT}            \
   --sl-fs-port=${SL_2_FS_PORT} --key=workspace/cifar10/cert/sl-2-key.pem --cert=workspace/cifar10/cert/sl-2-cert.pem   \
   --capath=workspace/cifar10/cert/ca/capath --ml-image=user-ml-env-tf2.7.0 --ml-name=ml2                               \
   --ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cifar10.py                                                   \
   --ml-v=workspace/cifar10/model:/tmp/test/model --ml-e MODEL_DIR=model --ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2         \
   --ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> --apls-ip=${APLS_IP}
   ```

10.	*On both host-1 and host-2*:  
   Two node Swarm training is started. User can open a new terminal on both host-1 and host-2 and monitor the docker logs of ML nodes (ml1 and ml2 containers) for Swarm training. Swarm training will end with the following log message at the end –  
   `SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.`  
   Final Swarm model will be saved inside the model directory i.e. `workspace/cifar10/model/saved_models` directory on both the hosts. SL and ML nodes will exit but will not be removed after Swarm training.

11. *On both host-1 and host-2*:  
    To clean-up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. ML container needs to be removed manually using `docker rm` command. If needed, take backup of the container logs. Finally delete the `workspace` directory.



## References
[1] V.N. a. G. H. Alex Krizhevsky, "CIFAR-10 and CIFAR-100 datasets," [Online]. Available: https://www.cs.toronto.edu/~kriz/cifar.html
