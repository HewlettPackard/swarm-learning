# Prerequisite for all examples
1. Start license server and install valid license before running any of the examples. Refer Installing licenses and starting license server.


# Swarm Learning Examples
Below examples of using Swarm Learning are provided with the package:  
    1. MNIST (`swarm-learning/examples/mnist`)  
    2. MNIST-PYT (`swarm-learning/examples/mnist-pyt`)  
    3. CIFAR-10 (`swarm-learning/examples/cifar10`)  
    4. Credit card fraud detection (`swarm-learning/examples/fraud-detection`)  
    5. Reverse Proxy based examples (`swarm-learning/examples/reverse-proxy`)  
    
They use different models, data, platforms and Swarm cluster configurations. Each example requires valid certificates to be used by different Swarm Learning components. A certificate generation utility (`gen-cert`) is provided under `swarm-learning/examples/utils` folder so that user can quickly generate certificates and run the examples.

```
./swarm-learning/examples/utils/gen-cert -h
Usage: gen-cert -e EXAMPLE-NAME -i HOST-INDEX
        -e Name of the example e.g. mnist, mnist-pyt, cifar10 etc.
        -i Host index like 1,2 etc.
        -h Show help.
```

**Note: It is strongly recommended that users must use their own certificates in actual production environment.**

See the README file for each example for brief instructions on running them. For a more detailed reference on the Swarm Learning platform and package, see the Swarm Learning Installation and Configuration Guide. This document can be found in the `swarm-learning/docs/` directory.

## System setup for the examples
1. The instructions in these examples assume that Swarm Learning will run on 1 to 2 host systems.
    - These systems have IP addresses 172.1.1.1 and 172.2.2.2.
    - License server is installed on 172.1.1.1 and running on default port 5814.
    - 172.1.1.1 will run the Sentinel Swarm Network node.
    - MNIST example has one more Swarm Network (SN) node. 172.2.2.2 will run the other Swarm Network node. A Swarm Learning (SL) and Machine Learning (ML) node pair will be spawned across these 2 host systems - 172.1.1.1 and 172.2.2.2. 
    - Spawning of SL and ML nodes can be automatic or manual.
    - Swarm Operator (SWOP) node, running on each host system, takes care of spawning them automatically using the task framework. MNIST example shows how Swarm training can be launched in automatic way using Swarm Command Interface (SWCI) and Swarm Operator (SWOP) nodes. SWCI runs on 172.1.1.1 whereas Swarm Operator runs on both 172.1.1.1 and 172.2.2.2 hosts.
    - CIFAR-10 example shows how Swarm training can be manually launched using run-sl script on each host.
    - Model training will start once minimum number (minPeers) of specified ML nodes are launched either automatic or manual way.
	- After training final Swarm model will be saved by each ML node
2. The files created under the workspace directory that includes certs, models, data etc., are expected to have the minimum file permission as 664. Once the files are copied to workspace directory check the permissions of the files inside it. If desired permissions are not met one might observe `file permission denied` in the respective swarm component's docker logs. To overcome such cases, upfront please change the permission of the files by using `chmod` command. 
3. Finally, these instructions assume swarm-learning to be the current working directory on all the systems:
    `cd swarm-learning`
