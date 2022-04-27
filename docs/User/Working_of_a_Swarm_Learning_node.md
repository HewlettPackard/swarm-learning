# <a name="GUID-80EB950E-DB95-469F-A3DF-E14BBD005486"/> Working of a Swarm Learning node

1.  SL node starts by acquiring a digital identity, which can be either user provided CERTS or SPIRE certificates.

2.  SL node acquires a license to run.

3.  SL node registers itself with an SN node.

4.  SL node starts a file server and announces to the SN node that it is ready to run the training program.

5.  Waits for the User ML component to start the ML model training.


SL node works in collaboration with all the other SL nodes in the network. It regularly shares its learnings with the other nodes and incorporates their insights. Users can control the periodicity of this sharing by defining a **Sync**hronization **Frequency**\(from now on referred to as, sync frequency.\) This frequency specifies the number of training batches after which the nodes share their learnings.

<blockquote>
NOTE:

Specifying a large value reduces the rate of synchronization and a small value increases it. Frequent synchronization slows down the training process while infrequent ones may reduce the accuracy of the final model. Therefore, the sync frequency must be treated as a hyperparameter and chosen with some caution.

</blockquote>

Swarm Learning can automatically control the sync frequency, this feature is called **Adaptive Sync**hronization **Frequency**. This feature judges the training progress by monitoring the mean loss. A reduction in the mean loss infers that the training is progressing well. As a response, it increases the sync frequency and enables more batches to run before sharing the learnings. This makes the training run faster. In contrast, when the loss does not improve, **Adaptive Sync** frequency reduces the sync frequency and synchronizes the models more frequently.

At the end of every sync frequency, when it is time to share the learnings from the individual models, one of the SL nodes is designated as “leader”. This leader node collects the individual models from each peer node and merges them into a single model by combining parameters of all the individuals. Each peer SL node then uses this merged model to start the next training batch. This process is coordinated by the SN network. The models are exchanged using the Swarm Learning file server.

A Swarm Learning ML program can specify a **Minimum Number of Peers** that are required to perform the synchronization. If the actual number of peers is less than this threshold value, the platform blocks the synchronization process until the required number of peers becomes available and reaches the synchronization point.

