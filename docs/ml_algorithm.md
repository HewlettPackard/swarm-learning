# Adapting ML programs for Swarm Learning 

You can transform any Keras (with TensorFlow 2 backend) or PyTorch based ML
program that has been written using Python3 into a Swarm Learning ML
program by making a few simple changes to the model training code, such
as updating the paths from where the program reads and writes data; and
including the Swarm Callback object. See the [examples](../examples) included with the
Swarm Learning package for sample code.

![](images/sl_ml_algorithm.png)

To convert a ML program into a Swarm Learning ML program:

1.  Change the program to read all its data from files and
    subdirectories inside the data directory, ``/platform/swarmml/data``.

2.  Change the program to write all its output to the model directory,
    ``/platform/swarmml/model``. This includes writing of the trained model
    with the final weights.

3.  Import SwarmCallback class from the swarm library:

        from swarm import SwarmCallback

 SwarmCallback is a custom callback class that consists of a set of
 functions that can be applied at various stages of the training
 process. These functions provide a view of the internal states and
 statistics of the model during training. SwarmCallback executes Swarm
 Learning specific operations during training like sharing insights
 with all the network peers at the end of a sync interval.

 For TensorFlow-based Keras platforms, SwarmCallback is based on the
 Keras ``tf.keras.callbacks.Callback class``. The methods of this class are
 called automatically by Keras at appropriate stages of the training.

 Unlike Keras, PyTorch does not have an in-built Callback class.
 Therefore, on PyTorch-based platforms, the user should call the
 methods of this class. These methods are described later in this
 section. An example of their usage is shown in the MNIST sample
 program.
     
   4.  Instantiate an object of the SwarmCallback class

      swarm_callback = SwarmCallback(
                 sync_interval = <batch interval as integer>,
                 min_peers = <minimum peers count as an integer>,
                 use_adaptive_sync = False <boolean>,
                 val_data = <either a (x_val, y_val) tuple or a generator>,
                 val_batch_size = <batch size of val_data as an integer>,
                 checkin_model_on_train_end = 'snapshot' <how to checkin model once its local training is over>,
                 node_weightage = 1 <node weightage as an interger between 0 to 100>,
                 ml_platform= <ML platform -'TF'/'KERAS'/'PYTORCH' as a string>, 
                 model_name='swarm_model' <model name as a string>
            )

>NOTE: Some of the parameters have default values as mentioned in above SwarmCallback. User needs to provide values as applicable to use case in work. 

-   'sync_interval' specifies the number of batches after which a
    synchronization is performed.
-   'min_peers' specifies the minimum number of network peers required to
    synchronize the insights.
-   'use_adaptive_sync' specifies whether the *adaptive sync interval*
    feature should be used for automatically generating the the sync interval. This feature is
    turned off by default.
-   'val_data' specifies the dataset for generating metrics for adaptive sync logic. It can be either a (x_val, y_val) tuple or a generator. This is used
    when use_adaptive_sync is turned ON.
-   'val_batch_size' specifies the batch size for 'val_data' dataset. This is used when use_adaptive_sync is turned ON.
-   'checkin_model_on_train_end' specifies the merge behaviour of a SL node *after* it has achieved stopping criterion and it is waiting for all other peers to complete their training. During this period this ***SL node will not train model with local data***. This parameter decides the nature of the weights that this SL node will contribute to the merge process. 

    Allowed values: ['inactive', 'snapshot', 'active'].
    - inactive – Node does not contribute its weights in the merge process but participates as non-contributing peer in the merge process.
    - snapshot – Node always contributes the weights that it had when it reached the stopping criterion, it will not accept merged weights. 
    - active – Node behaves as if it is in active training, but it will not train merged model with local data as mentioned above. 
-   'node_weightage' specifies a number between 0-100 to indicate the *relative* importance of this node compared to other nodes.
-   'ml_platform' specifies ML platform. Allowed values :['TF','KERAS','PYTORCH']
-   'model_name' used internally as a tag to identify the training session.   


 The parameters for this call are keyword-only parameters and
 therefore, must be named when the function is invoked. 

5.  Use the SwarmCallback object for training the model.

    -   For Keras platforms:

        -   Pass the object to the list of callbacks in Keras training
            code. The class methods are invoked automatically

             ``model.fit(..., callbacks = [swarm_callback])``

        -   SwarmCallback can be included along with other callbacks also:

             es_callback = EarlyStopping(...)
               model.fit(..., callbacks = [es_callback, swarm_callback])

    -   For PyTorch platforms, the class methods should be invoked by the user:

        -    Call on_train_begin() before starting the model training

             swarmCallback.on_train_begin()

        -   Call on_batch_end() after end of each batch training

            swarmCallback.on_batch_end()

        -   Call on_epoch_end() after end of each epoch training

            swarmCallback.on_epoch_end(epoch)

        -   Call on_train_end() after end of the model training

            swarmCallback.on_train_end()

6.  Place this modified program in the model directory,
    ``/platform/swarmml/model``. Place the datasets for the program in the
    data directory, ``/platform/swarmml/data``.

7.  Run Swarm Learning using the supplied scripts (see [Running Swarm Learning](RunningSL.md)) with the data and model directories as input parameters.

