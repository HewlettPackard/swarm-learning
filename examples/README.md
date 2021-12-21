## Swarm Learning Examples

Several examples of using Swarm Learning are provided with the package. 

## Prerequisite for all examples
Start license server and install valid license before running any of the examples. Refer [Installing licenses and starting license server](../docs/setup.md#installing-licenses-and-starting-license-server).

## Quick start examples:
These quick start examples are designed to run in a single machine and complete in limited time. These examples are aimed for the user who wants to download Swarm Learning images, quickly setup and run to get a feel of it. The steps and scripts for quick start examples are written to run one Swarm Network node and two Swarm Learning nodes on a single machine to simulate decentralized environment. The quick start examples are:  
   1. mnist-keras: It runs decentralized training on MNIST dataset for digit classification using TensorFlow based Swarm Learning framework.
   2. mnist-pytorch: It runs decentralized training on MNIST dataset for digit classification using PyTorch based Swarm Learning framework.
   3. fraud-detection-keras: It runs decentralized training on structured Credit Card Fraud dataset for fraud detection using TensorFlow based Swarm Learning framework.
            
## Multi-node examples:
These examples are designed to run in about 8 to 10 machines and demonstrate the use of multiple configurations of the Swarm Learning framework.

   1. mnist: It runs decentralized training on MNIST dataset for digit classification using TensorFlow and PyTorch.    
   2. CIFAR-10: It runs decentralized training on CIFAR-10 dataset for image classification using TensorFlow.    
   3. fraud-detection: It runs decentralized training on structured Credit Card Fraud dataset for credit card fraud 
       detection using TensorFlow.

See the README file for each example for brief instructions on running them. For a more detailed reference on the Swarm Learning platform and package, see [Readme](../README.md)

## System setup for the multi-node examples
1. The instructions in these examples assume that Swarm Learning will run on 8 to 10 systems. Ensure the [Prerequisites](../docs/Prerequisites.md#prerequisites) are met before the setup.
    - These 10 systems have IP addresses 172.1.1.1, 172.2.2.2, 172.3.3.3, 172.4.4.4, 172.5.5.5, 172.6.6.6, 172.7.7.7, 172.8.8.8, 172.9.9.9 and 172.10.10.10.
    - 172.1.1.1 will run the Sentinel node.
    - 172.4.4.4 will run a Swarm Network node.
    - 172.2.2.2 and 172.3.3.3 will run one Swarm Learning node each. These nodes will register themselves with the Sentinel node that is running on 172.1.1.1.
    - 172.5.5.5 and 172.6.6.6 will also run one Swarm Learning node each. These nodes will register themselves with the Swarm Network node that is running on 172.4.4.4.
    - 172.7.7.7 will run the License Server.
    - 172.8.8.8, 172.9.9.9 and 172.10.10.10 will run one SPIRE server node each, with different configurations. The sample program might use one, two or all three of these servers.

2. Further, these instructions also assume that each of the 4 hosts meant for running Swarm Learning nodes (172.2.2.2, 172.3.3.3, 172.5.5.5 and 172.6.6.6) have 8 NVIDIA GPUs each.

3. Finally, these instructions assume swarm-learning to be the current working directory on all 8 systems:
    `cd swarm-learning`

4. The scripts supplied with the Swarm Learning package do not have the capability to work across systems. So, the instructions must be issued on the right systems:
    - Commands targetting the Sentinel node should be issued on 172.1.1.1.
    - Commands targetting the Swarm Network node should be issued on 172.4.4.4
    - Commands targetting the Swarm Learning nodes that register with the Sentinel node should be issued on 172.2.2.2 and 172.3.3.3.
    - Commands targetting the Swarm Learning nodes that register with the Swarm Network node should be issued on 172.5.5.5 and 172.6.6.6.
    - Commands targetting the License Server node should be issued on 172.7.7.7.
    - Commands targetting the SPIRE server node should be issued on 172.8.8.8, 172.9.9.9 and 172.10.10.10.
