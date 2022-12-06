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

3.  Verify if the Swarm licenses are installed using APLS web management console. For more information, see APLS User Guide.


## Installation of HPE Swarm Learning on air-gaped systems or if the Web UI Installer runs into any issue and not able to install

- Download the following from HPE My Support Center(MSC) on a host system that has internet access - tar file (HPE_SWARM_LEARNING_DOCS_EXAMPLES_SCRIPTS_Q2V41-11033.tar.gz) and the signature file for the above tar file.
- Untar the tar file under `/opt/hpe/swarm-learning`.
- Do a docker login from your host:
   `docker login hub.myenterpriselicense.hpe.com –u <YOUR-HPE-PASSPORT-EMAIL> -p hpe_eval`
- Pull the signed Swarm Learning images from HPEs Docker Trust Registry (DTR):
   ```
   docker pull hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning/sn:<latest Swarm Learning Version (for example, 1.2.0)>
   docker pull hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning/sl:<latest Swarm Learning Version>
   docker pull hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning/swci:<latest Swarm Learning Version>
   docker pull hub.myenterpriselicense.hpe.com/hpe/swarm-learning/swop:<latest Swarm Learning Version>
   ```
- Copy the tar file and Docker images to the air-gaped systems.

## System resource issues if too many SLs are mapped to the same SN

When configuring Swarm Learning you may encounter system resource issues if too many SLs are mapped to same SN. For example:
    ```
    “swarm.blCnt : WARNING: SLBlackBoardObj : errCheckinNotAllowed:CHECKIN NOT ALLOWED”
    ```
The suggested workaround is to start with mapping 4 SL to 1 SN. Then after, slowly scale no of SLs to SN

## SWCI waits for task-runner indefinitely even after task completed or failed

User to ensure no failure in ML code before Swarm training starts. Check using `SWARM_LOOPBACK ENV` and ensure, user coderuns fine and local training completes successfully.

# Generic troubleshooting tips

- x.509 certificates are not configured correctly – See [https://www.linuxjournal.com/content/understanding-public-key-infrastructure-and-x509-certificates](https://www.linuxjournal.com/content/understanding-public-key-infrastructure-and-x509-certificates).
- License server is not running or Swarm licenses are not installed - See chapter "HPE AutoPass License Server License Management" in **AutoPass License Server User Guide** for details of the web GUI management interface and how to install license.
- Swarm core components (Docker containers) are not started or errors while starting. – For more information on how to start Swarm Learning, see [Running Swarm Learning](/docs/Install/Running_Swarm_Learning.md).
- Swarm components are not able to see each other - See the [Exposed Ports](/docs/Install/Exposed_port_numbers.md) to see if the required ports are exposed.
- User is not using the Swarm APIs correctly – See [Swarm Wheels Package](/docs/User/Swarm_client_interface-wheels_package.md) for details of API.
- Errors related to SWOP task definition, profile schema, or SWCI init script – These are user defined artifacts. Verify these files for correctness.
- Any experimental release of Ubuntu greater than LTS 20.04 may result in the following error message when running SWOP tasks.
  ```SWOP MAKE_USER_CONTAINER fails.```
  This occurs as SWOP is not able to obtain image of itself because of Docker setup differences in this experimental Ubuntu release. Switch to 20.04 LTS to resolve  this issue.
