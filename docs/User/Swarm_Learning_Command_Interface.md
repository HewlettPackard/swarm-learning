# <a name="GUID-4AB7AD75-8467-4F3F-9392-23C694131D4F"/> Swarm Learning Command Interface

Swarm Learning Command Line Interface \(SWCI\) is the command interface tool to the Swarm Learning framework. It is used to view the status, control, and manage the Swarm Learning framework. SWCI manages the Swarm Learning framework using contexts and contracts. For more information on how to start the SWCI tool, see [Starting SWCI](/docs/Install/Starting_SWCI_nodes.md).

The user can enter any command from the predefined set of commands in the SWCI prompt. The entered command is parsed, then executed and the output is shown in the command line.

The user can provide an init script file that has SWCI commands to be executed at the start of SWCI. If we provide this option, all the SWCI commands within this script file are processed, before it enters the interactive mode and waits for users commands. Users can simulate a non-interactive SWCI run, by having a bunch of SWCI commands and an SWCI `EXIT` command at the end of this init script file. This could be used for automation.

The subsequent sections provide details about SWCI-related commands, and are also part of the **online help** that is available within the tool.

## <a name="SECTION_ZL5_PFG_HSB"/> SWCI commands related to context

A SWCI tool can control operations on multiple Swarm Learning framework instances. Each instance is encapsulated and represented as a context. At a given time, only one context is active. All SWCI commands work with the current active context (default context) and they do not take context as an explicit argument. Before running any SWCI command, users are required to explicitly create a context \(using the CREATE context command\) and activate it as follows:

```
+------------------------------------------------------------------------+
| SWCI:13 > CREATE CONTEXT **testContext** WITH IP sn.test.sw.net        |
| API Server is UP!                                                      |
| CONTEXT CREATED : **testContext**                                      |
| SWCI:14 > SWITCH CONTEXT testContext                                   |
| DEFAULT CONTEXT SET TO : testContext                                   |
| SWCI:15 >                                                              |
+------------------------------------------------------------------------+
```

|Command|Description and parameters|
|-------|--------------------------|
|`CREATE CONTEXT <contextName : string> WITH IP <ip : string> [port : string]`|Creates a SWCI context.<br>-   `contextname`: A user given identifier for this context.<br>-   `ip`: IP address or FQDN of the API server \(Swarm Network node\) serving Swarm Learning APIs.<br>-   `port`\(optional\): The port number on which the API server is listening.<br>|
|`CREATE CONTEXT <contextName : string> WITH SERVICE <service : string>`|Creates a SWCI context. This is used when using reverse proxy.<br>-   `contextname`: A user given identifier for this context.<br>-   `service`: FQDN for the API Service of the associated Swarm Network node. If the reverse proxy is configured to run on any nondefault port, it has to be passed along with the service string parameter with ':' separator." This is an optional port.<br>|
|`GET CONTEXT INFO [contextName : string]`|Prints the context information of the current Context when `contextName` is not specified. If `contextName` is specified prints information for the specified context.<br>|
|`GET CONTEXT ENV \<contextName:string> \<env:string>`|Obtains the value of the specified context-specific environment variable. If the `contextName` is not specified, the default context is used.<br>-   `contextName`: Specifies the name of the target context.<br>-   `env`: Specifies the target environment variable within the context.<br>|
|`GET CONTEXT VERSION`|Returns the API Server’s version information.|
|`LIST CONTEXTS`|Prints the list of contexts related to the current SWCI session.|
|`LIST CONTEXT ENV <contextName : string>:`|Displays the list of context-specific environment variables. If the `contextName` is not specified, the default context is used.`contextName`: Specifies the context from which these environment variables are listed.<br>|
|`SET CONTEXT ENV <contextName : string> <env : string> <envValue : string>`|Sets the value of the specified context-specific environment variable. If the `contextName` is not specified, the default context is used. -   `contextName`: Specifies the name of the target context.<br>-   `env`: Specifies the target environment variable within the context.<br>-   `envValue`: The value for the variable being set.<br>|
|`SWITCH CONTEXT <contextName : string>`|Switches current SWCI context to a specified context.|

## <a name="SECTION_S1C_HLK_HSB"/> SWCI commands related to contract

|Command|Description and parameters|
|-------|--------------------------|
|`CREATE CONTRACT <SLContractName:string>`|Registers the specified Swarm Learning contract into the Swarm Learning network.|
|`GET CONTRACT INFO <SLContractName:string>`|Displays the static information about the specified Swarm Learning contract.|
|`GET CONTRACT STATUS <SLContractName:string>`|Reports the current dynamic status of the specified Swarm Learning contract.|
|`LIST CONTRACTS`|Displays the list of Swarm Learning contracts currently registered into the Swarm Learning network.|
|`PERFDATA CONTRACT <SLContractName:string>`|Displays performance data about the training under the Swarm Learning contract. <br> It provides training performance data like UID, SL ADMIN status, model loss, model metric, total number of epochs and total number of completed epochs, for each SL-ML pair.|
|`RESET CONTRACT <SLContractName:string>`|Resets the state of the contract to uninitialized state.<br> **WARNING**:This action cannot be undone, reset only completed Swarm Learning contracts. Resetting the active contracts can result in unexpected behavior.<br> A typical scenario would be when a user wants to reuse a completed training contract and start a new training session.|

