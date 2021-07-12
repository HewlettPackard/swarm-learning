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
            min_peers = <peer count>,
            sync_interval = <interval>,
            use_adaptive_sync = <bool>,
            val_batch_size = <batch size>,
            val_data = <either a (x_val, y_val) tuple or a generator>
            )

-   min_peers specifies the minimum number of network peers required to
    synchronize the insights.

-   sync_interval specifies the number of batches after which a
    synchronization is performed.

-   use_adaptive_sync specifies whether the *adaptive sync interval*
    feature should be used for tuning the sync interval. This feature is
    turned off by default.

-   val_batch_size specifies the size of each validation batch for
    measuring mean loss. This is used when use_adaptive_sync is turned
    ON.

-   val_data specifies the validation dataset for measuring mean loss.
    It can be either a (x_val, y_val) tuple or a generator. This is used
    when use_adaptive_sync is turned ON.

 The parameters for this call are keyword-only parameters and
 therefore, must be named when the function is invoked. Except for
 use_adaptive_sync, none of the other parameters have default values.
 They must be specified.

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

