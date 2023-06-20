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
############################################################################

import os
import numpy as np
import csv
import logging
import tensorflow as tf

from swarmlearning.tf import SwarmCallback


def getXY(dataSet):
    np.random.shuffle(dataSet)
    length = np.size(dataSet,0)
    X = dataSet[0:length, :-1]
    y = dataSet[0:length, -1:]
    return X , y


# Constants
testFileName = 'SB19_CCFDUBL_BAL_TEST_2C.csv'
fileNameList = [
    'SB19_CCFDUBL_BAL_TRAIN_2C.csv'
  , 'SB19_CCFDUBL_BAL_P1_2C.csv'
  , 'SB19_CCFDUBL_BAL_P2_2C.csv'
  , 'SB19_CCFDUBL_BAL_P3_2C.csv'
]

part = 0
batchSize = 32
defaultMaxEpoch = 1000
defaultMinPeers = 2

def main():
  modelName = 'fraud-detection'
  dataDir = os.getenv('DATA_DIR', '/platform/data')
  scratchDir = os.getenv('SCRATCH_DIR', '/platform/scratch')
  maxEpoch = int(os.getenv('MAX_EPOCHS', str(defaultMaxEpoch)))
  minPeers = int(os.getenv('MIN_PEERS', str(defaultMinPeers)))
  os.makedirs(scratchDir, exist_ok=True)
  print('***** Starting model =', modelName)
  # ================== load test and train Data =========================
  print('-' * 64)
  fname = fileNameList[part]
  trainFile = dataDir + '/' + fname
  print("loading train dataset %s .." % trainFile)
  with open(trainFile, 'r') as f:
    # first line is the header row so remove it
    trainData = np.array(list(csv.reader(f, delimiter=","))[1:], dtype=float)
    print('size of training Data set : %s' % np.size(trainData,0))

  print('-' * 64)
  testFile = dataDir + '/' + testFileName
  print("loading test dataset %s .." % testFile)
  with open(testFile, 'r') as f:
    # first line is the header row so remove it
    testData = np.array(list(csv.reader(f, delimiter=","))[1:], dtype=float)

  print('-' * 64)
  # ================== Model to train and evaluate =========================
  # logistic regression Model
  model = tf.keras.models.Sequential()
  model.add(tf.keras.layers.Dense(1, input_shape=(30,), activation='sigmoid',
    kernel_initializer='random_uniform', bias_initializer='zeros'))
  sgd = tf.keras.optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
  model.compile(loss = 'binary_crossentropy', optimizer=sgd, metrics=['accuracy'])
  print(model.summary())

  print('Starting training ...')
  x_train, y_train = getXY(trainData)
  x_test, y_test = getXY(testData)

  # Adding swarm callback
  swarmCallback = SwarmCallback(syncFrequency=128, minPeers=minPeers)

  # Model training
  model.fit(
      x_train
    , y_train
    , batch_size=batchSize
    , epochs=maxEpoch
    , validation_data=(x_test, y_test)
    , shuffle=True
    , callbacks=[swarmCallback]
  )

  print('Training done!')

  # Evaluate
  scores = model.evaluate(x_test, y_test, verbose=1)
  print('***** Test loss:', scores[0])
  print('***** Test accuracy:', scores[1])

  # Save
  model_path = os.path.join(scratchDir, modelName)
  model.save(model_path)
  print('Saved the trained model!')


if __name__ == '__main__':
    main()
