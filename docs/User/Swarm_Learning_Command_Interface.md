# <a name="GUID-4AB7AD75-8467-4F3F-9392-23C694131D4F"/> Swarm Learning Command Interface

Swarm Learning Command Line Interface \(SWCI\) is the command interface tool to the Swarm Learning framework. It is used to view the status, control, and manage the Swarm Learning framework. SWCI manages the Swarm Learning framework using contexts and contracts. For more information on how to start the SWCI tool, see *HPE Swarm Learning Installation and Configuration Guide*.

The user can enter any command from the predefined set of commands in the SWCI prompt. The entered command is parsed, then executed and the output is shown in the command line.

The subsequent sections mention about SWCI-related commands, and these commands are also part of the help text.

## <a name="SECTION_ZL5_PFG_HSB"/> SWCI commands related to context

Users are required to explicitly create a context \(using the CREATE context command\) and activate it as follows:

```
+----------------------------------------------------------------+
| SWCI:13 > create context **testContext** sn.test.sw.net        |
| API Server is UP!                                              |
| CONTEXT CREATED : **testContext**                              |
| SWCI:14 > SWITCH CONTEXT testContext                           |
| DEFAULT CONTEXT SET TO : testContext                           |
| SWCI:15 >                                                      |
+----------------------------------------------------------------+
```

|Command|Description and parameters|
|-------|--------------------------|
|`CREATE CONTEXT <contextName : string> <ip : string> [port : string]`|Creates a SWCI context.<br>-   `contextname`: A user given identifier for this context.<br>-   `IP`: IP address or FQDN of the API server \(Swarm Network node\) serving Swarm Learning APIs.<br>-   `port`\(optional\): The port number on which the API server is listening.<br>|
|`SWITCH CONTEXT <contextName : string>`|Switches current SWCI context to a specified context.|
|`LIST CONTEXTS`|Prints the list of contexts related to the current SWCI session.|
|`GET CONTEXT INFO [contextName : string]`|Prints the context information of the current Context when `contextName` is not specified. If `contextName` is specified prints information for the specified context.<br>|
|`LIST CONTEXT ENV <contextName : string>:`|Displays the list of context-specific environment variables. If the `contextName` is not specified, the default context is used.`contextName`: Specifies the context from which these environment variables are listed.<br>|
|`SET CONTEXT ENV <contextName : string> <env : string> <envValue : string>`|Sets the value of the specified context-specific environment variable. If the `contextName` is not specified, the default context is used. -   `contextName`: Specifies the name of the target context.<br>-   `env`: Specifies the target environment variable within the context.<br>-   `envValue`: The value for the variable being set.<br>|
|`GET CONTEXT ENV \<contextName:string> \<env:string>`|Obtains the value of the specified context-specific environment variable. If the `contextName` is not specified, the default context is used.<br>-   `contextName`: Specifies the name of the target context.<br>-   `env`: Specifies the target environment variable within the context.<br>|
|`GET CONTEXT VERSION`|Returns the API Server’s version information.|

## <a name="SECTION_S1C_HLK_HSB"/> SWCI commands related to contract

|Command|Description and parameters|
|-------|--------------------------|
|`LIST CONTRACTS`|Displays the list of Swarm Learning contracts currently registered into the Swarm Learning network.|
|`GET CONTRACT INFO \<SLContractName:string>`|Displays the static information about the specified Swarm Learning contract.|
|`GET CONTRACT STATUS \<SLContractName:string>`|Reports the current dynamic status of the specified Swarm Learning contract.|
|`RESET CONTRACT \<SLContractName:string>`|Resets the state of the contract to uninitialized state.<br> **WARNING**:This action cannot be undone, reset only completed Swarm Learning contracts. Resetting the active contracts can result in unexpected behavior.<br> A typical scenario would be when a user wants to reuse a completed training contract and start a new training session.|
|`CREATE CONTRACT \<SLContractName:string>`|Registers the specified Swarm Learning contract into the Swarm Learning network.|

## <a name="SECTION_VMG_GMK_HSB"/> SWCI commands related to Task

