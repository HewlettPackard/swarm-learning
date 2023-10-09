# <a name="GUID-AE96088D-D29A-4813-8EB6-506422459068"/> Stopping Swarm Learning node

Use the `swarm-learning/scripts/bin/stop-swarm` script to stop all Swarm Network and Swarm Learning nodes that are running on a host system.

<blockquote>
NOTE:This script does not operate across systems. It must be invoked on each host system to stop the Swarm Learning platform completely.

</blockquote>
This script accepts the following parameters:

|Parameter name|Description|Default value|
|--------------|-----------|-------------|
|`--all`|This parameter stops all components, SL, SN, SWCI, and SWOP.|None|
|`--sl`|This parameter stops Swarm Learning nodes.|None|
|`--sn`|This parameter stops Swarm Network nodes.|None|
|`--swci`|This parameter stops SWCI nodes.|None|
|`--swop`|This parameter stops SWOP nodes.|None|
|`--keep`| This parameter keep stopped containers - they are removed by default.<br> This parameter is optional. When it is specified, the containers are stopped but not removed. In this case, the Log output from the containers are still available after the script has run. The leftover containers can be removed, either manually or by invoking this script again without the `--keep` parameter.<br> |None|
|`--sudo`|This parameter specifies that sudo must be used when invoking Docker to stop or remove the Swarm Learning nodes.|None|

