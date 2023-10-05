# <a name="GUID-3E1F1726-9D98-413A-961F-80048D1080F4"/> SWCI APIs

The following API features help to invoke SWCI operations programmatically. It is used to view the status, control, and manage the Swarm Learning framework.

<blockquote>
NOTE:
  Arguments that do not have default values are mandatory.
  This is an experimental API methods for developers.

</blockquote>
The python3 program needs to import the SWCI class first, and then use the below APIs.

`from swarmlearning.swci import swci`

|SWCI API methods|Description|Arguments|
|----------------|-----------|---------|
|`swci()`|This method invokes the constructor of the SWCI class and creates a SWCI object instance.|`swciIP,port = int \(30306\), clientCert = None, clientPKey = None, clientCABundle = None, logger = None, logLv = logging.WARNING, enableCaching = True`<br>- `swciIP`: The IP address or Name of the SWCI container that the user wants to connect to.<br>- `clientCert/ clientPKey/ ClientCABundle`: If you need secure mTLS connection to the SWCI container, then specify the certificates.<br>- `logLv`: Log level - One of `{ logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG}` <br>- `enableCaching`: If True, it enables caching of command output of some commands whose output does not change frequently. This is done to avoid network round trips.<br>|
|`assignTask()`|This method assigns a task to a Taskrunner instance and specifies the minimum peer count for declaring the result. This triggers SWOPs to execute this task <br> <br> Meaningful value of peersNeeded is dependent on the task type. For `RUN_SWARM` task, it is the number of SL and ML node pairs. For all other task types, it is the number of SWOP nodes. <br> <br> For RUN_SWARM task type, the actual numbers of SL/ML peers started could be equal or greater than `peersNeeded`, depending on the number of the SL nodes defined in the SWOP profiles. <br> For other TASK types, the number of SWOPs participating would be equal to `peersNeeded`. | - `taskName`: Specifies the unique name of a task.<br>- `trName`: Specifies the unique name of a Taskrunner. SWOP’s listening on this Taskrunner participates and executes this task.<br>- `peersNeeded` is a nonzero positive integer specifying the minimum number of peers required to complete this task.<br> |
|`cd()`|This method changes the current working directory of SWCI container.|`dirPath`|
|`clearCache()`|This method clears any cached values in the SWCI instance.| |
|`createContext()`|This method creates an SWCI context.<br> **NOTE**: User can create SWCI context with (ip and port) or with service [eg:api.sn.swarm:30304].<br> </br> For example,<br> </br> 1. createContext(test,ip=172.1.1.1) - This variation assumes SN API running on default 30304 port. <br> </br> 2. createContext(test, ip=172.1.1.1, port=16000) – This variation is used when SN API running on nondefault port,<br> </br> 3. createContext(test,service=api.sn.swarm) – In reverse proxy scenario, this variation means SN API service running on default 443 port.<br> </br> 4. createContext(test,service=api.sn.swarm:17000) – In reverse proxy scenario, this variation means SN API service running on non-default port.|`ctxName`, `ip=None`, `port=30304`, `service=None`|
|`createTaskFrom()`|This method creates a new task from the YAML file, the YAML definition file must be exported to the SWCI container using `uploadTaskDefintion` method.|`yamlFileName`|
|`createTrainingContract()`|This method registers the specified Swarm Learning training contract into the Swarm Learning network.|`ctName`|
|`deleteTask()`|This method deletes the specified task which is not finalized.|`taskName`|
|`executeTask()`|This method executes a task. It assigns, monitors, and resets taskrunner at the end of the task execution.|- `taskName, tr='defaulttaskbb.taskdb.sml.hpe', peers=1, pollWaitInSec=120, resetTROnSuccess=TruepollWaitInSec`: Wait time before polling for status.<br>- `resetTROnSuccess`: If the taskrunner contract has to be reset on success.<br>|
|`finalizeTask()`|This method finalizes the specified task. Once finalized, the task body cannot be modified further.|`taskName`|
|`getContextInfo()`|This method prints the context information of the current context when contextName is not specified. If contextName is specified, it prints information for the specified context.|`ctxName`|
|`getErrors()`|This method prints the error if any from the previously executed SWCI method.| |
|`getTaskBody()`|This method prints the consolidated task body for the specified Task ID.|`taskName`|
|`getTaskInfo()`|This method prints the task information of the specified Task ID.|`taskName`|
|`getTaskRunnerInfo()`|This method prints the current status of the specified Taskrunner ID.|`trName`|
|`getTaskRunnerPeerStatus()`|This method prints the current status for the specified PEER (SWOP node) in the Taskrunner’s context.<br> <br> The status of the PEER differs based on the type of the current TASK that has been assigned to TASKRUNNER. <br> For RUN_SWARM task, the status summary reports SWOP node UID, Number of SL PEERs this SWOP has spawned, and list of all SL node information (UID, Status, Description). <br> For all other types of tasks, the status summary reports SWOP node status (UID, Status, Description). <br> Note: Node UID can be used to identify the container name/id from ‘LIST NODES’ command. With container name/id, user can debug the error with docker logs.|`trName`, `idx`|
|`getTaskrunnerStatus() <trName:string>`|This method prints the current status of the specified Taskrunner.<br>  <br> Provides below information like:<br>- TASK NAME – Current running task or ‘Empty’ if no task is assigned.<br>- PEER TYPE – SL for RUN_SWARM tasks, SWOP for all other tasks.<br>- TASK STATE – Current task state.<br>- ACTIVE, COMPLETED and FAILED PEERS information.<br>- TIME STAMPs of various events on the TASKRUNNER contract.| `trName`: Specifies the unique name of Taskrunner.<br>|
|`getTrainingContractInfo()`|This method prints static information about a training contract.|`ctName`|
|`getTrainingContractPerformanceData`|This method prints Performance Data for a training contract. <br>It provides training performance data like UID, SL ADMIN status, model loss, model metric, total number of epochs and total number of completed epochs, for each SL-ML pair.|`ctName='defaultbb.cqdb.sml.hpe'`|
|`getTrainingContractStatus()`|This method prints the current dynamic status of a training contract.|`ctName`|
|`isTaskDone()`|This method displays true if a taskrunner has completed the current task , else false.|`trName`|
|`listContexts()`|This method displays the list of contexts related to the current SWCI session.| |
|`listNodes()`|This method displays the list of Swarm nodes that have registered and are currently active.<br>&nbsp;<br>For each Swarm node, it displays the Node type, Host IP, Port, Container name, UUID, parent UUID and the last received ‘i-amalive’ Timestamp.<br>&nbsp;<br>SWCI and ML nodes are not displayed.| |
|`listTaskRunners()`|This method displays the list of taskrunners that are registered into the Swarm Learning network.| |
|`listTasks()`|This method displays the list of tasks that are registered into the Swarm Learning network.| |
|`listTrainingContracts()`|This method displays the list of training contracts registered with Swarm Learning network.| |
|`ls()`|This method displays the directory contents of the SWCI container.|`optStr=''`|
|`plotTopology()`|This method displays the PNG object showing the current topology of the Swarm Learning network.<br> By default, it will display the Swarm Node type and Host IP on which the node is running.<br> **NOTE**: Color codes are hexadecimal triplets representing the colors red, green, and blue (#RRGGBB).|User can pass additional attributes which they want to see on the plot. These additional attributes are: 'Port', 'ContainerName', 'UUID', 'parentUUID' and 'i-am-alive'.<br> </br> SNColour="#ADD8E6",<br> SWOPColor="#33FF33",<br> SLColor="#FFCCCB", <br> attrs=['ContainerName']|
|`pwd()`|This method displays the present working directory of the SWCI container.| |
|`registerTask()`|This method registers a task into the SN network and finalizes it, if the task is valid.|`yamlFileName, finalize=True`|
|`resetTaskRunner()`|This method resets the state of the taskrunner contract to an uninitialized state.<br><strong>WARNING:</strong>This action cannot be undone, reset only completed Taskrunner contracts. Resetting the active taskrunner contract can result in unexpected behavior.|`trName='defaulttaskbb.taskdb.sml.hpe'`|
|`resetTrainingContract()`|This method resets the state of the training contract to an uninitialized state.<br><strong>WARNING:</strong>This action cannot be undone, reset only completed Swarm Learning contracts. Resetting the active contracts can result in unexpected behavior.|`ctName='defaultbb.cqdb.sml.hpe'`|
|`sleep()`|This method sleeps for a specified time before executing the subsequent commands.<br>&nbsp;<br>For example, in between a `WAIT FOR TASKRUNNER` and `RESET TASKRUNNER`, one can use a `SLEEP 10`, to give a grace time of 10 secs, before the `RESET` command cleans up the SL and user container.<br>&nbsp;<br>This would be required to allow the user ML code to save the model or do any inference of the model, after the Swarm training is over.<br>&nbsp;<br>For more information, [see the example SWCI script](/examples/mnist/swci/swci-init) |`time in seconds`|
|`setLogLevel()`|This method sets the logging level for the SWCI container.|logLv One of `{ logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG }`<br>|
|`uploadTaskDefintion()`|This method uploads the local task definition file to the SWCI container.|`taskFilePath`|


## Example snippet of an API

```
##################################################################################################################
# This code snippet shows how an user can use SWCI API's
#
# We assume the following things before running this script:
# 1. Swarm Learning Infrastructure is setup and ready.
# 2. SWCI container is running in WEB mode (-e SWCI_MODE='WEB')
# 3. There should be explicit port forwarding for SWCI_WEB_PORT while running the SWCI container (ex: -p 30306:30306)
# 4. Swarm learning wheel package should be installed in the python environment where we run this file.
##################################################################################################################
```

```
# Import swci from the swarmlearning whl package
import swarmlearning.swci as sw

swciServerName = 'SWCI Server Name or IP'
snServerName = 'SN Server Name or IP'

# Connect to the SWCI via SWCI_WEB_PORT
s = sw.Swci(swciServerName,port=30306) #30306 is the default port
# Connect to SN and create context
print(s.createContext('testContext', ip=snServerName))
# Switches the context to testContext
print(s.switchContext('testContext'))
# Creates a training contract
print(s.createTrainingContract('testContract'))
# Lists all the created Contexts
print(s.listContexts())
# Lists all the tasks that includes root task
print(s.listTasks())
```
