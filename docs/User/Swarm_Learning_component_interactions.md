# <a name="GUID-CE2496F4-22BD-468B-AD40-011E3F113E6E"/> Swarm Learning component interactions

The Swarm nodes interact with each other in many ways using network ports that are dedicated for each purpose:<img width="80%" height="100%" src="/docs/User/Swarm_Learning_component_interaction.png">

|Callout|Description|
|-------|-----------|
|1 \(<strong>SN Peer-to-Peer Port</strong>\)<br>| This port is used by each SN node to share blockchain internal state information with the other SN nodes. The default value of this port is 30303.<br> |
|2 \(<strong>SN API Port</strong>\)<br>| This API server is used by the SL nodes to send and receive state information from the SN node that they are registered with. It is also used by SWCI and SWOP nodes to manage and view the status of the Swarm Learning framework. The default value of this port is 30304.<br> |
|3 \(<strong>SL File Server Port</strong>\)<br>| This port is used by each SL node to run a file server. This file server is used to share insights learned from training the model with the other SL nodes in the network. The default value of this port is 30305.<br> |
|4 \(<strong>License Server API Port</strong>\)<br>| This port is used by the License Server node to run a REST-based API server and a management interface. The API server is used by the SN, SL, SWOP, and SWCI nodes to connect to the License Server and acquire licenses. The management interface is used by Swarm Learning platform administrators to connect to the License Server from browsers and administer licenses. The default value of this port is 5814.<br> |
|5 \(<strong>SWCI API server port</strong>\)<br>|This port is used by the SWCI node to optionally run a REST-based API service. This SWCI API service can be used to control and manage the Swarm Learning framework from a program by using the library provided in the wheels package. The default value of this port is 30306.|
|6 \(<strong>SL_REQUEST_CHANNEL and SL_RESPONSE_CHANNEL</strong>\)<br>|These named pipes (FIFO) are used between each pair of ML and SL nodes for exchanging the model parameters.|
