############################################################################
## (C)Copyright 2022 Hewlett Packard Enterprise Development LP
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

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import keras
from keras.models import Sequential
from keras.layers import Dense
from sklearn.metrics import cohen_kappa_score, accuracy_score, recall_score

import logging
import os

import numpy as np
from six.moves import cPickle
from swarmlearning.tf import SwarmCallback
import sys


default_max_epochs = 256
default_min_peers = 2
batch_size = 35
num_classes = 10

data_dir = os.getenv('DATA_DIR', '/platform/swarmml/data')
model_dir = os.getenv('MODEL_DIR', '/platform/swarmml/model')
epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))

save_dir = os.path.join(model_dir, 'saved_models')
model_name = 'cancer-pred.h5'

col_names=['id','diagnosis','radius_mean','texture_mean','perimeter_mean','area_mean','smoothness_mean','compactness_mean','concavity_mean','concave points_mean','symmetry_mean','fractal_dimension_mean','radius_se','texture_se','perimeter_se','area_se','smoothness_se','compactness_se','concavity_se','concave points_se','symmetry_se','fractal_dimension_se','radius_worst','texture_worst','perimeter_worst','area_worst','smoothness_worst','compactness_worst','concavity_worst','concave points_worst','symmetry_worst','fractal_dimension_worst']
df=pd.read_csv(<dataset-file-path>)

df=df[col_names]

#Train and test splits
train_split, test = train_test_split(df, test_size=0.2, random_state=4)

#Dividing the train set across the two nodes.
train1, train2 = train_test_split(train_split, test_size=0.5, random_state=4)

#Use train1 or train2 according to the node on which the script is running
train=train1
#train=train2

X_train=train.iloc[:,2:].values
y_train=train.iloc[:,1].values

labelencode = LabelEncoder()
y_train=labelencode.fit_transform(y_train)

test.drop("Unnamed: 32",axis=1,inplace=True)

X_test=test.iloc[:,2:].values
y_test=test.iloc[:,1].values

y_test=labelencode.fit_transform(y_test)

sc=StandardScaler()
X_train=sc.fit_transform(X_train)
sc2=StandardScaler()
X_test=sc2.fit_transform(X_test)


classifier = Sequential()
# ADD YOUR MODEL CODE HERE

#adding the input and first hidden layer
classifier.add(Dense(16, activation='relu', kernel_initializer='glorot_uniform',input_dim=30))
#adding second layer
classifier.add(Dense(6, activation='relu', kernel_initializer='glorot_uniform'))
#adding the output layer
classifier.add(Dense(1, kernel_initializer='uniform', activation='sigmoid'))

print('--------------------------------------------------------------')
print('Model Summary:')
print(classifier.summary())
print('--------------------------------------------------------------')

# Let's train the model
classifier.compile(optimizer='Adam',loss='binary_crossentropy',metrics=['accuracy'])

# Create SwarmCallback
swarmCallback = SwarmCallback(syncFrequency=26,
                              minPeers=min_peers,
                              useAdaptiveSync=False,
                              adsValData=(X_test, y_test),
                              adsValBatchSize=batch_size)
swarmCallback.logger.setLevel(logging.DEBUG)

# Add SwarmCallback during training
classifier.fit(X_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          #validation_data=(X_test,y_test),
          shuffle=True,
          callbacks=[swarmCallback])

# Save model and weights
swarmCallback.logger.info('Saving the final Swarm model ...')
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
classifier.save(model_path)
swarmCallback.logger.info(f'Saved the trained model - {model_path}')

red = classifier.predict(X_test)
mean=sum(red) / len(red)
for i in range(len(red)):
  if red[i] >= mean:
    red[i] = 1
  else:
    red[i] = 0

# Inference
swarmCallback.logger.info('Starting inference on the test data ...')
loss, acc = classifier.evaluate(X_test, y_test, verbose=1)
swarmCallback.logger.info('Test acc actual= %.5f' % (accuracy_score(y_test,red)))
swarmCallback.logger.info('Test loss = %.5f' % (loss))
swarmCallback.logger.info('Test accuracy = %.5f' % (acc))
