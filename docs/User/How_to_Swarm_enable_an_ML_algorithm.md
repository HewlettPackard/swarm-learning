# <a name="GUID-2D0165E8-A087-41E9-A160-EBCD66F39CB4"/> How to Swarm enable an ML algorithm

To convert an ML program into a Swarm Learning ML program:

1.  Import `SwarmCallback` class from the Swarm library.

```
from swarmlearning.tf import SwarmCallback
```

   `SwarmCallback` is a custom callback class that consists of a set of functions that can be applied at various stages of the training process. During training, the `SwarmCallback` and the set of functions provide a view of internal states and statistics of the model to the Swarm Learning framework. `SwarmCallback` executes Swarm Learning specific operations during training like sharing parameters with all the network peers at the end of a sync interval.

   For TensorFlow-based Keras platforms, `SwarmCallback` is based on the Keras `tf.keras.callbacks.Callback` class. The methods of this class are called automatically by Keras at appropriate stages of the training.

   Unlike Keras, PyTorch does not have an in-built Callback class. Therefore, on PyTorch-based platforms, user must call the methods of this class. These methods are described subsequently in this section. An example of their usage is shown in the MNIST sample program \(Link TBD\).

2.  Instantiate an object of the `SwarmCallback` class:

```
from swarmlearning.tf import SwarmCallback #for TensorFlow
from swarmlearning.pyt import SwarmCallback #for PyTorch

# Create Swarm callback
swarmCallback = SwarmCallback(syncFrequency=128,
minPeers=min_peers,
useAdaptiveSync=True,
adsValData=(x_test, y_test),
adsValBatchSize=8,
swarmCallback.logger.setLevel(logging.DEBUG)
```

<blockquote>
    NOTE:Some of the parameters have default values as mentioned in the following table. User must provide values as applicable to their use case.

</blockquote>

|Parameter|Description|
|---------|-----------|
|`syncFrequency`|Specifies the number of batches of local training to be performed between two swarm sync rounds. If adaptive sync enabled, this is the frequency to be used at the start.|
|`minPeers`|Specifies the minimum number of SL peers required during each synchronization round for Swarm Learning to proceed further.|
|`useAdaptiveSync`|Modulate the next syncFrequency value post each synchronization round based on performance on validation data. The default value is false.<br>**Note**: As of now, this option is implemented only for KERAS platform.|
|`adsValData`|Specifies the dataset for generating metrics for adaptive sync logic. It can be either an \(x\_val, y\_val\) tuple or a generator.|
|`adsValBatchSize`|Specifies the batch size for `adsValData`. This is used when `useAdaptiveSync` is turned ON.|
|`checkinModelOnTrainEnd`|Specifies the merge behavior of a SL node after it has achieved stopping criterion and it is waiting for all other peers to complete their training. During this period this SL node does not train the model with local data. This parameter decides the nature of the weights that this SL node contributes to the merge process.Allowed values are:<br>`inactive`: Node does not contribute its weights in the merge process but participates as non-contributing peer in the merge process.<br>`snapshot`: Node always contributes the weights that it had when it reached the stopping criterion, it does not accept merged weights.<br>`active`: Node behaves as if it is in active training, but it does not train merged model with local data as mentioned above.<br>`snapshot` is the default value.<br>|
|`trainingContract`|Training contract associated with this learning. It is a user-defined string. Default value is `defaultbb.cqdb.sml.hpe`. <br> **NOTE**: This parameter enables a user to run <strong>concurrent</strong> swarm learning trainings, within the same swarm network. User must create this training contract using SWCI and then use it as the parameter value.|
|`nodeWeightage`|A number between 1–100 to indicate the relative importance of this node compared with others during the parameter merge process.By default, all nodes are equal and have the same weight-age of one.|
|`mlPlatform`|Specifies ML platform. Allowed values are either TF, KERAS or PYTORCH. If TF platform is used, the default value is KERAS. If PYTORCH platform is used, the default value is PYTORCH.|
|`logger`|Provides information about Python logger. `SwarmCallback` class invokes info, debug, and error methods of this logger for logging. If no logger is passed, then `SwarmCallback` class creates its own logger from basic python logger. If required, user can get hold of this logger instance to change the log level as follows: <br> `import logging` <br> `from swarmlearning.tf import SwarmCallback` <br> `swCallback = SwarmCallback(syncFrequency=128, minPeers=3)` <br> `swCallback.logger.setLevel(logging.DEBUG)`|

3.  Use the `SwarmCallback` object for training the model.

-   For Keras platforms:

-   Pass the object to the list of callbacks in Keras training code. The class methods are invoked automatically.

```
model.fit(..., callbacks = [swarm_callback])
```

-   `SwarmCallback` can be included along with other callbacks also:

```
es_callback = EarlyStopping(...)
model.fit(..., callbacks = [es_callback, swarm_callback])
```

-   For PyTorch platforms, you must invoke the class methods:

-   Call `on_train_begin()` before starting the model training:

```
swarmCallback.on_train_begin()
```

-   Call `on_batch_end()` after the end of each batch training:

```
swarmCallback.on_batch_end()
```

-   Call `on_epoch_end()` after the end of each epoch training:

```
swarmCallback.on_epoch_end(epoch)
```

-   Call `on_train_end()` after the end of the model training:

```
swarmCallback.on_train_end()
```

4.  Run Swarm Learning using the supplied scripts. For more information, see Running Swarm Learning in the with the data and model directories as input parameters.

