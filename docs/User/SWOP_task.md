# <a name="GUID-AF9F2109-FE92-4BFE-8566-E48DCC0B51A6"/> SWOP task

-   A Task is a reusable unit of work relevant for SWARM LEARNING Operations. For example, [swarm\_mnist\_task](/examples/mnist/README.md), runs the MNIST demo using SL and ML nodes.

-   A Task is defined by the user.

-   A Task has a prerequisite, a body, and an outcome. Tasks can be used to build on "outcomes" created by other tasks. For example, a build task becomes a prerequisite for a `run-swarm` task that runs a ML program.

-   Tasks can be chained together to create linear workflows.

-   Tasks are instantiated according to schema specified in the **TASK SCHEMA YAML** file.

-   Currently supported Task types are:

-   RUN\_SWARM—A task to run an ML program in the Swarm Learning Network.

-   MAKE\_SWARM\_USER\_CONTENT—A task to create a Docker volume that contains artifacts to execute the ML program including the ML program itself.

-   BUILD\_SWARM—A task with the instructions to build a user Docker container in place.

-   PULL\_IMAGE—A task to pull a prebuilt Docker image.


