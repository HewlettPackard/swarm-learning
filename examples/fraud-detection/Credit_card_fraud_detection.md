# <a name="GUID-0B85BF67-C19C-4D10-9EA0-94A48C179FB8"/> Credit card fraud detection

This example runs a credit card fraud detection algorithm on the Swarm Learning platform. It uses Keras and TensorFlow.

This example uses a subset of the data from[1](#). This subset is balanced and is created as a 50:50 data set with equal distribution of fraud and non-fraud cases.

This example uses four training batches and one test batch. These files are in the `examples/fraud-detection/app-data` directory.

<blockquote>
NOTE: For data license associated with this dataset, see <code>/examples/fraud-detection/data-and-scratch/app-data/data_license.md</code>.

</blockquote>

The ML program, after conversion to Swarm Learning, is in `examples/fraud-detection/model` and is called `fraud-detection.py`.

This example shows the Swarm training of the credit card fraud detection model using four ML nodes. ML nodes along with SL nodes are automatically spawned by SWOP nodes - all running on a single host. Swarm training gets initiated by the SWCI node and orchestrated by one SN node running on the same host. This example also shows how private data, private scratch area, and shared model can be mounted to ML nodes for Swarm training. For more information, see the profile files and task definition files placed under `examples/fraud-detection/swop` and `examples/fraud-detection/swci`.

The following image illustrates a cluster setup that uses only one host:

![Credit Card Fraud Detection](/docs/User/GUID-BE2185B8-5C3B-4BD3-91FF-9ABC77D0720C-high.png)

-   This example uses one SN node. The names of the docker containers representing this node is SN1. SN1 is also the Sentinel Node. SN1 runs on the host 172.1.1.1.

-   Four SL and ML nodes are automatically spawned by SWOP node during training and removed after the training. This example uses one SWOP node that connects to the SN node. The names of the docker containers representing this SWOP node is SWOP1. SWOP1 runs on the host 172.1.1.1.

-   Training is initiated by SWCI node \(SWCI1\) that runs on the host 172.1.1.1.

-   This example assumes that License Server already runs on the host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## <a name="GUID-3FADC998-63FD-4058-A7B8-F172469E01F3"/> Running the credit card fraud detection example

1.  On host-1, navigate to `swarm-learning` folder (that is, parent to examples directory).

```
cd swarm-learning
```

2.  On host-1, create a temporary `workspace` directory, `fraud-detection` example, and `gen-cert` utility.

```
mkdir workspace
cp -r examples/fraud-detection workspace/
cp -r examples/utils/gen-cert workspace/fraud-detection/
```

3.  This example has a separate private `data-and-scratch` directories for each user or ML node. Create the respective directories and copy `data-and-scratch` directory. Running this example creates a `scratch` directory for each user and saves the trained Swarm model in the directory at the end of the training.

```
mkdir workspace/fraud-detection/user1 workspace/fraud-detection/user2
mkdir workspace/fraud-detection/user3 workspace/fraud-detection/user4
cp -r workspace/fraud-detection/data-and-scratch workspace/fraud-detection/user1/
cp -r workspace/fraud-detection/data-and-scratch workspace/fraud-detection/user2/
cp -r workspace/fraud-detection/data-and-scratch workspace/fraud-detection/user3/
mv workspace/fraud-detection/data-and-scratch workspace/fraud-detection/user4/

```

4.  Run the `gen-cert` utility to generate certificates for each Swarm component using the command, `gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`.

```
./workspace/fraud-detection/gen-cert -e fraud-detection -i 1
```

5.  Search and replace all occurrences of `<CURRENT-PATH>` tag in `swarm_fd_task.yaml` and `swop1_profile.yaml` files with `$(pwd)`.

    ```
    sed -i "s+<CURRENT-PATH>+$(pwd)+g" workspace/fraud-detection/swop/swop*_profile.yaml workspace/fraud-detection/swci/taskdefs/swarm_fd_task.yaml
    
    ```

6.  Create a docker volume and copy Swarm Learning wheel file.

```
docker volume rm sl-cli-lib
docker volume create sl-cli-lib
docker container create --name helper -v sl-cli-lib:/data hello-world
docker cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl helper:/data
docker rm helper

```

7.  Create a docker network for SN, SWOP, SWCI, SL, and user containers running on the same host.

```
docker network create host-1-net

```

8.  Run Swarm Network node \(SN1\) - sentinel node.

```
./scripts/bin/run-sn -d --rm --name=sn1 \
--network=host-1-net --host-ip=sn1 --sentinel \
--key=workspace/fraud-detection/cert/sn-1-key.pem \
--cert=workspace/fraud-detection/cert/sn-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
--apls-ip=172.1.1.1
```

Use the Docker logs command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when the following messages appear in the log output:

```
swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
```

9.  Run Swarm Operator node \(SWOP1\).

<blockquote>
    
NOTE: If required, according to environment, modify IP and proxy in the profile files under <code>workspace/fraud-detection/swop</code> folder.

</blockquote>

```
./scripts/bin/run-swop -d --rm --name=swop1 \
--network=host-1-net --usr-dir=workspace/fraud-detection/swop \
--profile-file-name=swop1_profile.yaml \
--key=workspace/fraud-detection/cert/swop-1-key.pem \
--cert=workspace/fraud-detection/cert/swop-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
-e http_proxy= -e https_proxy= --apls-ip=172.1.1.1
```

10. Run SWCI node \(SWCI1\). It creates, finalizes and assigns below task to task-framework for sequential execution:

-   `user_env_tf_build_task`: Builds TensorFlow based Docker image for ML node to run model training.

-   `swarm_fd_task`: Create containers out of ML image, and mounts model and data path to run Swarm training.

<blockquote>
    
NOTE: If required, according to environment, modify SN IP in <code>workspace/fraud-detection/swci/swci-init</code> file.

</blockquote>

```
./scripts/bin/run-swci -ti --rm --name=swci1 \
--network=host-1-net --usr-dir=workspace/fraud-detection/swci \
--init-script-name=swci-init \
--key=workspace/fraud-detection/cert/swci-1-key.pem \
--cert=workspace/fraud-detection/cert/swci-1-cert.pem \
--capath=workspace/fraud-detection/cert/ca/capath \
-e http_proxy= -e https_proxy= --apls-ip=172.1.1.1
```

11. Four nodes of Swarm training are automatically started when the run task (`swarm_fd_task`) gets assigned and executed. Open a new terminal on host-1 and monitor the Docker logs of ML nodes for Swarm training. Swarm training ends with the following log message:

```
SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
```

Final Swarm model is saved inside each user’s private `scratch` directory, which is `workspace/fraud-detection/user<id>/data-and-scratch/scratch` on both the hosts. All the dynamically spawned SL and ML nodes exits after Swarm training. The SN and SWOP nodes continues to run.

12. To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs and remove Docker network (`host-1-net`) and Docker volume (`sl-cli-lib`), and delete the workspace directory.


1 [1](#)[https://www.kaggle.com/mlg-ulb/creditcardfraud](#)
