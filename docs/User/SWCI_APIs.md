# <a name="GUID-3E1F1726-9D98-413A-961F-80048D1080F4"/> SWCI APIs

The following API methods help to invoke SWCI operations programmatically. It is used to view the status, control, and manage the Swarm Learning framework.

<blockquote>
NOTE:Arguments that do not have default values are mandatory.

</blockquote>
The python3 program needs to import the SWCI class, and then use the below APIs.

`from swarmlearning.swci import swci`

|SWCI API methods|Description|Arguments|
|----------------|-----------|---------|
|`swci()`|This method invokes the constructor of the SWCI class and creates a SWCI object instance.|`swciIP,port = int \(30306\), clientCert = None, clientPKey = None, clientCABundle = None, logger = None, logLv = logging.WARNING, enableCaching = True`<br>- `swciIP`: The IP address or Name of the SWCI container that the user wants to connect to.<br>- `clientCert/ clientPKey/ ClientCABundle`: If you need secure mTLS connection to the SWCI container, then specify the certificates.<br>- `logLv`: Log level - One of `{ logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG}` <br>- `enableCaching`: If True, it enables caching of command output of some commands whose output does not change frequently. This is done to avoid network round trips.<br>|
|`assignTask()`|This method assigns a task to a taskrunner.|- `taskName, trName, peerstaskName`: Specifies the unique name of a task.<br>- `trName`: Specifies the unique name of a Taskrunner.<br>- `peers`: Is a nonzero positive integer specifying the minimum number of peers required to complete this task.<br> Meaningful value of minimum peers is dependent on the task type. For `RUN_SWARM` task, it is the number of SL and ML node pairs. For all other task types, it is the number of SWOP nodes.<br> |
|`cd()`|This method changes the current working directory of SWCI container.|`dirPath`|
|`clearCache()`|This method clears any cached values in the SWCI instance.| |
|`createContext()`|This method creates an SWCI context.|`ctxName`, `ip`, `port=30304`|
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
|`getTaskRunnerPeerStatus()`|This method prints the current status for the specified PEER (SWOP node) in the Taskrunner’s context.|`trName`, `idx`|
|`getTaskRunnerStatus()`|This method prints the overall status of the taskrunner.|`trName`|
|`getTrainingContractInfo()`|This method prints static information about a training contract.|`ctName`|
|`getTrainingContractStatus()`|This method prints the current dynamic status of a training contract.|`ctName`|
|`isTaskDone()`|This method displays true if a taskrunner has completed the current task , else false.|`trName`|
|`listContexts()`|This method displays the list of contexts related to the current SWCI session.| |
|`listNodes()`|This method displays the list of nodes present in the Swarm Learning network, it excludes the SWCI node.| |
|`listTaskRunners()`|This method displays the list of taskrunners that are registered into the Swarm Learning network.| |
|`listTasks()`|This method displays the list of tasks that are registered into the Swarm Learning network.| |
|`listTrainingContracts()`|This method displays the list of training contracts registered with Swarm Learning network.| |
|`ls()`|This method displays the directory contents of the SWCI container.|`optStr=''`|
|`plotTopology()`|This method displays the PNG object showing the current topology of the Swarm Learning network.| |
|`pwd()`|This method displays the present working directory of the SWCI container.| |
|`registerTask()`|This method registers a task into the SN network and finalizes it, if the task is valid.|`yamlFileName, finalize=True`|
|`resetTaskRunner()`|This method resets the state of the taskrunner contract to an uninitialized state.<br><strong>WARNING:</strong>This action cannot be undone, reset only completed Taskrunner contracts. Resetting the active taskrunner contract can result in unexpected behavior.|`trName='defaulttaskbb.taskdb.sml.hpe'`|
|`resetTrainingContract()`|This method resets the state of the training contract to an uninitialized state.<br><strong>WARNING:</strong>This action cannot be undone, reset only completed Swarm Learning contracts. Resetting the active contracts can result in unexpected behavior.|`ctName='defaultbb.cqdb.sml.hpe'`|
|`setLogLevel()`|This method sets the logging level for the SWCI container.|logLv One of `{ logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG }`<br>|
|`uploadTaskDefintion()`|This method uploads the local task definition file to the SWCI container.|`taskFilePath`|

