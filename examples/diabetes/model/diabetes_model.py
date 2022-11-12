############################################################################

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
from swarm.tf import SwarmCallback
import os

default_max_epochs =  100
default_min_peers = 3


def load_data(dataDir):
    """Loads the diabetes dataset.
    # Arguments
        dataDir: path where to find the diabetes.npz file
    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    """
    path = os.path.join(dataDir,'diabetes.npz') 

    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
    return (x_train, y_train), (x_test, y_test)



def main():
  dataDir = os.getenv('DATA_DIR', './data')
  modelDir = os.getenv('MODEL_DIR', './model')
  max_epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
  min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))

  model_name = 'diabetes'

  (x_train, y_train),(x_test, y_test) = load_data(dataDir)
  
  from sklearn.preprocessing import StandardScaler

  sc = StandardScaler()
  x_train = sc.fit_transform(x_train)
  x_test = sc.transform(x_test)

  model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(100, kernel_initializer = 'uniform', activation = 'relu', input_shape = (14,)),
    tf.keras.layers.Dense(54, kernel_initializer = 'uniform',activation = 'relu'),
    tf.keras.layers.Dense(34, kernel_initializer = 'uniform',activation = 'relu'),
    tf.keras.layers.Dense(24, kernel_initializer = 'uniform',activation = 'relu'),
    tf.keras.layers.Dense(1, kernel_initializer = 'uniform', activation = 'sigmoid')
  ])


  model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])

  

  # Create Swarm callback
  swarmCallback = SwarmCallback(syncFrequency=32,
                                min_peers=min_peers,
                                adsValdata=(x_test, y_test),
                                adsValBatchSize=16,
                                model_name=model_name)

  swarmCallback.logger.setLevel(logging.DEBUG)

  model.fit(x_train, y_train, 
            batch_size = 16,
            epochs=max_epochs,
            verbose=1,
            callbacks = [swarmCallback])
            
  print('Training done!')

  # Evaluate
    
  train_scores = model.evaluate(x_train, y_train)
  print('***** Train loss:', train_scores[0])
  print('***** Train accuracy:', train_scores[1])
  
  
  scores = model.evaluate(x_test, y_test)
  print('***** Test loss:', scores[0])
  print('***** Test accuracy:', scores[1])
  
  y_pred = model.predict(x_test)
  
  from sklearn.metrics import confusion_matrix
  cm = confusion_matrix(y_test, y_pred.round(0))

  print(cm)

  # Save model and weights
  print('Saving the final Swarm model ...')
  swarmCallback.logger.info('Saving the final Swarm model ...')
  model_path = os.path.join(modelDir, model_name)
  model.save(model_path)
  print('Saved the trained model!')
  swarmCallback.logger.info(f'Saved the trained model - {model_path}')

if __name__ == '__main__':
  main()
