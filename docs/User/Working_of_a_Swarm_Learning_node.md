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

At the end of every sync frequency, when it is time to share the learnings from the individual models, one of the SL nodes is designated as “leader”. This leader node collects the individual models from each peer node and merges them into a single model by combining parameters of all the individuals. 

**Merge Methods** are one of the core operations in Swarm Learning that ensures learning is shared across SL nodes. Swarm Learning provides three different merge options via Swarm callback. The merge options are 'mean', 'coordmedian' and 'geomedian'. User can pass one of these options via `mergeMethod` parameter in the Swarm callback. This is an optional parameter for the callback. These options will consider the weightages of individual SL nodes as well. All nodes that have participated in the sync round will receive aggregated model parameters for the next sync round.

The 'mean' option aggregates intermediate model parameters using a weighted mean method \(also known as weighted federative averaging\). This method sums up all the intermediate model parameters in an iterative way and at the end of the merge method, it divides with sum of weightages. This is the default merge method in Swarm.

The 'coordmedian' option finds the weighted coordinate median of the intermediate model parameters. These parameters from all the nodes that are participating in the given merge round will get transformed and transposed before calculating the coordinate median. This merge method finds the 50th percentile and tries to converge along with the model parameters over the sync cycles.

The 'geomedian' option finds the weighted geometric median of the intermediate model parameters. It uses Weiszfeld's algorithm which is an iterative method to calculate the geometric median. It starts with model parameters average as an initial estimate and iterate to find a better estimate. This process is repeated until the difference between new estimate and old estimate reaches to a threshold value.

**Leader Failure Detection and Recovery (LFDR)** feature enables SL nodes to continue Swarm training during merging process when an SL leader node fails. A new SL leader node is selected to continue the merging process. If the failed SL leader node comes back after the new SL leader node is in action, the failed SL leader node is treated as a normal SL node and contributes its learning to the swarm global model.

Each peer SL node then uses this merged model to start the next training batch. This process is coordinated by the SN network. The models are exchanged using the Swarm Learning file server.

A Swarm Learning ML program can specify a **Minimum Number of Peers** that are required to perform the synchronization. If the actual number of peers is less than this threshold value, the platform blocks the synchronization process until the required number of peers becomes available and reaches the synchronization point.

