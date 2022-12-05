# <a name="GUID-41298B6F-BF19-4873-A5AE-1DA0E1CFB358"/> Nvidia GPU based MNIST-PYT

This example runs MNIST-PYT[1](#) application with Nvidia GPU based local training on the Swarm Learning platform.

When compared to CPU based mnist-pyt example following are the key differences in this example. 
- User image build uses rocm/pytorch image as base image. Base image needs to be selected such that it support the host NVIDIA gpu setup. Refer https://hub.docker.com/r/pytorch/pytorch for more details. 
- SWOP options needs additional tags to access NVIDIA gpus. Refer Swop profile schema for more details. 
- Run task command needs additional argument to be passed in. Refer run task under this example. 
- User ML application code needs changes to access NVIDIA gpus. 

This example uses one training batch and one test batch. The files for both these batches are in an archive file, called `mnist.npz`.

<blockquote>
    
NOTE: See data license associated with this dataset, <code>examples/mnist-pyt/common/app-data/mnist-npz.md</code>.

</blockquote>

The Machine Learning program, after conversion to Swarm Learning for the PyTorch platform, is in `examples/mnist-pyt/gpu-based/nvidia/model`. The PyTorch-based file is called `mnist_pyt.py`.

This example shows the Swarm training of MNIST model using four ML nodes. ML nodes along with SL nodes are automatically spawned by SWOP nodes - all running on a single host. Swarm training gets initiated by the SWCI node and orchestrated by one SN node running on the same host. This example also shows how private data, private scratch area and shared model can be mounted to ML nodes for Swarm training.

The following image illustrates a cluster setup for the MNIST example:![Four cluster setup](/docs/User/GUID-DC68E962-E2A0-47C5-9345-0A7448C42AD6-high.png)


-   This example uses one SN node. The names of the docker containers representing this node is SN1. SN1 is also the Sentinel Node. SN1 runs on the host 172.1.1.1.

-   Four SL and ML nodes are automatically spawned by SWOP node during training and removed after the training. This example uses one SWOP node that connects to the SN node. The names of the docker containers representing this SWOP node is SWOP1. SWOP1 runs on the host 172.1.1.1.

-   Training is initiated by SWCI node \(SWCI1\) that runs on the host 172.1.1.1.

-   This example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


## <a name="SECTION_G1M_4RZ_LSB"/> Running the MNIST-PYT example

1.  Navigate to `swarm-learning` folder (that is, parent to examples directory).

```
cd swarm-learning
```

```<a name="CODEBLOCK_R41_BZX_CTB"/> 
curl https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz -o examples/mnist-pyt/common/app-data/mnist.npz
```

<blockquote>
    
NOTE: For `mnist.npz` data notice, see <code>examples/mnist-pyt/common/app-data/mnist-npz.md</code>.

</blockquote>

2.  Create a temporary workspace directory and copy `mnist-pyt` example.

```
mkdir workspace
cp -r examples/mnist-pyt/gpu-based/nvidia/ workspace/mnist-pyt/
cp -r examples/mnist-pyt/common/ workspace/mnist-pyt/data-and-scratch/
cp -r examples/utils/gen-cert workspace/mnist-pyt/
```

3.  This example has separate private `data-and-scratch` directories for each user. Create respective user directories and copy the `data-and-scratch` directory.


    ```
    mkdir workspace/mnist-pyt/user1 workspace/mnist-pyt/user2 workspace/mnist-pyt/user3 workspace/mnist-pyt/user4
    cp -r workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user1/
    cp -r workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user2/
    cp -r workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user3/
    cp -r workspace/mnist-pyt/data-and-scratch workspace/mnist-pyt/user4/
    ```

4.  Run the gen-cert utility to generate certificates for each Swarm component using the command (`gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`):


    ```
    ./workspace/mnist-pyt/gen-cert -e mnist-pyt -i 1
    ```


5.  Search and replace all occurrences of `<CURRENT-PATH>` tag in `run_mnist_pyt.yaml` and `swop_profile.yaml` files with `$(pwd)`.

```
sed -i "s+<CURRENT-PATH>+$(pwd)+g" workspace/mnist-pyt/swop/swop_profile.yaml workspace/mnist-pyt/swci/taskdefs/run_mnist_pyt.yaml

```

6.  Create a docker volume and copy Swarm Learning wheel file:

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


8.  Run SN node (SN1 - sentinel node)

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


9. On host-1, run SWOP node \(SWOP1\).

<blockquote>
    
NOTE: If required, according to environment, modify IP and proxy in the profile files under <code>workspace/mnist-pyt/swop</code> folder.

</blockquote>

```
./scripts/bin/run-swop -d --rm --name=swop1 \
--network=host-1-net --usr-dir=workspace/mnist-pyt/swop \
--profile-file-name=swop_profile.yaml \
--key=workspace/mnist-pyt/cert/swop-1-key.pem \
--cert=workspace/mnist-pyt/cert/swop-1-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath \
-e SWOP_KEEP_CONTAINERS=True \
-e http_proxy= -e https_proxy= --apls-ip=172.1.1.1
```
<blockquote>
   NOTE: `-e SWOP_KEEP_CONTAINERS=True` is an optional argument, by default it would be `False`. 
   SWOP_KEEP_CONTAINERS is set to True so that SWOP doesn't remove stopped SL and ML containers. With out this setting if there is any internal error in SL or ML then SWOP removes them automatically. Refer documentation of SWOP_KEEP_CONTAINERS for more details.
</blockquote>


10. Run SWCI node and observe sequential execution of two tasks – build task (`build_pyt_user_image`) and run task (`run_mnist_pyt`).

-   `build_pyt_user_image` - builds pytorch based user image.

-   `run_mnist_pyt` - runs Swarm training across for four ML nodes.

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


11. Four nodes of Swarm trainings are automatically started when the run task (`run_mnist_pyt`) gets assigned and executed. Open a new terminal and monitor the Docker logs of ML nodes for Swarm training. Swarm training ends with the following log message:

```
SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
```


   Final Swarm model is saved inside each user’s private `scratch` directory that is, `workspace/mnist-pyt/user/data-and-scratch/scratch`. All the dynamically spawned SL and ML containers exits after Swarm training if `SWOP_KEEP_CONTAINERS` is not set, otherwise SL and ML containers needs to be removed manually. The SN and SWOP nodes continues to run.

12. To clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs. Remove Docker networks (`host-1-net`) and Docker volume (`sl-cli-lib`), and delete the workspace directory.

 
 

### Running using `run-sl` command ###

In place of using swop and swci, execute `run-sl` command like below to start user and ml containers. Refer `run-sl` documentation and NVIDIA gpu specific docker options from swop profile for more details. User image needs to be built through docker build. 
```
./scripts/bin/run-sl --name=sl1 --host-ip=172.1.1.1 \
--sn-ip=172.1.1.1 --sn-api-port=30304 --sl-fs-port=16000 \
--key=workspace/mnist-pyt/cert/sl-1-key.pem \
--cert=workspace/mnist-pyt/cert/sl-1-cert.pem \
--capath=workspace/mnist-pyt/cert/ca/capath \
--ml-image=user-image-nvidia-pyt --ml-name=ml1 \
--ml-w=/tmp/test --ml-entrypoint=python3 --ml-cmd=model/mnist_pyt.py \
--ml-v=<CURRENT-PATH>/workspace/mnist-pyt/model:/tmp/test/model \
--ml-v=<CURRENT-PATH>/workspace/mnist-pyt/user1/data-and-scratch:/tmp/test/data-and-scratch \
--ml-e DATA_DIR=data-and-scratch/app-data \
--ml-e SCRATCH_DIR=data-and-scratch/scratch \
--ml-e MODEL_DIR=model \
--ml-e MAX_EPOCHS=100 \
--ml-e MIN_PEERS=2 \
--ml-gpus="all" \
--apls-ip=172.1.1.1
```



[1](#) [https://yann.lecun.com/exdb/mnist/](#)

 

