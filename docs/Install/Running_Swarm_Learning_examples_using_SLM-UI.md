# <a name="GUID-A2B92980-7281-4B0A-989F-33097B7C96A5/"> Running Swarm Learning examples using SLM-UI

SLM-UI containers are automatically started by the SLM-UI installer. But, if it is not running on the host, users need to manually start it using the commands. For more information, see [Starting SLM-UI manually](Starting_SLM-UI_manually.md).

Before you start using the SLM-UI, HPE recommends you to read the [Documentation](/README.md#documentation) section to understand about the architecture     of Swarm Learning, how these nodes work, how model training happens, and Swarm Learning Concepts section.

Perform the following steps to run the SL examples using SLM-UI.

1.  For ease of use, users can extract the examples folder from the documentation tar ball on their laptops.

2.  Users must generate x.509 certificates for their own environment. HPE-provided utility under swarm-learning/examples/utils can be used for generating self-signed certificates just for the purposes of running the examples. Ensure that these certificates are available on the laptop.

3.  User can use the provided template files and the generated certificates for the examples from the laptop and import them into the SLM-UI installer.

      **NOTE:** HPE recommends that users use their own certificates in actual production environment.
  
To run the Swarm Learning examples using SLM-UI, perform the following steps:

1.  [Adding a Swarm Host](Adding_a_Swarm_Host_in_SLM-UI.md)

2.  [Creating a Project](Creating_a_Project_in_SLM-UI.md)

3.  [Adding Swarm Nodes](Adding_Swarm_Nodes.md)

4.  [Creating a Task](Creating_a_task.md)

5.  [Creating Task Runners](Creating_Task_Runners.md)

6.  [Creating a Contract](Creating_a_Contract.md)

7.  [Executing a Task](Executing_a_Task.md)

8.  [Managing the Global Settings](Managing_the_Global_Settings.md)