## <a name="SECTION_VMG_GMK_HSB"/> SWCI commands related to Task

|Command|Description and parameters|
|-------|--------------------------|
|`APPEND TASK BODY <taskName : string> <idx : int> <contentLine : string>`| Add or overwrite a specified line in the task body.<br>**NOTE**:Finalized task cannot be modified.<br>-   `taskName`: Specifies the task that must be modified.<br>-   `idx`: Specifies a nonzero line that must be added or modified.<br>-   `contentLine`: Actual text that is less the 80 characters.<br> |
|`CREATE TASK <taskType : string> <taskName : string> <author : string> <prereq : string> <outcome : string>`|Creates a task and registers into Swarm network.<br>-   `taskType`: Specifies the type of task to be created.<br>-   `taskName`: Specifies the unique name of task.<br>-   `author`: Specifies the author of the task.<br>-   `prereq`: Specifies the prerequisite required to create and execute the task.<br>-   `outcome`: Specifies the name of the artifact that is produced as a result of this task.<br>|
|`CREATE TASK FROM <taskDefFile:string>:`|`taskDefFile` is a relative path to task definition file.|
|`DELETE TASK <taskName : string>`|Delete the specified task. This command is used for removing tasks that have errors while being created.<br>**NOTE**:Finalized task cannot be deleted.<br>`taskName`: Specifies the task that must be deleted.<br>|
|`FINALIZE TASK <taskName : string>`|Finalizes the specified task. Once finalized, task body cannot be modified further.<br>`taskName`: Specifies the task that must be finalized.<br>|
|`GET TASK BODY <taskName : string>`|Prints the consolidated task body for the specified Task ID.|
|`GET TASK INFO <taskName : string>`|Prints task information of the specified Task ID.|
|`LIST TASKS`|Displays the list of tasks that are registered into the Swarm Learning network.|

## <a name="SECTION_ZQZ_SNK_HSB"/> SWCI commands related to Taskrunner

|Command|Description and parameters|
|-------|--------------------------|
|`ASSIGN TASK <taskName : string> TO <trName : string> WITH <peersNeeded> PEERS`|Assigns a task to a taskrunner instance and specify the minimum peer count for declaring the result. This triggers SWOPs to execute this task<br><br>-   `taskName`: Specifies the unique name of task.<br>-   `trName`: Specifies the unique name of Taskrunner. SWOP’s listening on this Taskrunner participates and executes this task.<br>-   `WITH <peersNeeded> PEERS`: <br><br>`peersNeeded` is a nonzero positive integer specifying the minimum number of peers required to complete this task.<br>  <br> Meaningful value of minimum peers is dependent on the task type. For RUN_SWARM task, it is the number of SL and ML node pairs. For all other TASK types, it is the number of SWOP nodes. <br> <br>For RUN_SWARM task type, the actual numbers of SL/ML peers started could be equal or greater than `peersNeeded`, depending on the number of the SL nodes defined in the SWOP profiles. <br><br>For other TASK types, the number of SWOPs participating would be equal to `peersNeeded`.<br>|
|`CREATE TASKRUNNER <trName : string>`|Creates and registers a Taskrunner contract into Swarm network.<br>`trName`: Specifies the unique name of Taskrunner.<br>|
|`GET TASKRUNNER INFO <taskRunnerName : string>`|Displays the current status of the specified Taskrunner ID.|
|`GET TASKRUNNER PEER STATUS <taskRunnerName:string><swopIndex\swopUid>:`|Displays current status for the specified PEER in the Taskrunner’s context.<br><br>-   `taskRunnerName`: Specifies the unique name of Taskrunner.<br>-   `swopIndex`: The index number of SWOP Node, starts with 0 up to ENROLLEDSWOP.<br>-   `swopUid:`: The UID String of the SWOP Node. You can specify either `swopIndex` or `swopUid`, not both.<br>  <br> The status of the PEER differs based on the type of the current TASK that has been assigned to TASKRUNNER.<br><br>  For RUN_SWARM task, the status summary reports SWOP node UID, Number of SL PEERs this SWOP has spawned, and list of all SL node information (UID, Status, Description).<br><br> For all other types of tasks, the status summary reports SWOP node status (UID, Status, Description).<br><br> **Note**: Node UID can be used to identify the container name/id from ‘LIST NODES’ command. With container name/id, user can debug the error with docker logs.<br>|
|`GET TASKRUNNER STATUS <trName:string>`|Displays the current status of the specified Taskrunner.<br>   `trName`: Specifies the unique name of Taskrunner.<br>   Provides below information like,<br>-   TASK NAME – Current running task or ‘Empty’ if no task is assigned.<br>- PEER TYPE – SL for RUN_SWARM tasks, SWOP for all other tasks.<br>-   TASK STATE – Current task state.<br>-   ACTIVE, COMPLETED and FAILED PEERS information.<br>-  TIME STAMPs of various events on the TASKRUNNER contract.<br>|
|`LIST TASKRUNNERS`|Displays the list of Taskrunners that are registered into the Swarm Learning network.|
|`LIST TASKRUNNER PEERS <taskRunnerName:string>`|Displays list of enrolled peers for the specified Taskrunner ID.|
|`RESET TASKRUNNER <trName : string>`|Resets the state of the taskrunner contract to an uninitialized state. <br>**WARNING**:This action cannot be undone, reset only completed Taskrunner contracts. Resetting the active taskrunner contract can result in unexpected behavior.<br>`trName`: Specifies the unique name of Taskrunner.<br>|
|`WAIT FOR TASKRUNNER <trName : string>`|Waits for the Taskrunner to complete its current task.<br>&nbsp;<br>-`trName`: Specifies the unique name of the Taskrunner.<br>&nbsp;<br>`WAITING FOR TASKRUNNER TO COMPLETE` - Maximum wait time is : `<SWCI_TASK_MAX_WAIT_TIME>`.<br>&nbsp;<br>If `SWCI_TASK_MAX_WAIT_TIME` is not set, the default value is 120 mins.<br>&nbsp;<br>Prints # (a progress indicator) periodically until the task completes. When the task completes, the final state of the task is printed.<br>&nbsp;<br>If the maximum wait time is reached, the following warning message is displayed:<br>WARNING - Maximum configured SWCI wait time is over|

