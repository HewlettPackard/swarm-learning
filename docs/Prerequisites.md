# Prerequisites for running Swarm Learning

HPE recommends that you run each License Server, SPIRE Server, Swarm
Network node and Swarm Learning node on dedicated systems to get the
best performance from the platform. It is assumed that you have
dedicated systems for each Swarm Learning component, connected to form a
cluster. The requirements for each system are:

-   Hardware

    -   This is a suggestive specification for a Swarm Learning
        platform. The actual implementation can be a VM or a bare-metal
        machine. If using VM ensure AVX instruction set is enabled, 
        it is required for tensorFlow to work. 
        The exact hardware required is a function of the ML
        algorithm\'s complexity.

        -   4 cores

        -   32 GB of RAM

        -   200 GB of storage

        -   1 x 1 GBPS Ethernet

        -   Optionally, NVIDIA GPU for Swarm Learning nodes

-   Network

    -   Up to 3 open ports in each node. See the [*exposed ports*](RunningSL.md#5-exposed-port-numbers) section
        for details of the ports that should be opened. Participating
        nodes should be able to access each other\'s ports.

    -   Internet connectivity for downloading the Swarm Learning package
        and docker images.

-   Host OS &mdash; Linux

    -   Swarm Learning is qualified with Ubuntu 20.04.

-   Architecture

    -   AMD64.

-   Container hosting platform &mdash; either Docker or Kubernetes

    -   Docker

        -   Swarm Learning is qualified with docker 20.10.5.

        -   Configure docker to run as a non-root user. See 16 under [Resource](URL.md) for
            instructions.

        -   Configure network proxy settings for docker. See 17 under [Resource](URL.md) for
            instructions.
            
        -   Configure Docker to use IPV4. 

    -   Kubernetes

        -   Swarm Learning is qualified with Kubernetes 1.19.

-   For GPU enabled services:

    -   NVIDIA driver for GPU services

        -   Swarm Learning is qualified with NVIDIA Tesla K80, P100 and
            V100 GPUs.

        -   Swarm Learning is qualified with NVIDIA driver versions
            396.37 and 440.33.01.

    -   nvidia-docker2 or nvidia-container-toolkit

        -   Swarm Learning is qualified with nvidia-docker2.

-   Machine Learning framework

    -   Keras (TensorFlow 2 backend) or PyTorch based Machine Learning
        models implemented using Python3.

-   Multi system cluster Requirements:

    -   Passwordless SSH setup across systems

    -   **Synchronized time** across all systems
