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
                 val_batch_size = <validation batch size as an integer>,
                 val_data = <either a (x_val, y_val) tuple or a generator>,
                 checkin_model_on_train_end = 'snapshot' <how to checkin model once its local training is over>,
                 node_weightage = 1 <node weightage as an interger between 0 to 100>,
                 ml_platform= <ML platform -'TF'/'KERAS'/'PYTORCH' as a string>, 
                 model_name='swarm_model' <model name as a string>
            )

>NOTE: Some of the parameters have default values as mentioned in above SwarmCallback. User needs to provide values as applicable to use case in work. 

-   sync_interval specifies the number of batches after which a
    synchronization is performed.
-   min_peers specifies the minimum number of network peers required to
    synchronize the insights.
-   use_adaptive_sync specifies whether the *adaptive sync interval*
    feature should be used for tuning the sync interval. This feature is
    turned off by default.
-   val_batch_size specifies the size of each validation batch for
    measuring mean loss. This is used when use_adaptive_sync is turned
    ON.
-   val_data specifies the validation dataset for measuring mean loss.
    It can be either a (x_val, y_val) tuple or a generator. This is used
    when use_adaptive_sync is turned ON.
-   checkin_model_on_train_end specifies which model to check-in once local model training ends at a node. Allowed values: ['inactive', 'snapshot', 'active'].
    
    Specifies how the current model contributes to swarm network learning once the current model training is completed with all epochs. 
It can be anyone of following three types.
    - inactive – Model does not contribute any weights to further merge process. Models’ node weightage set to 0, so that it will be part of Swarm network learning to considered for minimum peers count but not for weight adjustments. It does not check-in any weights to merge process and it also does not consume any weights after merge process.
    - snapshot – Model snapshots its last batch weights as final weights, that means model freezes with last batch training. Model does check-in snapshotted weights to merge process and does not update its weights after merge completion. 
    - active – Model participates in swarm learning process as same as it was doing before its training completed but without local training. Model provides last merged weights as check-in weights and consumes weights after merge process to update its local weights. 
-   node_weightage specifies a number between 0-100 to indicate the relative importance of this node compared to others
-   ml_platform specifies ML platform. Allowed values :['TF','KERAS','PYTORCH']
-   model_name specifies a context-setter for the model being trained. Presently being used for naming the sync files. 


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

