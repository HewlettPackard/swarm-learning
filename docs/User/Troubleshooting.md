# <a name="GUID-96BB1337-2B99-45C7-BA9F-3D7D3B76663E"/> Troubleshooting

Troubleshooting provides solutions to commonly observed issues during Swarm Learning set up and execution.

## <a name="GUID-EDAB2731-9CF3-4770-B54C-40C56D2FFDAC"/> Error code: 6002

```
> Error message: Unable to connect to server. Server might be wrongly configured or down.
> Custom message: Error in communicating with server https://HOST_SYSTEM_IP:5814 (default port)
```

**Problem description**

Error code: 6002, as shown in the following screenshot occurs when Swarm Learning components are not able to connect to the APLS server.![Troubleshooting_image](GUID-28273425-4E6F-425D-8A32-339013B86F75-high.png)

**Resolution**

1.  Verify if License Server is running.

    On the License Server host, verify if it is running, if not, restart the License Server.

    For more information about restarting the License Server, see *AutoPass License Server User Guide*.

2.  Access the APLS web management console. If the browser cannot connect, verify the network proxy settings, firewall policies, that are in effect. If required, work with your network administrator to resolve.

3.  Verify if the Swarm licenses are installed using APLS web management console. For more information, see .


