## Prerequisite for all examples
1. Start license server and install valid license before running any of the examples. Refer [Installing licenses and starting license server](/docs/Install/HPE_Swarm_Learning_installation.md).

2. Install the Swarm Learning product using the Web UI installer.  Refer [Web UI installation](/docs/Install/HPE_Swarm_Learning_installation.md)

3. All the examples refer to a generic Swarm Learning client python wheel file. Create a symbolic link to the actual wheel file version, before running the examples
 ```
 cd swarm-learning/lib
 ln -fs swarmlearning-1.0.1-py3-none-manylinux_2_24_x86_64.whl swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
 ```
 
## Swarm Learning Examples

Several examples of using Swarm Learning are provided with the package. 

They use different models, data, ML platforms, and Swarm cluster configurations. All examples require valid X.509 certificates to be used by different Swarm Learning components. A certificate generation utility (gen-cert) is provided to enable users to run the examples quickly.

<blockquote>
NOTE:HPE recommends that users must use their own certificates in actual production environment.

</blockquote>

For details of running each example, see the below:

-   [MNIST](/examples/mnist/MNIST.md)
-   [MNIST-PYT](/examples/mnist-pyt/MNIST-PYT.md)
-   [CIFAR-10](/examples/cifar10/CIFAR-10.md)
-   [Credit card fraud detection](/examples/fraud-detection/Credit_card_fraud_detection.md)
