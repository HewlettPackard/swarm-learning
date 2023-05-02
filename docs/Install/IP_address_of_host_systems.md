# <a name="GUID-1D2971AF-D537-4521-ACAA-D910F50C43E0"/> IP address of host systems

By default, Swarm Learning framework uses a Docker bridge network. For improved isolation, users can even use a user-defined (custom) bridge network.

The `--host-ip` and `slhostip` IP addresses in the run scripts and the SWOP profile are the "IP addresses" of the host machine, where the respective containers are running. If user-defined docker bridge network is used, one can even use the FQDN of the host system.

While using the user-defined bridge network, the options `--ip` for run-scripts and `ip` field of `slnetworkopts` in SWOP profile are the IP addresses of the container (not host IP). This case is specific to the reverse proxy examples or scenarios where user wants to use fixed IP address for containers.


