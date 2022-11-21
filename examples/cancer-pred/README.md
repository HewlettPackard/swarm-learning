# Cancer Prediction

This example demonstrates how a cancer prediction model built over the Wisconsin Prognostic Breast Cancer Dataset [WPBC](https://archive.ics.uci.edu/ml/datasets/breast+cancer+wisconsin+(Prognostic)) would run and perform on the swarm learning platform.
The above mentioned link is of the official data repository. 

To download the dataset, follow the below steps:  

Click on “Download” in this link to the dataset - (https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data)

After clicking on  “Download” button, Extract the “archive.zip” present wherever it is saved (in this context - “/Downloads”)  
Run the command by appropriately replacing “/Downloads” with the saved location of the “data.csv” file -   
```
cp /Downloads/data.csv  examples/cancer-pred/ml-context/  
```

Replace the dataset-file_path in the cancer-pred.py file with the path of data.csv  
```
df=pd.read_csv(<dataset-file_path>)  
```

The following image illustrates a cluster setup for this example:

![WPBC Cluster Setup](/docs/User/GUID-4D303DEC-8E71-43F4-BDCB-04B0C1AE79D8-high.png)
-   This example uses one SN node. SN1 is the name of the Docker container that runs on host 172.1.1.1.
-   Two SL and ML nodes are manually spawned by running the `run-sl` script. Swarm training gets invoked once ML nodes are started. Name of the SL nodes that runs as container are SL1 and SL2. Name of the ML nodes that runs as container are ML1 and ML2.
-   SL1 and ML1 pair runs on host 172.1.1.1, whereas SL2 and ML2 pair runs on host 172.2.2.2.
-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.

## Running the WPBC example -

1.  On both host-1 and host-2, navigate to `swarm-learning` folder \(that is, parent to examples directory\).

```
cd swarm-learning
```

2.  On both host-1 and host-2, create a temporary workspace directory and copy `cancer-pred` example.

```
mkdir workspace
cp -r examples/cancer-pred workspace/
cp -r examples/utils/gen-cert workspace/cancer-pred/
```

3.  On both host-1 and host-2, run the `gen-cert` utility to generate certificates for each Swarm component using the command `gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`:

    On host-1:

    ```
    ./workspace/cancer-pred/gen-cert -e cancer-pred -i 1
    ```

    On host-2:

    ```
    ./workspace/cancer-pred/gen-cert -e cancer-pred -i 2
    ```

4.  On both host-1 and host-2, share the CA certificates between the hosts as follows:

    On host-1:

    ```
    scp host-2:<PATH>workspace/cancer-pred/cert/ca/capath/ca-2-cert.pem workspace/cancer-pred/cert/ca/capath
    ```

    On host-2:

    ```
    scp host-1:<PATH>workspace/cancer-pred/cert/ca/capath/ca-1-cert.pem workspace/cancer-pred/cert/ca/capath
    ```

5.  On both host-1 and host-2, copy Swarm Learning wheel file inside build context and build Docker image for ML that contains environment to run Swarm training of user models.

```
cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl workspace/cancer-pred/ml-context/
docker build -t user-ml-env-tf2.7.0 workspace/cancer-pred/ml-context
```
You may need to specify the correct https_proxy for the docker build if you are behind a firewall. For eg,
``` 
docker build -t user-ml-env-tf2.7.0 --build-arg https_proxy=http://<your-proxy-server-ip>:<port> workspace/cancer-pred/ml-context
```

6.  On host-1, Run Swarm Network node \(sentinel node\)

```
./scripts/bin/run-sn -d --rm --name=sn1 --host-ip=172.1.1.1 \
--sentinel --sn-api-port=30304 --key=workspace/cancer-pred/cert/sn-1-key.pem \
--cert=workspace/cancer-pred/cert/sn-1-cert.pem \
--capath=workspace/cancer-pred/cert/ca/capath --apls-ip=172.1.1.1
```

   Use the Docker logs command to monitor this Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```

7.  On host-1, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate.

```
./scripts/bin/run-sl --name=sl1 --host-ip=172.1.1.1 \
--sn-ip=172.1.1.1 --sn-api-port=30304 --sl-fs-port=16000 \
--key=workspace/cancer-pred/cert/sl-1-key.pem \
--cert=workspace/cancer-pred/cert/sl-1-cert.pem \
--capath=workspace/cancer-pred/cert/ca/capath --ml-it \
--ml-image=user-ml-env-tf2.7.0 --ml-name=ml1 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cancer-pred.py \
--ml-v=workspace/cancer-pred/model:/tmp/test/model \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1
```

8.  On host-2, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate.

```
./scripts/bin/run-sl --name=sl2 --host-ip=172.2.2.2 \
--sn-ip=172.1.1.1 --sn-api-port=30304 \
--sl-fs-port=17000 --key=workspace/cancer-pred/cert/sl-2-key.pem \
--cert=workspace/cancer-pred/cert/sl-2-cert.pem \
--capath=workspace/cancer-pred/cert/ca/capath \
--ml-it --ml-image=user-ml-env-tf2.7.0 --ml-name=ml2 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cancer-pred.py \
--ml-v=workspace/cancer-pred/model:/tmp/test/model \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1
```

9.  On both host-1 and host-2, Two node of Swarm training are started. User can monitor the Docker logs of ML nodes \(ML1 and ML2 containers\) for Swarm training on both host-1 and host-2. Training ends with the following log message:

```
SwarmCallback : INFO : Saved the trained model - model/saved_models/cancer-pred.h5
```

   Final Swarm model is saved inside the model directory that is `workspace/cancer-pred/model/saved_models` directory on both the hosts. SL and ML nodes exit but it is not removed after the Swarm training.

10. On both host-1 and host-2, To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs and delete the workspace directory.
