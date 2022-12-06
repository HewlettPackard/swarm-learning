# <a name="GUID-AC94A4EE-75B2-4381-9B79-94E4037D6DE9"/> Exposed port numbers

Depending on the type of Swarm Learning components that are running on a host, some or all these ports must be opened to allow the Swarm Learning containers to communicate with each other:

-   A Swarm Network peer-to-peer port on the hosts running Swarm Network nodes. By default, port 30303 is used.

-   A Swarm Network API server port on the hosts running Swarm Network nodes. By default, port 30304 is used.

-   Swarm Learning file server port on the hosts running Swarm Learning nodes. By default, port 30305 is used.

-   A License Server API port on the host running the License Server. By default, port 5814 is used.

-   \(Optional\). An SWCI API server port that is used by the SWCI node to run a REST based API service. By default, port 30306 is used.

<blockquote>
    NOTE:<br> </br>   1. If you use different ports other than the default port, you must open those ports accordingly. For instance, in our MNIST example, we are using ports 16000 and 18000 for the SL File server ports, which must be opened.<br> </br>
    2. If you use a reverse proxy, you need to open only the SN peer-to-peer port (30303) for each SN node.

</blockquote>


