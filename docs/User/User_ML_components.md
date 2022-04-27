# <a name="GUID-007E275A-28AA-4B62-AD9B-41BAFD3437CC"/> User ML components

User can transform any Keras or PyTorch based ML program that is written using Python3 into a Swarm Learning ML program by making a few simple changes to the model training code by including the `SwarmCallback` API. For more information, see the examples included with the Swarm Learning package for a sample code.

The transformed user Machine Learning \(user ML node\) program can be run on the host or user can build it as a Docker container.

<blockquote>
NOTE:HPE recommends users to build an ML Docker container.

</blockquote>

The ML node is responsible to train and iteratively update the model. For each ML node, there is a corresponding SL node in the Swarm Learning framework, which performs the Swarm training. Each pair of ML and SL nodes must riun on the same host. This process continues until the SL nodes train the model to the desired state.

<blockquote>
NOTE:All the ML nodes must use the same ML platform either Keras \(based on TensorFlow 2 backend\) or PyTorch. Using Keras for some of the nodes and PyTorch for the other nodes is not supported.

</blockquote>
