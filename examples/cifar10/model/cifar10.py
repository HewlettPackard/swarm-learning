############################################################################
## (C)Copyright 2021,2022 Hewlett Packard Enterprise Development LP
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

from __future__ import print_function
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import RMSprop
import logging
import os

import numpy as np
from six.moves import cPickle
from swarmlearning.tf import SwarmCallback
import sys


default_max_epochs = 5
default_min_peers = 2
batch_size = 32
num_classes = 10

data_dir = os.getenv('DATA_DIR', '/platform/swarmml/data')
model_dir = os.getenv('MODEL_DIR', '/platform/swarmml/model')
epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))

save_dir = os.path.join(model_dir, 'saved_models')
model_name = 'cifar10.h5'

# The data, split between train and test sets:
# Refer - https://keras.io/api/datasets/cifar10/
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
assert x_train.shape == (50000, 32, 32, 3)
assert x_test.shape == (10000, 32, 32, 3)
assert y_train.shape == (50000, 1)
assert y_test.shape == (10000, 1)


print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

model = Sequential()
# ADD YOUR MODEL CODE HERE
# Following Tiny model is given for quick demo
model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:]))
model.add(Activation('relu'))
model.add(Flatten())
model.add(Dense(num_classes))
model.add(Activation('softmax'))

print('--------------------------------------------------------------')
print('Model Summary:')
print(model.summary())
print('--------------------------------------------------------------')

# initiate RMSprop optimizer
opt = RMSprop(learning_rate=0.0001, decay=1e-6)

# Let's train the model
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

# Create SwarmCallback
swarmCallback = SwarmCallback(syncFrequency=128,
                              minPeers=min_peers,
                              useAdaptiveSync=False,
                              adsValData=(x_test, y_test),
                              adsValBatchSize=batch_size)
swarmCallback.logger.setLevel(logging.DEBUG)

# Add SwarmCallback during training
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          validation_data=(x_test, y_test),
          shuffle=True,
          callbacks=[swarmCallback])

# Save model and weights
swarmCallback.logger.info('Saving the final Swarm model ...')
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
swarmCallback.logger.info(f'Saved the trained model - {model_path}')

# Inference
swarmCallback.logger.info('Starting inference on the test data ...')
loss, acc = model.evaluate(x_test, y_test, verbose=1)
swarmCallback.logger.info('Test loss = %.5f' % (loss))
swarmCallback.logger.info('Test accuracy = %.5f' % (acc))
