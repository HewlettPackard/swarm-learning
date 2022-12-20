Reverse Proxy with CIFAR-10
========

This example runs Reverse Proxy with CIFAR-10 [1] on the Swarm Learning platform. It uses TensorFlow as the backend.

The code for this example has been modified to run on a Swarm Learning platform.

This example uses cifar10 dataset distributed along with tensorflow package. The ML program, after conversion to Swarm Learning, is in `swarm-learning/examples/reverse-proxy/cifar10/model` and is called `cifar10.py`. It contains a tiny ML model for the purpose of showing steps of converting ML code to Swarm Learning. 

As this example runs CIFAR example using reverse proxy, to mimic the real world behaviour this example uses BIND9 [2] as DNS server and NGINX [3] as the reverse proxy server and builds both the  docker images with suitable configurations (Please refer to the respective docker files). For user convenience, this example has patially automated the flow of running cifar 10 example that includes starting of the BIND9 and NGINX containers. Please refer to `run-prerequisites`, `run-on-host-1` and `run-on-host-2` scripts and their arguments required to run the respective run scripts of swarm components.

This example shows the Swarm training of CIFAR-10 model using four Machine Learning (ML) nodes. Machine Learning nodes are automatically spawned by Swarm Operators (SWOP) nodes running on two different hosts. Swarm training is initiated by Swarm Command Interface (SWCI) node and orchestrated by two Swarm Network (SN) nodes.

## Cluster Setup

The cluster setup for this example uses 1 host, as shown in the figure below:  
- host-1: 172.1.1.1
- host-2: 172.2.2.2  

|<img width="60%" height="50%" src="../../figs/reverse-proxy-cifar-setup.png">|
|:--:|
|<b>Figure 1: Cluster setup for the Reverse Proxy with CIFAR-10 example</b>|

1. This example uses two Swarm Network (SN) nodes. The names of the docker containers representing these two nodes are **sn-1** and **sn-2**. Where **sn-1** is the Sentinel Node and it runs on host 172.1.1.1 while **sn-2** is a Non-Sentinel Node that runs on host 172.2.2.2.
2. Swarm Learning (SL) and Machine Learning (ML) nodes are automatically spawned by Swarm Operator (SWOP) nodes during training.
3. This example uses two SWOP nodes - one connects to each SN node. The names of the docker containers representing these SWOP nodes are **swop-1** that runs on host 172.1.1.1 and **swop-2** that runs on host 172.2.2.2.
4. Training is initiated by SWCI node (**swci-1**) that runs on host 172.1.1.1
5. Example assumes that License Server already runs on host 172.1.1.1. All Swarm nodes connect to the License Server, on its default port 5814.

## DNS Configuration on both hosts
SNo | FQDN | IP Address |
--- | --- | --- | 
1 | api.sn-1.swarm | 172.1.1.1 | 
2 | p2p.sn-1.swarm | 172.1.1.1 | 
3 | fs.sl-1.swarm | 172.1.1.1 | 
4 | fs.sl-2.swarm | 172.1.1.1 | 
5 | api.sn-2.swarm | 172.2.2.2 | 
6 | p2p.sn-2.swarm | 172.2.2.2 | 
7 | fs.sl-3.swarm | 172.2.2.2 | 
8 | fs.sl-4.swarm | 172.2.2.2 | 

## NGINX Configuration on Host-1
SNo | FQDN | IP Address |
--- | --- | --- | 
1 | api.sn-1.swarm | 172.1.1.1:30304 | 
2 | p2p.sn-1.swarm | 172.1.1.1:30303 | 
3 | fs.sl-1.swarm | 172.1.1.1:40001 | 
4 | fs.sl-2.swarm | 172.1.1.1:40002 | 

## NGINX Configuration on Host-2
SNo | FQDN | IP Address |
--- | --- | --- | 
1 | api.sn-2.swarm | 172.2.2.2:30304 | 
2 | p2p.sn-2.swarm | 172.2.2.2:30303 | 
3 | fs.sl-3.swarm | 172.2.2.2:40001 | 
4 | fs.sl-4.swarm | 172.2.2.2:40002 | 

## Running the CIFAR example using Reverse Proxy

1. *On both host-1 and host-2*:</br>
   cd to `swarm-learning` folder (i.e. parent to examples directory).
