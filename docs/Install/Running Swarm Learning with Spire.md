# SPIFFE
Secure Production Identity Framework for Everyone (SPIFFE): The SPIFFE standard provides a specification for a framework capable of bootstrapping and issuing identity to services that work across heterogeneous environments and organizational boundaries. 

## Components of SPIFFE: 
- SPIFFE ID: One which standardizes an identity namespace. It is a URI that serves as the "name" of an entity.
- SPIFFE Verifiable Identity Document (SVID): One which dictates how an issued identity is presented and verified. An SVID is a document that carries the SPIFFE ID. SVID includes cryptographic properties that allow it to be proven as authentic and proven to belong to the presenter. The supported document types are an X.509 certificate or a JWT token.
- Workload API: One which specifies an API through which identity may be retrieved and/or issued. The SPIFFE Workload API is the method through which workloads, or compute processes, obtain their SVID(s). It is typically exposed locally (eg. via a Unix domain socket). The Workload API also delivers the CA bundles, and these bundles are associated with trust domains outside of the issued SVID and are used for federation. 

# SPIRE
SPIRE is a SPIffe Run time Environment. Spire follows the spiffe standard and does the following: 
- Node and workload attestation
- Securely issues SVIDs to workloads
- Verifies the SVIDs of other workloads
- Exposes the SPIFFE Workload API
- Attests running software systems
- Issues SPIFFE IDs and SVIDs to software systems

# Running Swarm Learning with Spire