## <a name="SECTION_M4G_JPK_HSB"/> Miscellaneous commands in SWCI

|Command|Description and parameters|
|-------|--------------------------|
|`cd <dirPath>`|This method changes the current working directory of SWCI container.<br>|
|`EXIT`|This command exits the SWCI session unconditionally.|
|`EXIT ON FAILURE [ON/OFF]`|This command instructs SWCI to exit the current session when any of the subsequent commands fail. The default value is OFF.<br>|
|`LIST NODES`|This command displays the list of Swarm nodes that have registered and are currently active.<br>&nbsp;<br>For each Swarm node, it displays the Node type, Host IP, Port, Container name, UUID, parent UUID and the last received ‘i-amalive’ Timestamp.<br>&nbsp;<br>SWCI and ML nodes are not displayed.<br>&nbsp;<br>For a reverse proxy scenario, it displays the service name of the associated node, instead of Host IP. Users can look at their NGINX configuration file to know the IP addresses of the respective service names.<br>&nbsp;<br>For Sentinel and Non-Sentinel nodes, it displays its respective API service names. For SL nodes, it displays the FS service names. For SWOP node, it displays the API service name of the associated SN node.<br>|
|`ls()`|This method displays the directory contents of the SWCI container.<br>|
|`pwd()`|This method displays the present working directory of the SWCI container.<br>|
|`SLEEP`|This command sleeps for a specified time before executing the subsequent commands.<br>&nbsp;<br>For example, in between a `WAIT FOR TASKRUNNER` and `RESET TASKRUNNER`, one can use a `SLEEP 10`, to give a grace time of 10 secs, before the `RESET` command cleans up the SL and user container.<br>&nbsp;<br>This would be required to allow the user ML code to save the model or do any inference of the model, after the Swarm training is over.<br>&nbsp;<br>For more information, see the example SWCI scripts in the `swarm-learning/examples/` directory.|
|`WAIT FOR IP <ip:string> [port:string] [retries:string]`|This command waits for the specified API server to accept connections.<br>-   `ip`: The IP address or FQDN of the API server \(SN node\) serving Swarm Learning APIs.<br>-   `port`: \(Optional\) The string representation of the port number on which the API Server is listening.<br>-   `retries`: \(Optional\). Default "retries" is 360 times \(30 mins\). This is the maximum number of times SWCI reattempts to connect after waiting for a 5 seconds timeout period.<br>|
|`WAIT FOR SERVICE <service:string> [retries:string]`|This command waits for the specified API server to accept connections.<br>-   `service`: FQDN for the API Service of the associated Swarm Network node. If the Port number exists, it has to be passed along with the service string parameter with ':' separator. This is an optional port.<br>-    `retries`: \(Optional\). Default "retries" is 360 times \(30 mins\). This is the maximum number of times SWCI reattempts to connect after waiting for a 5 seconds timeout period.<br>|
  
**For programmatic interface of SWCI**, see - [SWCI APIs](SWCI_APIs.md)

