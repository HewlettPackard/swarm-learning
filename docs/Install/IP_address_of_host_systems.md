# <a name="GUID-1D2971AF-D537-4521-ACAA-D910F50C43E0"/> IP address of host systems

The `--host-ip` and `slhostip` IP addresses in the run scripts and the SWOP profile are the IP addresses of the host machine, where the respective containers are running on the host machine. Based on access, user can even use the FQDN of the host system.

By default, Swarm Learning framework uses a Docker bridge network. For improved isolation, users can even use a user-defined bridge network.

While using the user-defined bridge network, the options `--ip` and `ip` field of `slnetworkopts` in SWOP profile are the IP addresses of the container themselves. This case is specific to the reverse proxy examples or scenarios where user wants to use the fixed IP addresses for containers.


