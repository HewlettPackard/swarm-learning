# Uninstalling Swarm Learning using SLM-UI

In the **Hosts** tab, user needs to click the delete icon next to each of the hosts where user wants to uninstall the product. This stops all Swarm Learning components on that host, removes the docker container images, and deletes the "docs", "examples", and the "scripts" directories installed under `swarm-learning`.

<blockquote>
CAUTION:

-   This command deletes all user created artifacts under the `examples` directory.
-   If needed, any log output produced by the containers must be saved before invoking the script. Logs are not available after the script is executed.
-   Also, the output files that have been written under the `examples` directory by previous runs may need to be saved.
</blockquote>

**Parent topic:** [HPE Swarm Learning Installation](HPE_Swarm_Learning_installation.md)

