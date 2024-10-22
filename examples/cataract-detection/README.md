
# Privacy preserving Swarm Learning on Cataract Detection

Cataract is one of the most common issues faced during old age 
that in the worst case can lead to loss of sight. Detecting 
cataract during its early stages can prevent several complications.
Data in the health care industry is considered to be highly sensitive and is distributed in various hospitals. Hence this project, focuses on developing a machine learning framework using Swarm Learning to help in the early detection of cataracts by maintaining the privacy of the patients data while creating an accurate and a robust model. 




 

## High Level Overview
<img width="245" alt="Screenshot 2023-01-11 221937" src="https://user-images.githubusercontent.com/66358485/211866773-9c75636c-267a-4013-a1d9-54dc995e9a67.png">


## Pre-requisites 
Swarm Learning framework must be installed and APLS must be running.
For installation info refer [HPE Swarm Learning Documentation](https://github.com/HewlettPackard/swarm-learning)

## Preview 
This project uses the Ocular Dataset and data splits have been done. More information can be found here " ". 
The ML program, after conversion to Swarm Learning, is in `cataract-detection/model` and is called `cataract.py`. 
It contains our model integrated with Swarm Learning Framework. More information can be found here " "

This project shows the Swarm training of Keras based Machine Learning 
model using two ML nodes. It also shows how ML environment can 
be built manually using docker command and how Swarm training 
can be launched without SWCI or SWOP nodes. 
Here `scripts/bin/run-sl` script is used to spawn each ML node 
to run Cataract model as a `sidecar` container of each SL node.

The following image illustrates a cluster setup:


-   This example uses one SN node. SN1 is the name of the Docker container that runs on host 172.1.1.4.

-   Two SL and ML nodes are manually spawned by running the `run-sl` script. Swarm training gets invoked once ML nodes are started. Name of the SL nodes that runs as container are SL1 and SL2. Name of the ML nodes that runs as container are ML1 and ML2.

-   SL1 and ML1 pair runs on host 172.1.1.4, whereas SL2 and ML2 pair runs on host 172.1.1.5.

-   This example assumes that License Server already runs on host 172.1.1.4. All Swarm nodes connect to the License Server, on its default port 5814.


## Running Cataract detection Model

1.  On both host-1 and host-2, navigate to `swarm-learning` folder \(that is, parent to examples directory\).

```
cd swarm-learning
```

2.  On both host-1 and host-2, create a temporary workspace directory and copy `cataract-detection` example.

```
mkdir workspace
cp -r examples/cataract-detection workspace/
cp -r examples/utils/gen-cert workspace/cataract-detection/
```

3.  On both host-1 and host-2, run the `gen-cert` utility to generate certificates for each Swarm component using the command `gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`:

    On host-1:

    ```
    ./workspace/cataract-detection/gen-cert -e cataract-detection -i 1
    ```

    On host-2:

    ```
    ./workspace/cataract-detection/gen-cert -e cataract-detection -i 2
    ```

4.  On both host-1 and host-2, share the CA certificates between the hosts as follows:

    On host-1:

    ```
    scp host-2:<PATH>workspace/cataract-detection/cert/ca/capath/ca-2-cert.pem workspace/cataract-detection/cert/ca/capath
    
    ```

    On host-2:

    ```
    scp host-1:<PATH>workspace/cataract-detection/cert/ca/capath/ca-1-cert.pem workspace/cataract-detection/cert/ca/capath
    
    ```

5.  On both host-1 and host-2, copy Swarm Learning wheel file inside build context and build Docker image for ML that contains environment to run Swarm training of user models.

```
cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl workspace/cataract-detection/ml-context/
docker build -t user-ml-env-tf2.7.0 workspace/cataract-detection/ml-context
```
You may need to specify the correct https_proxy for the docker build if you are behind a firewall. For eg,
``` 
docker build -t user-ml-env-tf2.7.0 --build-arg https_proxy=http://<your-proxy-server-ip>:<port> workspace/cataract-detection/ml-context
```

6.  On host-1, Run Swarm Network node \(sentinel node\)

```
./scripts/bin/run-sn -d --name=sn1 --host-ip=172.1.1.4 \
-e http_proxy= -e https_proxy=  \
--sentinel --sn-api-port=30304 --key=demo/cataract-detection/cert/sn-1-key.pem \
--cert=demo/cataract-detection/cert/sn-1-cert.pem \
--capath=demo/cataract-detection/cert/ca/capath --apls-ip=172.1.1.4
```

   Use the Docker logs command to monitor this Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```

7.  On host-1, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate, as the ML program needs to download the ODIR dataset.

```
./scripts/bin/run-sl --name=sl1 --host-ip=172.1.1.4 \
-e http_proxy= -e https_proxy=  \
--sn-ip=172.1.1.4 --sn-api-port=30304 --sl-fs-port=16000 \
--key=demo/cataract-detection/cert/sl-1-key.pem \
--cert=demo/cataract-detection/cert/sl-1-cert.pem \
--capath=demo/cataract-detection/cert/ca/capath --ml-it \
--ml-image=user-ml-env-tf2.7.0 --ml-name=ml1 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cataract.py \
--ml-v=demo/cataract-detection/model:/tmp/test/model \
--ml-v=demo/cataract-detection/app-data:/tmp/test/app-data \
--ml-e DATA_DIR=app-data --ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--apls-ip=172.1.1.4
```

8.  On host-2, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate, as the ML program needs to download the ODIR dataset

```
./scripts/bin/run-sl --name=sl2 --host-ip=172.1.1.5 \
-e http_proxy= -e https_proxy=  \
--sn-ip=172.1.1.4 --sn-api-port=30304 \
--sl-fs-port=17000 --key=demo/cataract-detection/cert/sl-2-key.pem \
--cert=demo/cataract-detection/cert/sl-2-cert.pem \
--capath=demo/cataract-detection/cert/ca/capath \
--ml-it --ml-image=user-ml-env-tf2.7.0 --ml-name=ml2 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cataract.py \
--ml-v=demo/cataract-detection/model:/tmp/test/model \
--ml-v=demo/cataract-detection/app-data:/tmp/test/app-data \
--ml-e DATA_DIR=app-data --ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--apls-ip=172.1.1.4
```

9.  On both host-1 and host-2, Two node of Swarm training are started. User can monitor the Docker logs of ML nodes \(ML1 and ML2 containers\) for Swarm training on both host-1 and host-2. Training ends with the following log message:

```
SwarmCallback : INFO : Saved the trained model - model/saved_models/cataract.h5
```

   Final Swarm model is saved inside the model directory that is `workspace/cataract-detection/model/saved_models` directory on both the hosts. SL and ML nodes exit but it is not removed after the Swarm training.

10. On both host-1 and host-2, To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs and delete the workspace directory.




 




## Authors

- [@janavi2001](https://www.github.com/janavi2001)
- [@ThilakShekharShriyan](https://www.github.com/ThilakShekharShriyan)
- [@samyakmaurya](https://www.github.com/samyakmaurya)
- [@vaibzvb](https://github.com/vaibzvb)

