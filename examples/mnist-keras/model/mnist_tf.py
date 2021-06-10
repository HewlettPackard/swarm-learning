############################################################################
## Copyright 2021 Hewlett Packard Enterprise Development LP
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
############################################################################

import tensorflow as tf
import numpy as np
import time
import datetime
from swarm import SwarmCallback
import os

default_max_epochs = 5
default_min_peers = 2

def load_data(dataDir):
    """Loads the MNIST dataset.
    # Arguments
        dataDir: path where to find the mnist.npz file
    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    """
    path = os.path.join(dataDir,'mnist.npz') 

    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
    return (x_train, y_train), (x_test, y_test)


def main():
  dataDir = os.getenv('DATA_DIR', './data')
  modelDir = os.getenv('MODEL_DIR', './model')
  modelDir = os.getenv('MODEL_DIR', './model')
  max_epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
  min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))

  model_name = 'mnist_tf'

  (x_train, y_train),(x_test, y_test) = load_data(dataDir)
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
  swarmCallback = SwarmCallback(sync_interval=128,
                                min_peers=min_peers,
                                val_data=(x_test, y_test),
                                val_batch_size=32,
                                model_name=model_name)

  model.fit(x_train, y_train, 
            batch_size = 128,
            epochs=max_epochs,
            verbose=1,            
            callbacks=[swarmCallback])

  # Save model and weights
  model_path = os.path.join(modelDir, model_name)
  model.save(model_path)
  print('Saved the trained model!')

if __name__ == '__main__':
  main()
