# Taskrunner Framework

Taskrunner framework is a decentralized task management framework.

It differs significantly from centralized task and workflow management frameworks \(for example, Apache Airflow\) in many aspects.

Here, we point out a few key differences.

-   The total size of the participating entities is not always known. In other words, we know only the quorum that is needed to take a decision and never know the full set of entities. The total size of the participating entities can change dynamically.
-   Success or Failure of a scheduled task depends on whether the predetermined quorum of nodes completed the task successfully or not.
-   It is very computationally complex to ensure all participating entities are in the same state at any given instant. Only eventual consistency is feasible. This implies that all participating entities will tend towards a common stable state eventually.

Considering the above aspects, rolling back a failed task is not possible, as we have only partial knowledge of the full state of the system at any given time. Instead, we can always take corrective action by re-running a task or creating new tasks that supersede earlier failed tasks.

**Parent topic:**[Swarm Operator node \(SWOP\)](Swarm_Operator_node_(SWOP).md)

