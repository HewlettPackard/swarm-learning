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

from __future__ import print_function
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import os

import numpy as np
from six.moves import cPickle
from swarm import SwarmCallback
import sys


# Substitute for keras.datasets.cifar10.load_data().
# The original function downloads the dataset to use.
# Instead, we use a local copy that is available in the data directory.
def cifar10_load_data(data_dir='/platform/swarmml/data'):
    """Loads CIFAR10 dataset.

    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    """

    def cifar10_load_batch(batch_file, label_key='labels'):
        """Internal utility for parsing CIFAR data.

        # Arguments
            batch_file: path to the batch file to parse.
            label_key: key for label data in the retrieve dictionary.

        # Returns
            A tuple `(data, labels)`.
        """
        with open(batch_file, 'rb') as f:
            if sys.version_info < (3,):
                d = cPickle.load(f)
            else:
                d = cPickle.load(f, encoding='bytes')
                # decode utf8
                d_decoded = {}
                for k, v in d.items():
                    d_decoded[k.decode('utf8')] = v
                d = d_decoded

        data = d['data']
        labels = d[label_key]

        data = data.reshape(data.shape[0], 3, 32, 32)
        return data, labels


    num_train_samples = 50000

    x_train = np.empty((num_train_samples, 3, 32, 32), dtype='uint8')
    y_train = np.empty((num_train_samples,), dtype='uint8')

    for i in range(1, 6):
        batch_file = os.path.join(data_dir, 'data_batch_' + str(i))
        (
            x_train[(i - 1) * 10000: i * 10000, :, :, :]
          , y_train[(i - 1) * 10000: i * 10000]
        ) = cifar10_load_batch(batch_file)

    batch_file = os.path.join(data_dir, 'test_batch')
    x_test, y_test = cifar10_load_batch(batch_file)

    y_train = np.reshape(y_train, (len(y_train), 1))
    y_test = np.reshape(y_test, (len(y_test), 1))

    x_train = x_train.transpose(0, 2, 3, 1)
    x_test = x_test.transpose(0, 2, 3, 1)

    return (x_train, y_train), (x_test, y_test)


data_dir = '/platform/swarmml/data'
model_dir = '/platform/swarmml/model'

batch_size = 32
num_classes = 10

# The original number of epochs was 100. However, that makes the test run for a
# very long time. So, we have reduced it somewhat drastically. We want to show
# the concepts of the Swarm Learning platform with these examples - we are not
# particularly concerned about producing the best and most accurate model here.
epochs = 3

# data_augmentation = True
num_predictions = 20
# save_dir = os.path.join(os.getcwd(), 'saved_models')
save_dir = os.path.join(model_dir, 'saved_models')
model_name = 'keras_cifar10_trained_model.h5'

# The data, split between train and test sets:
# (x_train, y_train), (x_test, y_test) = cifar10.load_data()
(x_train, y_train), (x_test, y_test) = cifar10_load_data(data_dir)
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

model = Sequential()
model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:]))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes))
model.add(Activation('softmax'))

# initiate RMSprop optimizer
opt = keras.optimizers.RMSprop(learning_rate=0.0001, decay=1e-6)

# Let's train the model using RMSprop
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

swarm_callback = SwarmCallback(min_peers=4,
                               sync_interval=10,
                               val_data=(x_test, y_test),
                               val_batch_size=batch_size)

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          validation_data=(x_test, y_test),
          shuffle=True,
          callbacks=[swarm_callback])

# Save model and weights
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
print('Saved trained model at %s ' % model_path)

# Score trained model.
scores = model.evaluate(x_test, y_test, verbose=1)
print('Test loss:', scores[0])
print('Test accuracy:', scores[1])
