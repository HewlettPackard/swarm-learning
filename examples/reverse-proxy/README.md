# Examples using reverse proxy

## Prerequisite for running reverse Proxy examples

1.  Reverse proxy examples use NGINX and BIND9 as custom Docker images to build it. Both of these images use Ubuntu 22.04 as the base image, along with some image-specific apt-get packages. Make sure these packages and images are downloaded properly while running the scripts within these examples.

2.  Before running these examples, make sure APLS is already running. Also, ensure wheel file with its symbolic link are placed under the `lib` directory.

3.  Reverse proxy examples runs the containers with fixed IP addresses. This is needed because we pre-configure the Nginx with IP addresses of SWARM containers before they start. For a default bridge networks there are more chances of IP conflicts or the docker command will not consider the ip passed. Hence it is recommended to create a seperate non-default(custom) bridge network to start contianers with predefined IP addresses. 

    One may use command like below to create their own network. In this command, `<subnet-ip>` can be an IP other than default docker bridge network's subnet. For example, if default bridge uses 172.18.0.0 subnet then one can use something like 192.18.0.0 and `<network-name>` would be a string that will be used as an argument to the run scripts of these examples.
    ```
    docker network create --subnet=<subnet-ip>/16 <network-name>
    ```
4.  The NGINX container started by these examples will by default use 443 port. Please make sure there is no other service that is already running on this 443 port. 

5.  In these reverse proxy examples, build task will pull docker images along with some packages and run task will pull datasets from the external sites. Please make sure to add necessary proxy configurations in the swop profiles before running the automated scripts. 


**NOTE:**

All reverse proxy-based examples are in the `examples/reverse-proxy` folder. NGINX and BIND9 Docker files are specified in the `examples/reverse-proxy/common` folder. The configuration file of NGINX, called `nginx.conf`, is present in the respective example of the reverse proxy.


## Working of Reverse Proxy Examples  

1.  DNS and Proxy modifications are needed to run Swarm Learning using reverse proxy mode. As these modifications are plenty, these examples are curated to handle these modifications automatically.
2.  Bind9 as a docker container is used as a DNS server for these examples to resolve the Fully Qualified Domain Names to IP address.
3. If the user wants to use their local DNS server instead of Bind9 as a container, then they should have enough privilege to add IP and FQDN mapping to the local `named.conf` file. Please note that the location of this file is specific to the type of operating system.
4. Bind9 container created from these examples has a built-in function called "add-dns" to add the mapping into the running DNS bind9 container.
5. On the other hand, routing/tunneling of requests using a reverse proxy is managed by running the NGINX as a docker container.
6. Routing configuration in NGINX is managed by using `nginx.conf` file, it is volume mounted before the start of the Nginx container.
7. These examples run the container with pre-configured `nginx.conf` files and the container IP addresses used in this configuration file are the IPs adjacent to the Bind9 container. Hence for these examples, it is recommended to keep these container IPs available.
8. If the user wants to use custom IP addresses, then they have to alter their `nginx.conf` according to their needs and start the NGINX container.
