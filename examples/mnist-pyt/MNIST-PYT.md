# <a name="GUID-41298B6F-BF19-4873-A5AE-1DA0E1CFB358"/> MNIST-PYT

This example runs MNIST-PYT[1](#) on the Swarm Learning platform. It uses PyTorch as the backend. The code for this example is modified to run on a Swarm Learning platform.

This example uses one training batch and one test batch. The files for both these batches are in an archive file, called `mnist.npz`.

<blockquote>
    
NOTE: See data license associated with this dataset, <code>examples/mnist-pyt/app-data/mnist-npz.md</code>.

</blockquote>

The Machine Learning program, after conversion to Swarm Learning for the PyTorch platform, is in `examples/mnist-pyt/model`. The PyTorch-based file is called `mnist_pyt.py`.

This example shows the Swarm training of MNIST model using four ML nodes. ML nodes along with SL nodes are automatically spawned by SWOP nodes running on two different hosts. Swarm training is initiated by SWCI node and orchestrated by two SN nodes running in different hosts. This example also shows how private data, private scratch area and shared model can be mounted to ML nodes for Swarm training.

The following image illustrates a cluster setup for the MNIST example:![Four cluster setup](/docs/User/GUID-25587679-1F3A-43DC-8D02-48E6BEFF7DA6-high.png)

-   This example uses two SN nodes. The names of the docker containers representing these two nodes are SN1 and SN2. SN1 is the Sentinel Node. SN1 runs on host 172.1.1.1 and SN2 runs on host 172.2.2.2.

-   Two SL nodes and two ML nodes are automatically spawned by each SWOP node during training and removed after training. Example uses two SWOP nodes – one connects to each SN node. The names of the docker containers representing these two SWOP nodes are SWOP1 and SWOP2. SWOP1 runs on host 172.1.1.1 and SWOP2 runs on host 172.2.2.2.

-   Training is initiated by SWCI node that runs on host 172.1.1.1.

-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## <a name="SECTION_G1M_4RZ_LSB"/> Running the MNIST-PYT example

1.  On both host-1 and host-2, navigate to `swarm-learning` folder (that is, parent to examples directory).

```
cd swarm-learning
```

```<a name="CODEBLOCK_R41_BZX_CTB"/> 
curl https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz -o examples/mnist-pyt/data-and-scratch/app-data/mnist.npz
```

<blockquote>
    
NOTE: For `mnist.npz` data notice, see <code>examples/mnist-pyt/data-and-scratch/app-data/mnist-npz.md</code>.

</blockquote>

2.  On both host-1 and host-2, create a temporary workspace directory and copy `mnist-pyt` example.

```
mkdir workspace
cp -r examples/mnist-pyt workspace/
cp -r examples/utils/gen-cert workspace/mnist-pyt/
```

3.  On both host-1 and host-2, this example has separate private `data-and-scratch` directories for each user. Create respective user directories and copy the `data-and-scratch` directory.

    On host-1:

    ```
    mkdir workspace/mnist-pyt/user1 workspace/mnist-pyt/user2
    cp -r workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user1/
    mv workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user2/
    ```

    On host-2:

    ```
    mkdir workspace/mnist-pyt/user3 workspace/mnist-pyt/user4
    cp -r workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user3/
    mv workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user4/
    ```

4.  On both host-1 and host-2, run the gen-cert utility to generate certificates for each Swarm component using the command (`gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`):

    On host-1:

    ```
    ./workspace/mnist-pyt/gen-cert -e mnist-pyt -i 1
    ```

    On host-2:

    ```
    ./workspace/mnist-pyt/gen-cert -e mnist-pyt -i 2
    ```

5.  On both host-1 and host-2, share the CA certificates between the hosts as follows:

    On host-1:

    ```
    scp host-2:<PATH>workspace/mnist-pyt/cert/ca/capath/ca-2-cert.pem workspace/mnist-pyt/cert/ca/capath
    ```

    On host-2:

    ```
    scp host-1:<PATH>workspace/mnist-pyt/cert/ca/capath/ca-1-cert.pem workspace/mnist-pyt/cert/ca/capath
    ```

6.  On both host-1 and host-2, search and replace all occurrences of `<CURRENT-PATH>` tag in `swarm_mnist_task.yaml` and `swop_profile.yaml` files with `$(pwd)`.

```
sed -i "s+<CURRENT-PATH>+$(pwd)+g" workspace/mnist-pyt/swop/swop*_profile.yaml workspace/mnist-pyt/swci/taskdefs/swarm_mnist_task.yaml

```

7.  On both host-1 and host-2, create a docker volume and copy Swarm Learning wheel file:

```
docker volume rm sl-cli-lib
docker volume create sl-cli-lib
docker container create --name helper -v sl-cli-lib:/data hello-world
docker cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl helper:/data
docker rm helper
```

8.  On both host-1 and host-2, create a docker network for SN, SWOP, SWCI, SL, and user containers running in a host.

    On host-1:

    ```
    docker network create host-1-net
    ```

    On host-2:

    ```
    docker network create host-2-net
    ```

9.  On host-1, Run SN node (SN1 - sentinel node)

```
./scripts/bin/run-sn -d --rm --name=sn1 --network=host-1-net \
--host-ip=172.1.1.1 --sentinel --sn-p2p-port=30303 --sn-api-port=30304 \
--key=workspace/mnist-pyt/cert/sn-1-key.pem \
--cert=workspace/mnist-pyt/cert/sn-1-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath \
--apls-ip=172.1.1.1
```

   Use the Docker logs command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

```
swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
```

   On host-2, run SN node (SN2).

```
./scripts/bin/run-sn -d --rm --name=sn2 --network=host-2-net \
--host-ip=172.2.2.2 --sentinel-ip=172.1.1.1 --sn-p2p-port=30303 \
--sn-api-port=30304 --key=workspace/mnist-pyt/cert/sn-2-key.pem \
--cert=workspace/mnist-pyt/cert/sn-2-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath \
--apls-ip=172.1.1.1
```

10. On host-1, run SWOP node \(SWOP1\).

<blockquote>
    
NOTE: If required, according to environment, modify IP and proxy in the profile files under <code>workspace/mnist/swop</code> folder.

</blockquote>

```
./scripts/bin/run-swop -d --rm --name=swop1 \
--network=host-1-net --usr-dir=workspace/mnist-pyt/swop \
--profile-file-name=swop1_profile.yaml \
--key=workspace/mnist-pyt/cert/swop-1-key.pem \
--cert=workspace/mnist-pyt/cert/swop-1-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath \
-e http_proxy= -e https_proxy= --apls-ip=172.1.1.1
```

   On host-2, run SWOP node (SWOP2).

<blockquote>
    NOTE: If required, according to environment, modify IP and proxy in the profile files under <code>workspace/mnist/swop</code> folder.
</blockquote>

```
./scripts/bin/run-swop -d --rm --name=swop2 \
--network=host-2-net --usr-dir=workspace/mnist-pyt/swop \
--profile-file-name=swop2_profile.yaml \
--key=workspace/mnist-pyt/cert/swop-2-key.pem \
--cert=workspace/mnist-pyt/cert/swop-2-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath -e http_proxy= \
-e https_proxy= --apls-ip=172.1.1.1
```

11. On host-1, run SWCI node and observe sequential execution of two tasks – build task (`user_env_tf_build_task`) and run task (`swarm_mnist_task`).

-   `user_env_tf_build_task` - builds TensorFlow based ML nodes with model and data.

-   `swarm_mnist_task` - run Swarm training across for two ML nodes.

<blockquote>
   NOTE: If required, according to the environment, modify SN IP in <code>workspace/mnist-pyt/swci/swci-init</code> file.
</blockquote>

```
./scripts/bin/run-swci -ti --rm --name=swci1 \
--network=host-1-net --usr-dir=workspace/mnist-pyt/swci \
--init-script-name=swci-init --key=workspace/mnist-pyt/cert/swci-1-key.pem \
--cert=workspace/mnist-pyt/cert/swci-1-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath -e http_proxy= \
-e https_proxy= --apls-ip=172.1.1.1
```

12. On both host-1 and host-2, Four nodes of Swarm trainings are automatically started when the run task (`swarm_mnist_task`) gets assigned and executed. Open a new terminal on both host-1 and host-2 and monitor the Docker logs of ML nodes for Swarm training. Swarm training ends with the following log message:

```
SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
```

   Final Swarm model is saved inside each user’s private `scratch` directory that is, `workspace/mnist-pyt/user/data-and-scratch/scratch` on both the hosts. All the dynamically spawned SL and ML nodes exits after Swarm training. The SN and SWOP nodes continues to run.

13. On both host-1 and host-2, to clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs. Remove Docker networks (`host-1-net` and `host-2-net`) and Docker volume (`sl-cli-lib`), and delete the workspace directory.

     


[1](#) [https://yann.lecun.com/exdb/mnist/](#)

 

