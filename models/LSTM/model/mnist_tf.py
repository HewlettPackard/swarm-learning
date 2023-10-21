############################################################################
## (C)Copyright 2021-2023 Hewlett Packard Enterprise Development LP
## Licensed under the Apache License, Version 2.0 (the "License"); you may
## not use this file except in compliance with the License. You may obtain
## a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations
## under the License.


## Change history for mnist.py 
## These changes are listed in decreasing version number order. Note this can be different from a strict chronological order when there are two branches in development at the same time.

## *** New Features 
## Modified to run on a Swarm Learning platform.

## *** Changes 
## Version _0_ to _1_ 
## Reading mnist.npz data instead of loading from keras datasets.
## Added SwarmCallback and supporting code updates to enable Swarm Learning training.
## Added model saving code.
## Added inferencing with Test data.

## version: 1
## Feature: Swarmified mnist tensorflow model
## Fix: 
## Debug: 
############################################################################

import tensorflow as tf
from tensorflow.keras.datasets import mnist
import numpy as np
import time
import datetime
from swarmlearning.tf import SwarmCallback
import os
import logging

default_max_epochs = 5
default_min_peers = 2

def load_data():
    """Loads the MNIST dataset.
    # The data, split between train and test sets:
    # Refer - https://keras.io/api/datasets/mnist/.
    """
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    return (x_train, y_train), (x_test, y_test)


def main():
  modelDir = os.getenv('MODEL_DIR', '/platform/model')
  max_epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
  min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))
  scratchDir = os.getenv('SCRATCH_DIR', '/platform/scratch')
  os.makedirs(scratchDir, exist_ok=True)
  model_name = 'mnist_tf'

  (x_train, y_train),(x_test, y_test) = load_data()
  x_train, x_test = x_train / 255.0, x_test / 255.0

  model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(512, activation=tf.nn.relu),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
  ])

  model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

  # Create Swarm callback
  swarmCallback = SwarmCallback(syncFrequency=128,
                                minPeers=min_peers,
                                useAdaptiveSync=False,
                                adsValData=(x_test, y_test),
                                adsValBatchSize=8)
  swarmCallback.logger.setLevel(logging.DEBUG)

  model.fit(x_train, y_train, 
            batch_size = 128,
            epochs=max_epochs,
            verbose=1,            
            callbacks=[swarmCallback])

  # Save model and weights
  print('Saving the final Swarm model ...')
  swarmCallback.logger.info('Saving the final Swarm model ...')
  model_path = os.path.join(scratchDir, model_name)
  model.save(model_path)
  print('Saved the trained model!')
  swarmCallback.logger.info(f'Saved the trained model - {model_path}')

  swarmCallback.logger.info('Starting inference on the test data ...')
  loss, acc = model.evaluate(x_test, y_test)
  swarmCallback.logger.info('Test loss = %.5f' % (loss))
  swarmCallback.logger.info('Test accuracy = %.5f' % (acc))

if __name__ == '__main__':
  main()
