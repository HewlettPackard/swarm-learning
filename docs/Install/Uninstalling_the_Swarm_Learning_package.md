# <a name="GUID-9B602231-E16D-4F02-8FA5-567825277484"/> Uninstalling the Swarm Learning package

Use the `swarm-learning/scripts/bin/uninstall` script to uninstall the Swarm Learning package. This script does not accept command line parameters. It should be run on every node where Swarm Learning package is installed.

On the host where it is run, the script stops all Swarm Learning components removes the docker container images, and deletes the "docs", "examples", and the "scripts" directories installed under `swarm-learning`.

<blockquote>
CAUTION:

-   This command deletes all user created artifacts under the "examples" directory.

-   If needed, any log output produced by the containers must be saved before invoking the script. Logs are not available after the script is executed.

-   Also, the output files that have been written under the “examples” directory by previous runs may need to be saved.


</blockquote>
