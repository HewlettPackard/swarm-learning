## Prerequisite for all examples
1. Start license server and install valid license before running any of the examples. Refer [Installing licenses and starting license server](/docs/Install/HPE_Swarm_Learning_installation.md).

2. Install the Swarm Learning product using the Web UI installer.  Refer [Web UI installation](/docs/Install/HPE_Swarm_Learning_installation.md)

For more information on starting license server and installing the Swarm Learning, see [HPE Swarm Learning Installation and Configuration Guide](/docs/Install/HPE_Swarm_Learning_installation.md).
In this section, examples use different models, data, ML platforms, and Swarm cluster configurations. All examples require valid X.509 certificates to be used by different Swarm Learning components. A certificate generation utility is provided with each example to enable users to run the examples quickly.
<blockquote>
NOTE: HPE recommends that users must use their own certificates in actual production environment.

</blockquote>

## Swarm Learning Examples

Several examples of using Swarm Learning are provided with the package. 

For details of running each example, see the below:

-   [MNIST](/examples/mnist/README.md)
-   [MNIST-PYT](/examples/mnist-pyt/README.md)
-   [CIFAR-10](/examples/cifar10/README.md)
-   [Credit card fraud detection](/examples/fraud-detection/README.md)
-   [Reverse Proxy based examples](/examples/reverse-proxy/README.md)
-   [Spire based example](/examples/spire/cifar10/README.md)

They use different models, data, ML platforms, and Swarm cluster configurations. All examples require valid X.509 certificates to be used by different Swarm Learning components. A certificate generation utility (`gen-cert`) is provided to enable users to run the examples quickly.
<blockquote>
NOTE: Spire based example is automated and doesn't need any certificates to be generated. Spire agent and server containers will manage the certificates internally. 

</blockquote>

``` {#CODEBLOCK_WLX_CZN_WWB}
./swarm-learning/examples/utils/gen-cert -h
Usage: gen-cert -e EXAMPLE-NAME -i HOST-INDEX
        -e Name of the example e.g. mnist, mnist-pyt, cifar10 etc.
        -i Host index like 1,2 etc.
        -h Show help.
```

<blockquote>
NOTE: HPE recommends that users must use their own certificates in actual production environment.

</blockquote>


For more information on Swarm Learning platform and package, see *HPE Swarm Learning Installation and Configuration Guide*. This document is present in `swarm-learning/docs/directory`.

### System setup for the examples

1.  The instructions in these examples assume that Swarm Learning runs on 1 to 2 host systems.

    -   These systems have IP addresses 172.1.1.1 and 172.2.2.2.
    -   License server is installed on 172.1.1.1 and running on default port 5814.
    -   172.1.1.1 runs the Sentinel SN node.
    -   MNIST example has one more SN node. 172.2.2.2 runs the other SN node. A SL and ML node pair are spawned across these 2 host systems - 172.1.1.1 and 172.2.2.2.

    -   Spawning of SL and ML nodes can be automatic or manual.
    -   SWOP node, which runs on each host system, is automatically spawned using the task framework. MNIST example shows how Swarm training can be automatically launched using SWCI and SWOP nodes. SWCI runs on 172.1.1.1 host, while Swarm Operator runs on both 172.1.1.1 and 172.2.2.2 hosts.
    -   CIFAR-10 example shows how Swarm training can be manually launched using `run-sl` script on each host.
    -   Model training starts once minimum number \(`minPeers`\) of specified ML nodes are launched, either automatically or manually.
    -   After training, the final Swarm model is saved by each ML node.
2.  The files created under the workspace directory that include certs, models, data, etc., are expected to have the minimum file permission as 664. Once the files are copied to the workspace directory, check the permissions of the files inside it. If desired permissions are not met, user might observe `file permission denied` in the respective swarm component's Docker logs. To overcome such cases, user can change the permissions of the files by using the `chmod` command.
3.  Finally, these instructions assume that `swarm-learning` is the current working directory on all the systems: `cd swarm-learning`.
