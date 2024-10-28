# Nail Disease Classification

This example demonstrates how nail diseases can be classified on the swarm learning platform which helps in early diagnosis of various underlying diseases.  
It also uses pre-trained model(InceptionV3) to leverage the concept of transfer learning

The Swarm training of pre-trained InceptionV3 model using two ML nodes is demonstrated in this example. The ML environment is built manually using docker command and Swarm training is launched without SWCI or SWOP nodes. Here `scripts/bin/run-sl` script is used to spawn each ML node to run InceptionV3 model as a `sidecar` container of each SL node.

This project uses dataset from multiple sources :

* https://www.kaggle.com/datasets/arthitaya/nail-dataset2

* https://www.kaggle.com/datasets/arthitaya/nail-dataset

* https://www.kaggle.com/datasets/reubenindustrustech/nail-dataset

* https://www.kaggle.com/datasets/nuttidalapthanachai/nails-new-test

The data is split into *train* and *test*.
The training data is further split into two parts for testing.

The following image illustrates a cluster setup for this example:

![WPBC Cluster Setup](/docs/User/GUID-4D303DEC-8E71-43F4-BDCB-04B0C1AE79D8-high.png)

* This example uses one SN node. SN1 is the name of the Docker container that runs on host 172.1.1.1.

* Two SL and ML nodes are manually spawned by running the `run-sl` script. Swarm training gets invoked once ML nodes are started. Name of the SL nodes that runs as container are SL1 and SL2. Name of the ML nodes that runs as container are ML1 and ML2.

* SL1 and ML1 pair runs on host 172.1.1.1, whereas SL2 and ML2 pair runs on host 172.2.2.2.

* This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.

## Running the example -

1. On both host-1 and host-2, navigate to `swarm-learning` folder \(that is, parent to examples directory\).

``` bash
cd swarm-learning
```

2. On both host-1 and host-2, create a temporary workspace directory and copy `nail-disease` example.

```bash
mkdir workspace
cp -r examples/contrib/nail-disease workspace/
cp -r examples/utils/gen-cert workspace/nail-disease/
```

3. On both host-1 and host-2, run the `gen-cert` utility to generate certificates for each Swarm component using the command `gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`:

    On host-1:

    ```bash
    ./workspace/nail-disease/gen-cert -e nail-disease -i 1
    ```

    On host-2:

    ```bash
    ./workspace/nail-disease/gen-cert -e nail-disease -i 2
    ```

4. On both host-1 and host-2, share the CA certificates between the hosts as follows:

    On host-1:

    ```bash
    scp host-2:<PATH>workspace/nail-disease/cert/ca/capath/ca-2-cert.pem workspace/nail-disease/cert/ca/capath
    ```

    On host-2:

    ```bash
    scp host-1:<PATH>workspace/nail-disease/cert/ca/capath/ca-1-cert.pem workspace/nail-disease/cert/ca/capath
    ```

5. On both host-1 and host-2, copy Swarm Learning wheel file inside build context and build Docker image for ML that contains environment to run Swarm training of user models.

```bash
cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl workspace/nail-disease/ml-context/
docker build -t user-ml-env-tf2.7.0 workspace/nail-disease/ml-context
```

You may need to specify the correct https_proxy for the docker build if you are behind a firewall. For eg,

```bash
docker build -t user-ml-env-tf2.7.0 --build-arg https_proxy=http://<your-proxy-server-ip>:<port> workspace/nail-disease/ml-context
```

6. Split the `train` data in two equal parts and place them in each hosts. Keep the `test` data same(duplicate) on both the hosts. The path of the data will look like : 
    * app-data/test
    * app-data/train

7. On host-1, Run Swarm Network node

```bash
./scripts/bin/run-sn -d --rm --name=sn1 --host-ip=172.1.1.1 \
--sentinel --sn-api-port=30304 --key=workspace/nail-disease/cert/sn-1-key.pem \
--cert=workspace/nail-disease/cert/sn-1-cert.pem \
--capath=workspace/nail-disease/cert/ca/capath --apls-ip=172.1.1.1
```

   Use the Docker logs command to monitor this Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```

8. On host-1, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate.

```bash
./scripts/bin/run-sl --name=sl1 --host-ip=172.1.1.1 \
--sn-ip=172.1.1.1 --sn-api-port=30304 --sl-fs-port=16000 \
--key=workspace/nail-disease/cert/sl-1-key.pem \
--cert=workspace/nail-disease/cert/sl-1-cert.pem \
--capath=workspace/nail-disease/cert/ca/capath \
--ml-image=user-ml-env-tf2.7.0 --ml-name=ml1 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/nail-disease.py \
--ml-v=workspace/nail-disease/model:/tmp/test/model \
--ml-v=workspace/nail-disease/app-data1:/tmp/test/app-data \
--ml-e DATA_DIR=app-data \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1 \
--apls-port=5814
```

9. On host-2, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate.

```bash
./scripts/bin/run-sl --name=sl2 --host-ip=172.2.2.2 \
--sn-ip=172.1.1.1 --sn-api-port=30304 \
--sl-fs-port=17000 --key=workspace/nail-disease/cert/sl-2-key.pem \
--cert=workspace/nail-disease/cert/sl-2-cert.pem \
--capath=workspace/nail-disease/cert/ca/capath \
--ml-image=user-ml-env-tf2.7.0 --ml-name=ml2 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/nail-disease.py \
--ml-v=workspace/nail-disease/model:/tmp/test/model \
--ml-v=workspace/nail-disease/app-data2:/tmp/test/app-data \
--ml-e DATA_DIR=app-data \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1 \
--apls-port=5814
```

10. On both host-1 and host-2, Two node of Swarm training are started. User can monitor the Docker logs of ML nodes \(ML1 and ML2 containers\) for Swarm training on both host-1 and host-2. Training ends with the following log message:

```
SwarmCallback : INFO : Saved the trained model - model/saved_models/nail-disease.h5
```

   Final Swarm model is saved inside the model directory that is `workspace/nail-disease/model/saved_models` directory on both the hosts. SL and ML nodes exit but it is not removed after the Swarm training.

11. On both host-1 and host-2, To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs and delete the workspace directory.