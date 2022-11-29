# MNIST using Reverse Proxy

This is single host MNIST example using reverse proxy service parameters with 1 SN node, 1 SWOP node, 1 SWCI node and 2 SL nodes.

The following image illustrates a cluster setup for the Reverse Proxy with MNIST example:

![](/docs/User/GUID-D9C8F73B-BAFB-41E2-9B70-02C628836B96-high.png)

1.  This example uses a SN node. This node is named as **sn-1** and is the Sentinel Node. **sn-1** runs on host 172.1.1.1.

2.  SL and ML nodes are automatically spawned by SWOP node during training.

3.  This example uses a SWOP node that connects to SN node. The name of the docker container representing this SWOP node is **swop-1**. **swop-1** runs on host 172.1.1.1.

4.  Training is initiated by SWCI node \(**swci-1**\) that runs on host 172.1.1.1.

5.  This example assumes that the License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.


This example runs Reverse Proxy with MNIST [1] on the Swarm Learning platform. It uses TensorFlow as the backend. The code for this example is taken from [2] and modified to run on a Swarm Learning platform.

This example shows the MNIST using reverse proxy to mimic real world behaviour. This example uses BIND9 as the DNS server and NGINX as the reverse proxy server and builds both the docker images with suitable configurations. \(Please refer to the respective docker files\). This example has automated the end-to-end running of MNIST, and includes starting the BIND9 and NGINX containers for user convenience. For more information on arguments passed to the respective run scripts of swarm components, see `run-all` script.

This example uses one training batch and one test batch. Both batch files are stored in an archive file called `mnist.npz`. The Machine Learning program, after conversion to Swarm Learning for the TensorFlow-based Keras platform, is in `examples/reverse-proxy/mnist/model` and the TensorFlow-based file name is `mnist tf.py`.

This example shows the Swarm training of MNIST model using two ML nodes. ML nodes are automatically spawned by SWOP node. Swarm training is initiated by SWCI node and orchestrated by a SN node. This example also shows how private data and shared model can be mounted to ML nodes for Swarm training. For more information, see the profile files and task definition files placed under `examples/reverse-proxy/mnist/swop` and `examples/reverse-proxy/mnist/swci` folders, respectively.

## Running the MNIST example

1.  On host-1, navigate to swarm-learning folder.

    ``` {#CODEBLOCK_MYT_33W_NVB}
    cd swarm-learning
    ```

2.  Run the `run-all` script from the `swarm-learning` folder with `APLS IP` argument and `wait time for sn`.

    ``` {#CODEBLOCK_LQT_DNY_NVB}
    .\examples\reverse-proxy\run-all 172.1.1.1 4m
    ```

    First argument `APLS IP` in this command is a mandatory parameter. Second argument `wait time for sn` if not passed, by default it will wait for 5 minutes. This `wait time for sn` argument is similar to sleep, where `m` denotes minutes.

    This script will take care of starting BIND9 container, NGINX container and rest all of the swarm containers in the sequential manner. All the run-script commands will now take FQDN's as service parameter arguments instead of ports.

    **NOTE:** SN-P2P-PORT still needs 30303 port in the host machine, where SN container runs.

3.  On host-1, Swarm training is automatically started when the run task \(`swarm_mnist_task`\) gets assigned and executed. Open a new terminal on host-1 and monitor the docker logs of ML nodes for Swarm training. Swarm training will end with the following log message.

    ``` {#CODEBLOCK_T4Y_2JW_NVB}
    SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
    ```

    The final Swarm model is saved inside `workspace/reverse-proxy/mnist/model` directory on host-1. All the dynamically spawned SL and ML nodes exits after Swarm training. The SN and SWOP nodes continue to run.

4.  On host-1, to clean-up, run the `scripts/bin/stop-swarm` script to stop and remove the swarm container nodes of the previous run. If required, backup the container logs. This example builds and starts BIND9 and NGINX, so remove their respective images and containers. Then, remove docker volume \(`sl-cli-lib`\) and delete the `workspace` directory.


**Parent topic:**[Examples using reverse proxy](GUID-DD2A624E-30B8-4FCD-A23F-014AE0D76452.md)

[1]	Y. LeCun, C. Cortes and C. J. Burges, "THE MNIST DATABASE," [Online]. Available: [http://yann.lecun.com/exdb/mnist/](http://yann.lecun.com/exdb/mnist/)  

[2] [https://www.tensorflow.org/tutorials/quickstart/beginner](https://www.tensorflow.org/tutorials/quickstart/beginner)

[3] https://www.isc.org/bind/ and https://bind9.readthedocs.io/

[4] https://www.nginx.com/ and https://nginx.org/en/docs/



