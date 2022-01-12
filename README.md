# <d></d> <img style="float: right;" src="docs/images/GettyImages-1148109728_EAA-graphic-A_112_0_72_RGB.jpg?raw=true"/> SWARM LEARNING
Swarm Learning is a decentralized, privacy-preserving Machine Learning framework. This framework utilizes the computing power at, or near, the distributed data sources to run the Machine Learning algorithms that train the models. It uses the security of a blockchain platform to share learnings with peers in a safe and secure manner. In Swarm Learning, training of the model occurs at the edge, where data is most recent, and where prompt, data-driven decisions are mostly necessary. In this completely decentralized architecture, only the insights learned are shared with the collaborating ML peers, not the raw data. This tremendously enhances data security and privacy.

<d></d> <img style="float: center;" src="docs/images/sl_platform_components.png?raw=true"/>

Swarm Learning has five components, connected to form a network: 
- Swarm Learning (SL) nodes – These nodes run a user-defined Machine Learning algorithm. This algorithm is called the Swarm Learning ML Program. This program is responsible for training and updating the model in an iterative fashion. The Swarm Learning ML program should be either a Keras (TensorFlow 2 backend) or PyTorch based Machine Learning algorithm that is implemented using Python3. It can also be configured to run on NVIDIA GPUs.
- Swarm Network (SN) nodes – These nodes form the blockchain network. The current version of Swarm Learning uses an open-source version of Ethereum as the underlying blockchain platform. The Swarm Network nodes interact with each other using this blockchain platform to maintain global state information about the model that is being trained and to track progress (note that only metadata is written to the blockchain. The model itself is not stored in the blockchain.) The Swarm Network nodes use this state and progress information to coordinate the working of the Swarm Learning nodes. Each Swarm Learning node registers itself with a Swarm Network node as a part of its startup and initialization.
   - Sentinel node: This is a special Swarm Network node. The Sentinel node is responsible for initializing the blockchain network. This should be the first node to start.
- Swarm Learning Command Interface node (SWCI) - SWCI node is the command interface tool to the Swarm Learning framework. It is used to view the status, control and manage the swarm learning framework. It uses a secure link to connect to the Swarm Network node, using the API port. SWCI node can connect to any of the SN nodes in a given Swarm Learning framework to manage the framework.
- SPIFFE SPIRE Server nodes – These nodes provide the security for the whole network. The platform can run one or more SPIRE Server nodes that are connected together to form a federation. The platform includes a SPIRE Agent Workload Attestor plugin (not shown in the figure) that communicates with the SPIRE Servers to attest the identities of the Swarm Network and Swarm Learning nodes, acquire and manage a SPIFFE Verifiable Identity Document (SVID). For an overview SPIFFE, SPIRE and their capabilities refer to <https://spiffe.io/docs/latest/spiffe-about/overview/>

- License Server node – The license to run the Swarm Learning platform is installed and managed by the License Server node.

>**NOTE**: All the Swarm Learning nodes must use the same ML platform – either Keras (based on TensorFlow 2) or PyTorch. Using Keras for some of the nodes and PyTorch for the other nodes is not supported.

Swarm Learning nodes works in collaboration with other Swarm Learning nodes in the network. It regularly shares its learnings with the other nodes and incorporates their insights. This process continues until the Swarm Learning nodes train the model to desired state.

You can transform any Keras or PyTorch based ML program that has been written using Python3 into a Swarm Learning ML program by making a [few simple changes](docs/ml_algorithm.md) to the model training code, such as updating the paths from where the program reads and writes data; and including the `SwarmCallback` object. See the [examples](examples) included with the Swarm Learning package for sample code.

## Getting Started
  - [Prerequisites](docs/Prerequisites.md) for Swarm Learning
  - Clone this repository 
  - [Download and setup](docs/setup.md) docker images and evaluation licenses
  - Execute [MNIST example](examples/mnist-keras) 
  - [Frequently Asked Questions](docs/FAQ.md)
  - [Troubleshooting](docs/Troubleshooting.md)

## Documentation
  - [How Swarm Learning Components interact](docs/Component_interactions.md)
  - [Adapting ML programs for Swarm Learning](docs/ml_algorithm.md)
  - [Configuring and Running Swarm Learning Components](docs/RunningSL.md)
  - [Using SWCI Tool](docs/swci_tool.md)
  
## References
  - [Papers](docs/papers-and-articles.md)
  - [Videos](docs/videos.md)
  - [URLs](docs/URL.md)

## Acronyms and Abbreviations
  Refer to [Acronyms and Abbreviations](docs/acronyms.md) for more information.

## Getting in touch 
  Feedback and questions are appreciated. You can use the issue tracker to report bugs on GitHub.
  
  or
  
  Join below Slack channel to communicate with us. 
  
  [hpe-ai-swarm-learning](https://hpe-external.slack.com/archives/C02PWRJPWVD)


## Contributing
  Refer to [Contributing](CONTRIBUTING.md) for more information.

## License
  The distribution of Swarm Learning in this repository is for non-commercial and experimental use under this [license](LICENSE.md). 
  
  See [ATTRIBUTIONS](ATTRIBUTIONS.md) and [DATA LICENSE](DATA_LICENSE.md) for terms and conditions for using the datasets included in this repository.
