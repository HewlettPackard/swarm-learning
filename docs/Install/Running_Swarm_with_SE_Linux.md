# Running Swarm Learning with SE Linux

**TIP:** User must consult their system administrator before running Swarm with SE Linux in their system or doing any security related changes on the system.

When SE Linux is enabled, it restricts access to various system resources. Before starting Swarm, user must apply appropriate security context labels to `workspace`. For more information, see *Platform specific SE Linux guide*.

To get access to various system resources, user needs to apply `svirt_sandbox_file_t` security context label to `workspace_path` using the `chcon` command.

```
chcon -Rt svirt_sandbox_file_t <workspace_path>
```

For more information, see [docker\_selinux\_security\_policy](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_atomic_host/7/html/container_security_guide/docker_selinux_security_policy).

## SN changes to support SE Linux

For SE Linux environment, `workspace` label set by `chcon` are sufficient.

## SWOP changes to support SE Linux

SWOP needs access to host podman socket which is restricted by default. To get access to host podman socket, user needs to pass the following parameter in `run-swop` script:

```
--docker-socket-file="<podman socket path>"
--security-opt=label=type:container_runtime_t
```

-   `docker-socket-file` parameter exposes `podman.socket` to SWOP container; and
-   `container_runtime_t` label allows the container to interact with the `container.runtime` and access the socket.

**NOTE:**

Paths in SWOP profile need to be labeled with `svirt_sandbox_file_t` security context using the `chcon` command.

## SL or ML changes to support SE Linux

For SE Linux environment, `workspace` label set by `chcon` are sufficient.

