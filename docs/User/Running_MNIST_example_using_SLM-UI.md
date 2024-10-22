# Running MNIST example using SLM-UI

Perform the following steps to run the MNIST two node example using SLM-UI.

1.  Add a Swarm host.

    This step is optional. User can use this step to install Swarm on hosts where they want to run this project. This example needs two hosts \[ip1 and ip2\]. For more information on adding a host in SLM-UI, see *Installing Swarm Learning using SLM-UI* section in *HPE Swarm Learning Installation and Configuration Guide*.

2.  Create a project in SLM-UI.

    This example can be downloaded from example/mnist folder. For more information on creating a project in SLM-UI, see *Creating a Project in SLM-UI* section in *HPE Swarm Learning Installation and Configuration Guide*.

3.  Create SN \(sentinel\) node by selecting `sn` node in the **Add Swarm Node** screen. Make sure that the sentinel node and the SWCI are started properly from the logs.

    1.  Go to **Host** tab and click on **sentinel IP**. It shows all running containers.

    2.  Click on the SN container to view the logs.

    The SWCI container starts automatically. User does not have to create it manually. User can see the container while clicking on the host where they added the sentinel node. User needs to provide all information as mentioned in the *Adding Swarm Nodes* section in *HPE Swarm Learning Installation and Configuration Guide* to add \[ip1\].

4.  Create a second SN node using the sentinel SN IP address from the dropdown.

5.  In the **Create Node** section drop down, select SWOP \[ip1\] to create SWOP in first node.

6.  In the **Create Node** section drop down, select SWOP \[ip2\] to create SWOP in second node.

7.  Create `MAKE_USER_CONTAINER` task.

    For more information, see *Creating a task* section in *HPE Swarm Learning Installation and Configuration Guide*.

8.  Create `RUN_SWARM` task.

    For more information, see *Creating a task* section in *HPE Swarm Learning Installation and Configuration Guide*.

9.  Execute `MAKE_USER_CONTAINER` task with 2 peers.

    For more information, see *Executing a Task* section in *HPE Swarm Learning Installation and Configuration Guide*.

10. Execute `RUN_SWARM` task with 2 peers.

    For more information, see *Executing a Task* section in *HPE Swarm Learning Installation and Configuration Guide*.

11. Click on the project to view topology.

12. Check the task runner to view the status of the task.


**Parent topic:** [Examples](/examples/README.md)

