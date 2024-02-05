# SPIFFE
Secure Production Identity Framework for Everyone (SPIFFE): The SPIFFE[1] standard provides a specification for a framework capable of bootstrapping and issuing identity to services that work across heterogeneous environments and organizational boundaries. 

## Components of SPIFFE:
- SPIFFE ID: One which standardizes an identity namespace. It is a URI that serves as the "name" of an entity.
- SPIFFE Verifiable Identity Document (SVID): One which dictates how an issued identity is presented and verified. An SVID is a document that carries the SPIFFE ID. SVID includes cryptographic properties that allow it to be proven as authentic and proven to belong to the presenter. The supported document types are an X.509 certificate or a JWT token.
- Workload API: One which specifies an API through which identity may be retrieved and/or issued. The SPIFFE Workload API is the method through which workloads, or compute processes, obtain their SVID(s). It is typically exposed locally (eg. via a Unix domain socket). The Workload API also delivers the CA bundles, and these bundles are associated with trust domains outside of the issued SVID and are used for federation. 

# SPIRE
SPIRE[2] is a SPIffe Run time Environment. SPIRE follows the SPIFFE standard and does the following: 
- Node and workload attestation
- Securely issues SVIDs to workloads
- Verifies the SVIDs of other workloads
- Exposes the SPIFFE Workload API
- Attests running software systems
- Issues SPIFFE IDs and SVIDs to software systems

## Components of Spire
SPIRE has two major components: 
- Spire Server which is responsible for authenticating agents and minting SVIDs
- Spire Agent which is responsible for serving the SPIFFE Workload API. 

## Spire usage
SPIRE can be used in 3 different ways 
- Standalone - Installing spire on a dedicated machine.
- Docker Compose / Docker - Installing it in a docker container.
- Kubernetes – Installing in K8S via kubectl.
  
Although the spire can be run in multiple ways, since Swarm core components are docker images, it is ideal to make use of the spire via the docker images itself. Docker images are available for both spire-agent and spire-server via ghcr(git hub container registry) or cgr(chain guard registry). Both the docker images can be easily started by setting up the respective configuration files (`server.conf`, `agent.conf`) appropriately. One can try the quick start example[3] that uses docker-compose Or can refer to the vanilla docker[4] way of spire execution. To understand the SPIRE and SPIFFE concepts in detail, one can refer to the book called Solving the Bottom Turtle [5].

# Running Swarm Learning with Spire

Due to the federative nature of Swarm Learning, it will mostly have multiple hosts and multiple organizations involved in swarm training. For details on how to actually run with SPIRE, refer the [Spire with CIFAR-10](../../examples/spire/cifar10/README.md).

To run Swarm Learning using SPIRE on a multi-host setup, HPE recommends to proceed with the following steps:
- Each host should have its own spire-agent container running.
- It is recommended to have seperate join token for each spire agent.
- Entry creation is specific to each swarm component. No need to create multiple entries in the spire server for the same component.

To run Swarm Learning using a federated spire[6] setup, HPE recommends to proceed with the following steps: 
- Each Org will have its own spire server started.
- The federation block of the `server.conf` holds the information of other spire servers in the federation.
- Along with the spire server API port (default 8081), we need an additional port (default is 8443) for the federation service.
- A Bundle file will be created at each spire server and exchanged with other spire servers for federation.
- Workload entries are specific to each spire server. For example, the entry of sn workload should be done on each org where sn exists. 

Note: Identifying of workload will happen via the selector defined while creating an entry to the spire server. Always make sure if an env is used while creating an entry, then the same should be used in the docker run command. If a label is used while creating the entry, then the same should be used in the docker run command.

[1] https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE.md

[2] https://github.com/spiffe/spire

[3] https://spiffe.io/docs/latest/try/spire101/

[4] https://github.com/spiffe/spire/blob/v1.8.4/doc/plugin_agent_workloadattestor_docker.md

[5] https://spiffe.io/pdf/Solving-the-bottom-turtle-SPIFFE-SPIRE-Book.pdf

[6] https://spiffe.io/docs/latest/architecture/federation/readme/


