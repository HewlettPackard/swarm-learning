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


df=pd.read_csv("https://raw.githubusercontent.com/Akhil-2001/DecentralizedML-Cancer-Prediction/main/diag-data/train1-diag.csv")

df.drop("Unnamed: 32",axis=1,inplace=True)
#dropping the last column (an empty last column)

X_train=df.iloc[:,2:].values
y_train=df.iloc[:,1].values

labelencode = LabelEncoder()
y_train=labelencode.fit_transform(y_train)

df2=pd.read_csv("https://raw.githubusercontent.com/Akhil-2001/DecentralizedML-Cancer-Prediction/main/diag-data/test-diag.csv")

df2.drop("Unnamed: 32",axis=1,inplace=True)

X_test=df2.iloc[:,2:].values
y_test=df2.iloc[:,1].values

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
