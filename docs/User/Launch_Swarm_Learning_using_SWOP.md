# <a name="GUID-B3F03E6D-20B1-473C-B846-153C03FE01CB"/> Launch Swarm Learning using SWOP

SWOP components obtain information about other components from the SWOP profile file supplied by the user. This profile file is used at start up to initialize the SWOP component, create containers, and build new containers. The SWOP profile file must conform to the schema specified in the `profile-schema.yaml` file. The SWOP profile file specifies the following component information:

-   Name of the group.

-   The number of SL nodes in the group.

-   Taskrunner contract of the group.

-   Infrastructure information such as APLS, SPIRE, and SN

-   Environmental variables \(optional\)


The SWOP container must be started by the user by providing the YAML profile file and `run-swop` script along with other parameters.