2. *On host-1*:</br>
   Run `run-prerequisites` script. It accepts the host index as the argument. Use index 1 as argument while running on host-1. Here 1 and 2 are the indexes of the respective hosts. Run the command like below 
   
   ```
   .\examples\reverse-proxy\cifar10\run-prerequisites 1
   ```
      This will create workspace directory, moves files from examples to workspace, create a common path between hosts for ml program, generate certificates and creates volume for the wheel file.
3. *On host-2*:</br>
   Now use the argument as 2 to `run-prerequisites` on host-2. Run the command like below 
   
   ```
   .\examples\reverse-proxy\cifar10\run-prerequisites 2
   ```
      This will create workspace directory, moves files from examples to workspace, create a common path between hosts for ml program, generate certificates and creates volume for the wheel file.
4. *On host-1*:</br>
   Share the certificate of host-2 to host-1
   
   ```
   scp host-2:<PATH>workspace/reverse-proxy/cifar10/cert/ca/capath/ca-2-cert.pem workspace/reverse-proxy/cifar10/cert/ca/capath
   ```
5. *On host-2*:</br>
   Share the certificate of host-1 to host-2
   
   ```
   scp host-1:<PATH>workspace/reverse-proxy/cifar10/cert/ca/capath/ca-1-cert.pem workspace/reverse-proxy/cifar10/cert/ca/capath
   ```
6. *On host-1*:</br>
   Run the `run-on-host-1` script  from the `swarm-learning` folder with `APLS_IP` argument, `Host_IP_1`, `Host_IP_2`, and `Host_DNS_IP`. Here Host_DNS_IP is the DNS IP of the host-1. This will ensure the SL and ML contianer to use two DNS IP's for name resolution. One of it is host DNS IP and the another is the DNS IP of the bind9 container. Run command like below 
   ```
   .\examples\reverse-proxy\cifar10\run-on-host-1 172.1.1.1 172.1.1.1 172.2.2.2 172.3.3.3
   ```
    Above step will take care of starting Bind9 container, Nginx container and rest of all the swarm containers specific to *host-1* in the sequential manner. All the run-script commands will now take FQDN's as service parameter arguments instead of ports. NOTE: SN-P2P-PORT still needs 30303 port in the host machine where SN container runs.
7. *On host-2*:</br>
      Run the `run-on-host-2` script  from the `swarm-learning` folder with `APLS_IP` argument, `Host_IP_1`, `Host_IP_2`, and `Host_DNS_IP`. Here Host_DNS_IP is the DNS IP of the host-2. This will ensure the SL and ML contianer to use two DNS IP's for name resolution. One of it is host DNS IP and the another is the DNS IP of the bind9 container. Run command like below 
      
   ```
      .\examples\reverse-proxy\cifar10\run-on-host-1 172.1.1.1 172.1.1.1 172.2.2.2 172.4.4.4
   ```
      Above step will take care of starting Bind9 container, Nginx container and rest of all the swarm containers specific to *host-2* in the sequential manner. All the run-script commands will now take FQDN's as service parameter arguments instead of ports. NOTE: SN-P2P-PORT still needs 30303 port in the host machine where SN container runs.  
8. Swarm training is automatically started when the run task (swarm_mnist_task) gets assigned and executed. User can open a new terminal on either host-1 or host-2 to monitor the docker logs of ML nodes for Swarm training. Swarm training will end with the following log message at the end
    - `SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.`  
7. Final Swarm model will be saved inside `workspace/reverse-proxy/cifar10/model` directory on both host-1 and host-2. All the dynamically spawned SL and ML nodes will exit after Swarm training. The SN and SWOP nodes continue running.
8. To clean-up, run the `scripts/bin/stop-swarm` script on the host system to stop and remove the swarm container nodes of the previous run. If needed, take backup of the container logs. As this example builds and starts Bind9 and Nginx, please remove their respective images and containers. Finally remove docker volume (`sl-cli-lib`) and delete the `workspace` directory.
        

**Parent topic:**[Examples using reverse proxy](../README.md)

[1] V.N. a. G. H. Alex Krizhevsky, "CIFAR-10 and CIFAR-100 datasets," [Online]. Available: https://www.cs.toronto.edu/~kriz/cifar.html

[2] https://www.isc.org/bind/ and https://bind9.readthedocs.io/

[3] https://www.nginx.com/ and https://nginx.org/en/docs/
