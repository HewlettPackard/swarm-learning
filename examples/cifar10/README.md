# <a name="GUID-E12971F4-0E2C-49B9-B417-9D62734773FA"/> CIFAR-10

This example runs CIFAR-10 [1](#) on the Swarm Learning platform. It uses Tensorflow as the backend.

The code for this example has been modified to run on a Swarm Learning platform.

This example uses CIFAR-10 dataset distributed along with TensorFlow package. The ML program, after conversion to Swarm Learning, is in `swarm-learning/examples/cifar10/model` and is called `cifar10.py`. It contains a tiny ML model for the purpose of showing steps of converting ML code to Swarm Learning.

This example shows the Swarm training of Keras based CIFAR-10 model using two ML nodes. It also shows how ML environment can be built manually using docker command and how Swarm training can be launched without SWCI or SWOP nodes. Here `scripts/bin/run-sl` script is used to spawn each ML node to run CIFAR-10 model as a `sidecar` container of each SL node.

The following image illustrates a cluster setup for the CIFAR-10 example:

![CIFAR-10 Cluster Setup](/docs/User/GUID-4D303DEC-8E71-43F4-BDCB-04B0C1AE79D8-high.png)

-   This example uses one SN node. SN1 is the name of the Docker container that runs on host 172.1.1.1.

-   Two SL and ML nodes are manually spawned by running the `run-sl` script. Swarm training gets invoked once ML nodes are started. Name of the SL nodes that runs as container are SL1 and SL2. Name of the ML nodes that runs as container are ML1 and ML2.

-   SL1 and ML1 pair runs on host 172.1.1.1, whereas SL2 and ML2 pair runs on host 172.2.2.2.

-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## <a name="SECTION_UN3_VTV_NSB"/> Running the CIFAR-10 example

1.  On both host-1 and host-2, navigate to `swarm-learning` folder \(that is, parent to examples directory\).

```
cd swarm-learning
```

2.  On both host-1 and host-2, create a temporary workspace directory and copy `cifar10` example.

```
mkdir workspace
cp -r examples/cifar10 workspace/
cp -r examples/utils/gen-cert workspace/cifar10/
```

3.  On both host-1 and host-2, run the `gen-cert` utility to generate certificates for each Swarm component using the command `gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`:

    On host-1:

    ```
    ./workspace/cifar10/gen-cert -e cifar10 -i 1
    ```

    On host-2:

    ```
    ./workspace/cifar10/gen-cert -e cifar10 -i 2
    ```

4.  On both host-1 and host-2, share the CA certificates between the hosts as follows:

    On host-1:

    ```
    scp host-2:<PATH>workspace/cifar10/cert/ca/capath/ca-2-cert.pem workspace/cifar10/cert/ca/capath
    
    ```

    On host-2:

    ```
    scp host-1:<PATH>workspace/cifar10/cert/ca/capath/ca-1-cert.pem workspace/cifar10/cert/ca/capath
    
    ```

5.  On both host-1 and host-2, copy Swarm Learning wheel file inside build context and build Docker image for ML that contains environment to run Swarm training of user models.

```
cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl workspace/cifar10/ml-context/
docker build -t user-ml-env-tf2.7.0 workspace/cifar10/ml-context
```
You may need to specify the correct https_proxy for the docker build if you are behind a firewall. For eg,
``` 
docker build -t user-ml-env-tf2.7.0 --build-arg https_proxy=http://<your-proxy-server-ip>:<port> workspace/cifar10/ml-context
```

6.  On host-1, Run Swarm Network node \(sentinel node\)

```
./scripts/bin/run-sn -d --rm --name=sn1 --host-ip=172.1.1.1 \
--sentinel --sn-api-port=30304 --key=workspace/cifar10/cert/sn-1-key.pem \
--cert=workspace/cifar10/cert/sn-1-cert.pem \
--capath=workspace/cifar10/cert/ca/capath --apls-ip=172.1.1.1
```

   Use the Docker logs command to monitor this Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```

7.  On host-1, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate, as the ML program needs to download the CIFAR dataset.

```
./scripts/bin/run-sl --name=sl1 --host-ip=172.1.1.1 \
--sn-ip=172.1.1.1 --sn-api-port=30304 --sl-fs-port=16000 \
--key=workspace/cifar10/cert/sl-1-key.pem \
--cert=workspace/cifar10/cert/sl-1-cert.pem \
--capath=workspace/cifar10/cert/ca/capath --ml-it \
--ml-image=user-ml-env-tf2.7.0 --ml-name=ml1 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cifar10.py \
--ml-v=workspace/cifar10/model:/tmp/test/model \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1
```

8.  On host-2, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate, as the ML program needs to download the CIFAR dataset

```
./scripts/bin/run-sl --name=sl2 --host-ip=172.2.2.2 \
--sn-ip=172.1.1.1 --sn-api-port=30304 \
--sl-fs-port=17000 --key=workspace/cifar10/cert/sl-2-key.pem \
--cert=workspace/cifar10/cert/sl-2-cert.pem \
--capath=workspace/cifar10/cert/ca/capath \
--ml-it --ml-image=user-ml-env-tf2.7.0 --ml-name=ml2 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cifar10.py \
--ml-v=workspace/cifar10/model:/tmp/test/model \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1
```

9.  On both host-1 and host-2, Two node of Swarm training are started. User can monitor the Docker logs of ML nodes \(ML1 and ML2 containers\) for Swarm training on both host-1 and host-2. Training ends with the following log message:

```
SwarmCallback : INFO : Saved the trained model - model/saved_models/cifar10.h5
```

   Final Swarm model is saved inside the model directory that is `workspace/cifar10/model/saved_models` directory on both the hosts. SL and ML nodes exit but it is not removed after the Swarm training.

10. On both host-1 and host-2, To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs and delete the workspace directory.


[1](#) [https://www.cs.toronto.edu/%7Ekriz/cifar.html](#)

 

