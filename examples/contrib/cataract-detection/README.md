
# Privacy preserving Swarm Learning on Cataract Detection

Cataract is one of the most common issues faced during old age 
that in the worst case can lead to loss of sight. Detecting 
cataract during its early stages can prevent several complications.
Data in the healthcare industry is considered to be highly sensitive and is distributed in various hospitals. Hence this project, focuses on developing a machine learning framework using Swarm Learning to help in the early detection of cataracts by maintaining the privacy of the patients data while creating an accurate and a robust model. 


## References of this example:
- Selected and presented in the 29th International Conference on Computational & Experimental Engineering and Sciences (ICCES2023)

## High Level Overview
<img width="500" alt="Screenshot 2023-01-11 221937" src="/docs/User/GUID-4D303DEC-8E71-43F4-BDCB-04B0C1AE79D8-high.png">

## Pre-requisites 
Swarm Learning framework must be installed and APLS must be running.
For installation info refer [HPE Swarm Learning Documentation](https://github.com/HewlettPackard/swarm-learning)

## Dataset Description
This project uses the Ocular Disease Intelligent Recognition (ODIR),	
The dataset is intended to mimic a "real-life" collection of patient 
data gathered by Shanggong Medical Technology Co., Ltd. from various
hospitals and healthcare facilities in China. The dataset contains retinal images of both eyes which 
classifies multiple disease conditions such as cataracts, Glaucoma,
Hypertension, Age-related Macular Degeneration, and Pathological Myopia. The npz file of the dataset, with different data splits, is in `cataract-detection/app-data` directory.


## Data Pre-Processing
The dataset consists of pre-processed images. However, we need 
to pre-process the images by resizing them accordingly for the 
model that will be implemented (i.e., VGG19 uses 224x224x3 as 
the input channel). To make the process of reading the images 
faster, we have converted the images to NumPy arrays (.npz format).
Further, these NumPy arrays are split into training and testing
data in the ratio 80:20.

## Data-Split 

 To reflect a real-life scenario, we have considered different data-splits, where data 
 across different organizations (hospitals/clinics) are 
 unequally distributed containing biased data pertaining to a 
 particular region, sex, ethnicity, or even type of organization.
  Hence, we have segregated our dataset into three categories 
  such as Gynac (GY) containing a dataset of all women from the 
  age 18-60, General Physician (GP) containing a dataset of men 
  and women up to the age 60 and Senior Citizens (SC) which 
  contains a dataset of all men and women above the age of 60.
  The maximum validation accuracy obtained for the
centralized setup is 93.9, 93.3, and 97.7 for GP, GY, and SC
nodes respectively

  After training with two swarm learning nodes , the maximum validation accuracy obtained under the Swarm Learning setup is 95.48
and 98.27 for GP-GY and GP-SC splits respectively

#### The following summarizes our data splits

##### 1) GP
##### 2) GY
##### 3) SC

## Preview 
This project uses the Ocular Dataset and data splits have been done. More information can be found [here](https://www.kaggle.com/datasets/andrewmvd/ocular-disease-recognition-odir5k). 
The ML program, after conversion to Swarm Learning, is in `cataract-detection/model` and is called `cataract.py`. It also uses pre-trained model(VGG19) to leverage the concept of transfer learning
It contains our model integrated with Swarm Learning Framework.

This project shows the Swarm training of Keras based Machine Learning 
model using two ML nodes. It also shows how ML environment can 
be built manually using docker command and how Swarm training 
can be launched without SWCI or SWOP nodes. 
Here `scripts/bin/run-sl` script is used to spawn each ML node 
to run Cataract model as a `sidecar` container of each SL node.

The High Level Overview image above illustrates a cluster setup:

-   This example uses one SN node. SN1 is the name of the Docker container that runs on host 172.1.1.1.

-   Two SL and ML nodes are manually spawned by running the `run-sl` script. Swarm training gets invoked once ML nodes are started. Name of the SL nodes that runs as container are SL1 and SL2. Name of the ML nodes that runs as container are ML1 and ML2.

-   SL1 and ML1 pair runs on host 172.1.1.1, whereas SL2 and ML2 pair runs on host 172.1.1.2.

-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## Running Cataract detection Model

1.  On both host-1 and host-2, navigate to `swarm-learning` folder \(that is, parent to examples directory\).

```
cd swarm-learning
```

2.  On both host-1 and host-2, create a temporary workspace directory and copy `cataract-detection` example.

```
mkdir workspace
cp -r examples/contrib/cataract-detection workspace/
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
./scripts/bin/run-sn -d --name=sn1 --host-ip=172.1.1.1 \
-e http_proxy= -e https_proxy=  \
--sentinel --sn-api-port=30304 --key=workspace/cataract-detection/cert/sn-1-key.pem \
--cert=workspace/cataract-detection/cert/sn-1-cert.pem \
--capath=workspace/cataract-detection/cert/ca/capath --apls-ip=172.1.1.1
```

   Use the Docker logs command to monitor this Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```

7.  On host-1, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate, as the ML program needs to download the ODIR dataset.

```
./scripts/bin/run-sl --name=sl1 --host-ip=172.1.1.1 \
-e http_proxy= -e https_proxy=  \
--sn-ip=172.1.1.1 --sn-api-port=30304 --sl-fs-port=16000 \
--key=workspace/cataract-detection/cert/sl-1-key.pem \
--cert=workspace/cataract-detection/cert/sl-1-cert.pem \
--capath=workspace/cataract-detection/cert/ca/capath --ml-it \
--ml-image=user-ml-env-tf2.7.0 --ml-name=ml1 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cataract.py \
--ml-v=workspace/cataract-detection/model:/tmp/test/model \
--ml-v=workspace/cataract-detection/app-data:/tmp/test/app-data \
--ml-e DATA_DIR=app-data --ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1
```

8.  On host-2, run Swarm Learning node and Machine Learning node \(as a side-car\): Set the proxy server as appropriate, as the ML program needs to download the ODIR dataset

```
./scripts/bin/run-sl --name=sl2 --host-ip=172.1.1.2 \
-e http_proxy= -e https_proxy=  \
--sn-ip=172.1.1.1 --sn-api-port=30304 \
--sl-fs-port=17000 --key=workspace/cataract-detection/cert/sl-2-key.pem \
--cert=workspace/cataract-detection/cert/sl-2-cert.pem \
--capath=workspace/cataract-detection/cert/ca/capath \
--ml-it --ml-image=user-ml-env-tf2.7.0 --ml-name=ml2 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/cataract.py \
--ml-v=workspace/cataract-detection/model:/tmp/test/model \
--ml-v=workspace/cataract-detection/app-data:/tmp/test/app-data \
--ml-e DATA_DIR=app-data --ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=1 --ml-e MIN_PEERS=2 \
--ml-e https_proxy=http://<your-proxy-server-ip>:<port-number> \
--apls-ip=172.1.1.1
```

9.  On both host-1 and host-2, Two node of Swarm training are started. User can monitor the Docker logs of ML nodes \(ML1 and ML2 containers\) for Swarm training on both host-1 and host-2. Training ends with the following log message:

```
SwarmCallback : INFO : Saved the trained model - model/saved_models/cataract.h5
```

   Final Swarm model is saved inside the model directory that is `workspace/cataract-detection/model/saved_models` directory on both the hosts. SL and ML nodes exit but it is not removed after the Swarm training.

10. On both host-1 and host-2, To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs and delete the workspace directory.

## Authors

- [@samyakmaurya](https://www.github.com/samyakmaurya)
- [@janavi2001](https://www.github.com/janavi2001)
- [@ThilakShekharShriyan](https://www.github.com/ThilakShekharShriyan)
- [@vaibzvb](https://github.com/vaibzvb)

