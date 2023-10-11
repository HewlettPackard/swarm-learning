## Prerequisites

HPE recommends that you run each Swarm Network node, and Swarm Learning node on dedicated systems to get the best performance from the platform.

The recommended requirements for each system are as follows:

<blockquote>
  
NOTE:Configuration of the ML user nodes are driven by the complexity of the ML algorithm. GPUs may be needed.

</blockquote>

## <a name="GUID-8944D617-0D1D-40B5-B3A2-089887148125"/> Hardware

-   Any x86-64 hardware

-   System memory of 32 GB or more

-   Hard disk space of 200 GB or more

-   Qualified with HPE Edgeline, Proliant DL380, and Apollo 6500


## <a name="GUID-A378E927-47A1-4809-BF60-82700A884002"/> Network

-   A minimum of one or a maximum four open TCP/IP ports in each node. All swarm nodes **must be able to access** the ports of every other node. For more information on port details that must be opened, see [Exposed ports](Exposed_port_numbers.md).

-   Stable internet connectivity to download Swarm Learning package and Docker images.


## <a name="SECTION_DXX_P12_JSB"/> Operating systems

-   Linux - Qualified on Ubuntu 20.04, RHEL 8.5, SLES 15.

-   For Swarm SLM-UI installer, any x86-64 hardware running Linux, Windows, or Mac.


## <a name="SECTION_JCW_Q12_JSB"/> Container hosting platform

-   HPE Swarm Learning is qualified with Docker 24.0.5 and Podman 3.4.4. Configure Docker/Podman to use IPv4. For more details on Podman, see [Running Swarm Leaning with Podman](Running_Swarm_Learning_with_Podman.md).

-   Configure Docker to run as a non-root user. For more details, see [Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

-   Configure network proxy settings for Docker. For more details, see [HTTP/HTTPS proxy](https://docs.docker.com/config/daemon/systemd/#httphttps-proxy).



## <a name="SECTION_SMY_512_JSB"/> Machine Learning framework

Qualified with Keras 2.9.0 \(TensorFlow 2 backend\) and PyTorch 1.5 based Machine Learning models implemented using Python3.

<blockquote>

  NOTE: Python version must be between 3.6 to 3.9.

</blockquote>

## <a name="SECTION_BMS_BN4_RSB"/> Multi system cluster requirements

-   Synchronized time across all systems using NTP.


<blockquote>

  NOTE:'Qualified' in this section means that HPE has qualified the product with the respective versions. Swarm Learning may work with other versions as well.

</blockquote>

