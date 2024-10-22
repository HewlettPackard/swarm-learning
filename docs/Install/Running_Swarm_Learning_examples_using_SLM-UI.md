# <a name="GUID-A2B92980-7281-4B0A-989F-33097B7C96A5/"> Running Swarm Learning examples using SLM-UI


**TIP:**

![](GUID-4D9096A6-6206-4F26-AC88-20CC85208ED3-high.png) User can get a quick intuition and overview of SLM-UI by looking at this [video](https://youtu.be/TVYPsZs3UkY).

Before you start using the SLM-UI, HPE recommends you to read the [Documentation](/README.md#documentation) section to understand about the architecture     of Swarm Learning, how these nodes work, how model training happens, and Swarm Learning Concepts section.

Perform the following steps to run the SL examples using SLM-UI.

1.  For ease of use, users can extract the examples folder from the documentation tar ball on their laptops.

2.  Users must generate x.509 certificates for their own environment. HPE-provided `gen-cert` utility under swarm-learning/examples/utils can be used for generating self-signed certificates just for the purposes of running the examples. Run the `gen-cert` utility on one of the Linux host to generate the self-signed certificates. Ensure that these certificates are copied to your laptop under the examples folder.

3.  User can use Linux remote desktop to display the SLM-UI on the local browser \(instead of the remote laptop browser\). With this, the SLM-UI's file open dialog box shows all local Linux files to the user. This makes it easier to upload the training artifacts like certs, SWOP profile, Task yaml, etc.

    Alternatively, user can use cross-platform file sharing to mount the artifacts directory from the Linux machine on his laptop.

4.  User can use the provided template files and the generated certificates for the examples and import them into the SLM-UI installer.

5.  User can use the certificate names which are hardcoded inside the provided template yaml files. In case, user changes the certificate names, then they need to make the corresponding changes in the SWOP yaml file.

      ### **NOTE:** 
     HPE recommends that users use their own certificates in actual production environment.
  
To run the Swarm Learning examples using SLM-UI, perform the following steps:

1.  [Creating a Project](Creating_a_Project_in_SLM-UI.md)

2.  [Adding Swarm Nodes](Adding_Swarm_Nodes.md)

3.  [Creating a Task](Creating_a_task.md)

4.  [Creating Task Runners](Creating_Task_Runners.md)

5.  [Creating a Contract](Creating_a_Contract.md)

6.  [Executing a Task](Executing_a_Task.md)

7.  [Managing the Global Settings](Managing_the_Global_Settings.md)

8.  [Centralized Swarm diagnostic](Centralized_Swarm_diagnostic.md)


