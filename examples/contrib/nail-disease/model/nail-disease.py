# -*- coding: utf-8 -*-
import numpy as np
import os
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dense,Flatten,Conv2D,Activation,Dropout
from keras import backend as K
import keras
from keras.models import Sequential, Model
from keras.models import load_model
from keras.optimizers import gradient_descent_v2
from keras.callbacks import EarlyStopping,ModelCheckpoint
from keras.layers import MaxPool2D


from keras.applications.inception_v3 import InceptionV3
from keras.callbacks import ReduceLROnPlateau

import tensorflow as tf

from swarmlearning.tf import SwarmCallback
import sys

print(tf.config.list_physical_devices('GPU'))

default_max_epochs = 5
default_min_peers = 2
data_dir = os.getenv('DATA_DIR', '/platform/swarmml/data')
model_dir = os.getenv('MODEL_DIR', '/platform/swarmml/model')
epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))
batch_size = 16

save_dir = os.path.join(model_dir, 'saved_models')
model_name = 'vgg16.h5'

train_path=data_dir+"/train"
test_path=data_dir+"/test"
class_names=os.listdir(train_path)
class_names_test=os.listdir(test_path)
path = data_dir
num_classes=len(class_names)

print(class_names)
print(class_names_test)


train_datagen=ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.8,
    #rotation_range=80
    #horizontal_flip=True
    )
test_datagen=ImageDataGenerator(rescale=1./255)


input_shape=(224,224,3)
train_generator =train_datagen.flow_from_directory(train_path,shuffle=False,target_size=(224,224),batch_size=batch_size)


IMAGE_SIZE = [224, 224]
inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)
# We don't need to train existing weights
for layer in inception.layers:
    layer.trainable = False

# Model layers -> can add more if required
x = Flatten()(inception.output)
prediction = Dense(num_classes, activation='softmax')(x)
# Create a model object
model = Model(inputs=inception.input, outputs=prediction)
# View the structure of the model
model.summary()

validation_generator = test_datagen.flow_from_directory(
                       test_path,
                       target_size=(224, 224),
                       batch_size=batch_size)


mc = ModelCheckpoint(save_dir+'/best_model.h5', monitor='val_accuracy', mode='max', save_best_only=True)

model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])

swarmCallback = SwarmCallback(syncFrequency=3,
                              minPeers=min_peers,
                              useAdaptiveSync=False,
                              adsValData=(validation_generator),
                              adsValBatchSize=batch_size)

history4 = model.fit(
    train_generator,
    steps_per_epoch=None,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=None,
    verbose=1,
    callbacks=[swarmCallback, ReduceLROnPlateau(monitor='val_loss', factor=0.3,patience=3, min_lr=0.000001), mc],
    shuffle=False)


swarmCallback.logger.info('Saving the final Swarm model ...')
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
swarmCallback.logger.info(f'Saved the trained model - {model_path}')

loss, acc = model.evaluate(validation_generator)
swarmCallback.logger.info('Test loss = %.5f' % (loss))
swarmCallback.logger.info('Test accuracy = %.5f' % (acc))
