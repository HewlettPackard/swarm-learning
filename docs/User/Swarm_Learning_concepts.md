# <a name="GUID-01AF4513-24A0-49DA-B345-E28A054E87B8"/> Swarm Learning concepts

This section provides information about key Swarm Learning concepts. The subsequent section describes working of a Swarm Learning node, how to Swarm enable an ML algorithm, and interactions with SL, contexts, training contract, Taskrunner contract, and task.

SWCI is the command interface tool to the Swarm Learning framework. It is used to view the status, control, and manage the Swarm Learning framework. SWCI manages the Swarm Learning framework using contexts and contracts. For more information about SWCI, see [Swarm Learning Command Interface](Swarm_Learning_Command_Interface.md).

An SWCI context is a string identifier. It identifies an SWCI command environment and has artifacts \(API server IP, port, environment variables, and versions\) that are used to execute SWCI commands. SWCI can have only one active context at any given time even if multiple contexts are created. For more information related to context commands, see [SWCI commands related to context](Swarm_Learning_Command_Interface.md#-swci-commands-related-to-context).

Swarm Learning training contracts are used to control the swarm learning training process. It is an instance of Ethereum smart contract. It is deployed into the blockchain and registered into Swarm Learning Network using the `CREATE CONTRACT` command. For more information related to contract commands, see [SWCI commands related to contract](Swarm_Learning_Command_Interface.md#-swci-commands-related-to-contract).

<blockquote>
NOTE:When a contract is created, it is permanent and cannot be deleted.

</blockquote>

SWOP is the central component of the Taskrunner framework. It is packaged as a SWOP container. Taskrunner framework is a decentralized task management framework. For more information about SWOP, see [Swarm Operator node \(SWOP\)](Swarm_Operator_node_(SWOP).md).

A Task is a well-defined unit of work, that can be assigned to a Taskrunner. Tasks are instantiated according to the schema specified in the Task Schema YAML file. For more information related to Task commands, see [SWCI commands related to Task](Swarm_Learning_Command_Interface.md#-swci-commands-related-to-task).

A Taskrunner is an instance of Ethereum smart contract used to coordinate execution of task by SWOP nodes. For more information related to Taskrunner commands, see [SWCI commands related to Taskrunner](Swarm_Learning_Command_Interface.md#-swci-commands-related-to-taskrunner).

