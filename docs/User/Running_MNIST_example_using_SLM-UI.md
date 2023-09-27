# Running MNIST example using SLM-UI {#GUID-E6431502-DE7B-4B09-9B0C-87CD892FC68A .task}

Perform the following steps to run the MNIST two node example using SLM-UI.

1.  Add a Swarm host.

    User can add all hosts where they want to run this project. This example needs two hosts \[ip1 and ip2\]. For more information on adding a host in SLM-UI, see *Adding a Swarm Host in SLM-UI* section in *HPE Swarm Learning Installation and Configuration Guide*.

2.  Create a project in SLM-UI.

    This example can be downloaded from example/mnist folder. For more information on creating a project in SLM-UI, see *Creating a Project in SLM-UI* section in *HPE Swarm Learning Installation and Configuration Guide*.

3.  Create SN \(sentinel\) node by selecting `sn` node in the **Add Swarm Node** screen. Make sure that the sentinel node and the SWCI are started properly from the logs.

    1.  Go to **Host** tab and click on **sentinel IP**. It shows all running containers.

    2.  Click on the SN container to view the logs.

    The SWCI container starts automatically. Users need not to create it manually. User can see the container while clicking on the host where they added the sentinel node. User needs to provide all information as mentioned in the *Adding Swarm Nodes* section in *HPE Swarm Learning Installation and Configuration Guide* to add \[ip1\].

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


**Parent topic:**[Examples](GUID-1F38FA71-0483-40E1-B6DE-1C627C3D50CD.md)

