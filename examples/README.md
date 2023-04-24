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

-   [MNIST](/examples/mnist/MNIST.md)
-   [MNIST-PYT](/examples/mnist-pyt/MNIST-PYT.md)
-   [CIFAR-10](/examples/cifar10/CIFAR-10.md)
-   [Credit card fraud detection](/examples/fraud-detection/Credit_card_fraud_detection.md)
-   [Reverse Proxy based examples](/examples/reverse-proxy/README.md)

They use different models, data, ML platforms, and Swarm cluster configurations. All examples require valid X.509 certificates to be used by different Swarm Learning components. A certificate generation utility (`gen-cert`) is provided to enable users to run the examples quickly.

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

