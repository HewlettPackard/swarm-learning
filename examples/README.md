## Prerequisite for all examples
1. Start license server and install valid license before running any of the examples. Refer [Installing licenses and starting license server](/docs/Install/HPE_Swarm_Learning_installation.md).

2. Install the Swarm Learning product using the Web UI installer.  Refer [Web UI installation](/docs/Install/HPE_Swarm_Learning_installation.md)

3. After Web UI completes its installation, verify if swarm-learning wheel file and its symbolic link are placed under the `lib` directory.


## Swarm Learning Examples

Several examples of using Swarm Learning are provided with the package. 

They use different models, data, ML platforms, and Swarm cluster configurations. All examples require valid X.509 certificates to be used by different Swarm Learning components. A certificate generation utility (gen-cert) is provided to enable users to run the examples quickly.

<blockquote>
NOTE:HPE recommends that users must use their own certificates in actual production environment.

</blockquote>


For details of running each example, see the below:

### [MNIST](/examples/mnist#-mnist) 
This example demonstrates Swarm learning use case on following setup. 
- Based on 2 hosts  
- Mnist dataset
- ML platform is Tensorflow 
- SL-ML pairs are spawned using SWOP
        
### [MNIST-PYT](/examples/mnist-pyt#mnist-pytorch-example) 
This example demonstrates Swarm learning use case on following setup. 
Additionally this example has branches to show case **CPU based** and **GPU based (amd, nvidia)** local training of machine learning application. 
- Based on single host
- Mnist dataset
- ML platform is PyTorch 
- SL-ML pairs are spawned using SWOP
        
### [CIFAR-10](/examples/cifar10#-cifar-10)
This example demonstrates Swarm learning use case on following setup. 
- Based on 2 hosts  
- Cifar dataset
- ML platform is Tensorflow
- SL-ML pairs are spawned using run-sl script
        
### [Credit card fraud detection](/examples/fraud-detection#-credit-card-fraud-detection) 
This example demonstrates Swarm learning use case on following setup. 
- Based on 1 host  
- Credit card fraud detection dataset
- ML platform is Tensorflow
- SL-ML pairs are spawned using SWOP
        
### [BreakHis](/examples/breakhis)
This example demonstrates Swarm learning use case on following setup. 
- Based on 2 hosts  
- BreakHis dataset
- ML platform is Tensorflow
- SL-ML pairs are spawned using run-sl script
        
### [Cancer prediction](/examples/cancer-pred#cancer-prediction) 
This example demonstrates Swarm learning use case on following setup. 
- Based on 2 hosts  
- Cancer prediction dataset
- ML platform is Tensorflow
- SL-ML pairs are spawned using run-sl script

### [Examples using reverse proxy](/examples/reverse-proxy)
These examples demonstrates Swarm learning using a Reverse proxy server. [For details see](/docs/User/Swarm_Learning_Component_Interactions_using_Reverse_Proxy.md)
- Uses 'services' instead of opening up network ports for connecting among Swarm components
- ML platform is Tensorflow
- SL-ML pairs are spawned using SWOP
        
### [3D Point-Cloud detection ](/examples/point_clouds)
This example demonstrates Swarm learning use case on following setup. 
- Based on 4 hosts  
- kitti 3d object detection dataset
- ML platform is Pytorch
- SL-ML pairs are spawned using run-sl script
