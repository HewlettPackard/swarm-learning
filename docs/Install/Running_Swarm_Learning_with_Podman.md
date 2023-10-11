# Running Swarm Learning with Podman

-   Install podman-base package `podman`.

-   Install `podman-docker` package from system package manager. This package maps docker commands to respective podman commands.

-   Enable `podman.socket`. It can be root or rootless. For more information on setting rootless podman socket, see [https://docs.podman.io/en/latest/markdown/podman-system-service.1.html](https://docs.podman.io/en/latest/markdown/podman-system-service.1.html).

**Note:**

  - Shorthand registry names may not work with podman. For more information, see _Short-name aliases_ section in [www.redhat.com/sysadmin/manage-container-registries](https://www.redhat.com/sysadmin/manage-container-registries).
  - ML or User container running as non-root may fail due to permission issue while saving trained model file. User
needs to precreate a directory with full permissions.
  - GPU based local training is not supported through Podman.
  - SLM-UI is not supported with Podman.