|Command|Description and parameters|
|-------|--------------------------|
|`LIST TASKS`|Displays the list of tasks that are registered into the Swarm Learning network.|
|`GET TASK INFO <taskName : string>`|Prints task information of the specified Task ID.|
|`GET TASK BODY <taskName : string>`|Prints the consolidated task body for the specified Task ID.|
|`CREATE TASK <taskType : string> <taskName : string> <author : string> <prereq : string> <outcome : string>`|Creates a task and registers into Swarm network.<br>-   `taskType`: Specifies the type of task to be created.<br>-   `taskName`: Specifies the unique name of task.<br>-   `author`: Specifies the author of the task.<br>-   `prereq`: Specifies the prerequisite required to create and execute the task.<br>-   `outcome`: Specifies the name of the artifact that is produced as a result of this task.<br>|
|`CREATE TASK FROM <taskDefFile:string>:`|`taskDefFile` is a relative path to task definition file.|
|`APPEND TASK BODY <taskName : string> <idx : int> <contentLine : string>`| Add or overwrite a specified line in the task body.<br>**NOTE**:Finalized task cannot be modified.<br>-   `taskName`: Specifies the task that must be modified.<br>-   `idx`: Specifies a nonzero line that must be added or modified.<br>-   `contentLine`: Actual text that is less the 80 characters.<br> |
|`DELETE TASK <taskName : string>`|Delete the specified task. This command is used for removing tasks that have errors while being created.<br>**NOTE**:Finalized task cannot be deleted.<br>`taskName`: Specifies the task that must be deleted.<br>|
|`FINALIZE TASK <taskName : string>`|Finalizes the specified task. Once finalized, task body cannot be modified further.<br>`taskName`: Specifies the task that must be finalized.<br>|

## <a name="SECTION_ZQZ_SNK_HSB"/> SWCI commands related to Taskrunner

|Command|Description and parameters|
|-------|--------------------------|
|`LIST TASKRUNNERS`|Displays the list of Taskrunners that are registered into the Swarm Learning network.|
|`GET TASKRUNNER INFO <taskRunnerName : string>`|Displays the current status of the specified Taskrunner ID.|
|`CREATE TASKRUNNER <trName : string>`|Creates and registers a Taskrunner contract into Swarm network.<br>`trName`: Specifies the unique name of Taskrunner.<br>|
|`RESET TASKRUNNER <trName : string>`|Resets the state of the taskrunner contract to an uninitialized state. <br>**WARNING**:This action cannot be undone, reset only completed Taskrunner contracts. Resetting the active taskrunner contract can result in unexpected behavior.<br>`trName`: Specifies the unique name of Taskrunner.<br>|
|`ASSIGN TASK <taskName : string> TO <trName : string> WITH <peersNeeded> PEERS`|Assigns a task to a taskrunner instance and expected minimum peer count.<br>-   `taskName`: Specifies the unique name of task.<br>-   `trName`: Specifies the unique name of Taskrunner.<br>-   `WITH <peersNeeded> PEERS`:<br>`peersNeeded` is a nonzero positive integer specifying the minimum number of peers required to complete this task.<br>Meaningful value of minimum peers is dependent on the task type. For RUN\_SWARM task, it is the number of SL and ML node pairs. For all other TASK types, it is the number of SWOP nodes.<br>|
|<code> GET TASKRUNNER PEER STATUS <taskRunnerName : string> <swopIndex&vert;swopUid></code>:|Displays current status for the specified PEER \(SWOP node\) in the Taskrunner’s context.<br>-   `taskRunnerName`: Specifies the unique name of Taskrunner.<br>-   `swopIndex`: The index number of SWOP Node, starts with 0 up to `ENROLLEDSWOP`.<br>-   `swopUid`: The UID String of the SWOP Node. You can specify either `swopIndex` or `swopUid`, not both.<br>|
|`LIST TASKRUNNER PEERS <taskRunnerName:string>`|Displays list of enrolled peers for the specified Taskrunner ID.|
|`WAIT FOR TASKRUNNER <trName : string>`|Waits for the Taskrunner to complete its current task.<br>`trName`: Specifies the unique name of the Taskrunner.<br>Prints a message periodically until the task completes. When the task completes, the final state of the task is printed.<br>|

## <a name="SECTION_M4G_JPK_HSB"/> Miscellaneous commands in SWCI

|Command|Description and parameters|
|-------|--------------------------|
|`WAIT FOR \<ip:string> \[port:string\] \[retries:string\]`|This command waits for the specified API server to accept connections.<br>-   `ip`: The IP address or FQDN of the API server \(SN node\) serving Swarm Learning APIs.<br>-   `port`: \(Optional\) The string representation of the port number on which the API Server is listening.<br>-   `retries`: \(Optional\). Default "retries" is 360 times \(30 mins\). This is the maximum number of times SWCI reattempts to connect after waiting for a 5 seconds timeout period.<br>|
|`EXIT`|This command exits the SWCI session unconditionally.|
|`EXIT ON FAILURE \[ON/OFF\]`|This command instructs SWCI to exit the current session when any of the subsequent commands fail. The default value is OFF.|
|`LIST NODES`|This command prints the list of registered and active nodes.|
  
**For programmatic interface of SWCI**, see - [SWCI APIs](SWCI_APIs.md)

