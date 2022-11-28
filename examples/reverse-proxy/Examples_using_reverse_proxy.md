# Examples using reverse proxy {#GUID-DD2A624E-30B8-4FCD-A23F-014AE0D76452 .concept}

## Prerequisite for running reverse Proxy examples {#SECTION_TC3_XYY_NVB .section}

1.  Reverse proxy examples use NGINX and BIND9 as custom Docker images to build. Both of these images use Ubuntu 22.04 as the base image, along with some image-specific apt-get packages. Make sure these packages and images are downloaded properly while running the scripts within these examples.

2.  Before running these examples, make sure APLS is already running.


**NOTE:**

All reverse proxy-based examples are in the examples/reverse-proxy folder. NGINX and BIND9 Docker files are specified in the examples/reverse-proxy/common folder. The configuration file of NGINX, called nginx.conf, is present in the respective example of the reverse proxy.

-   **[MNIST using Reverse Proxy](GUID-9BD49A0E-88FF-4F9F-B722-CE9E1AF1CE5B.md)**  


