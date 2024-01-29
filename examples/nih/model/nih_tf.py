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


# Some the code are being used from below kaggle kernel
#https://www.kaggle.com/code/adamjgoren/nih-chest-x-ray-multi-classification


# Much of this work is inspired by the wonderful kernel 'Train Simple XRay CNN' by Kevin Mader
# Some code fragments are sourced or adapted directly from this Kernel
# I cite his work when appropriate, including URL/Dates, and it can also be referenced here: https://www.kaggle.com/kmader/train-simple-xray-cnn

# Much of my thinking is also guided by Google's nice explanation of AutoML for Vision. General principles are quite useful
# https://cloud.google.com/vision/automl/docs/beginners-guide

# Lastly, I found this article on how AI is changing radiology imaging quite interesting
# https://healthitanalytics.com/news/how-artificial-intelligence-is-changing-radiology-pathology



# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python

# load help packages
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt # basic plotting
import seaborn as sns # additional plotting functionality
import math
from sklearn.utils.class_weight import compute_class_weight

# IMAGE PRE-PROCESSING
# See Keras documentation: https://keras.io/preprocessing/image/
import tensorflow as tf
# Create ImageDataGenerator, to perform significant image augmentation
# Utilizing most of the parameter options to make the image data even more robust
from tensorflow.keras.preprocessing.image import ImageDataGenerator


# Import relevant libraries
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D
from keras.layers import Dropout, Flatten, Dense
from keras.models import Sequential

from tensorflow.keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from sklearn.metrics import roc_curve, auc

from sklearn.metrics import confusion_matrix

import shutil

# Input data files are available in the "input/" directory.
# For example, running the below code (by clicking run or pressing Shift+Enter) will list the files in the input directory
import os

import os
import numpy as np
import csv
import logging
import tensorflow as tf

from swarmlearning.tf import SwarmCallback

import matplotlib.pyplot as plt

from sklearn.metrics import roc_curve, auc
    
    
def auc_analysis(model, test_gen, plotdiagrams=False, saveDir=None):
    print("printing Area Under Curve ")
    # Make predictions using the model
    deep_model_predictions = model.predict(test_gen)
    #print("predictions:", deep_model_predictions)
    
    dummy_labels = test_gen.class_indices
    #print("dummy_labels : ", dummy_labels)
    testSamples = len(test_gen.filenames)
    steps = int(math.ceil(testSamples/batchSize))
    
    #iterations to cover all data, so if batch is 5, it will take total_images/5  iteration 
    test_X , test_Y = [] , []
    for i in range(steps):
        a , b = test_gen.next()
        test_X.extend(a) 
        test_Y.extend(b)
    test_X = np.array(test_X)
    test_Y = np.array(test_Y)
    #print("test_Y is : ", test_Y)
    
    if(plotdiagrams): 
        # create plot
        fig, c_ax = plt.subplots(1,1, figsize = (9, 9))
        for (i, label) in enumerate(dummy_labels):
            fpr, tpr, thresholds = roc_curve(test_Y[:,i].astype(int), deep_model_predictions[:,i])
            c_ax.plot(fpr, tpr, label = '%s (AUC:%0.2f)'  % (label, auc(fpr, tpr)))
            print("%s = AUC is %0.2f"%(label, auc(fpr, tpr)))
        print("-----------------------------------------------\n")
        # Set labels for plot
        c_ax.legend()
        c_ax.set_xlabel('False Positive Rate')
        c_ax.set_ylabel('True Positive Rate')
        savefigPath = os.path.join(saveDir, 'deep_trained_model.png')
        fig.savefig(savefigPath)
    else:
        for (i, label) in enumerate(dummy_labels):
            fpr, tpr, thresholds = roc_curve(test_Y[:,i].astype(int), deep_model_predictions[:,i])
            print("%s = AUC is %0.3f"%(label, auc(fpr, tpr)))
        # added dummy prints otherwise above print is ovveridden by epoch progress
        print("------------------------------------------------\n")

class analysisCallback(tf.keras.callbacks.Callback):
    def __init__(self, test_gen, log_freq=5):
        super(analysisCallback, self).__init__()
        self.test_gen = test_gen
        self.log_freq = log_freq

    def on_epoch_end(self, epoch, logs=None):
        if epoch % self.log_freq == 0:
            auc_analysis(self.model, self.test_gen)


batchSize = 128
defaultMaxEpoch = 100
defaultMinPeers = 2

def main():
    
    print("CURRENT WORKING DIRECTORY :", os.getcwd())
  
    modelName = 'NIH'
    dataDirBase = os.getenv('DATA_DIR', '/platform/data')
    scratchDir = os.getenv('SCRATCH_DIR', '/platform/scratch')
    

    if(scratchDir=="user1"):
        dataDir = os.path.join(dataDirBase, "Node1")
        print("Data dir path is :", dataDir)
    elif(scratchDir=="user2"):
        dataDir = os.path.join(dataDirBase, "Node2")
        print("Data dir path is :", dataDir)
    elif(scratchDir=="user3"):
        dataDir = os.path.join(dataDirBase, "Node3")
        print("Data dir path is :", dataDir)
    else:
        print("============INVALID INPUT DATA PATH================")
        
        
    maxEpoch = int(os.getenv('MAX_EPOCHS', str(defaultMaxEpoch)))
    minPeers = int(os.getenv('MIN_PEERS', str(defaultMinPeers)))
    os.makedirs(scratchDir, exist_ok=True)
    print('***** Starting model =', modelName)

    data_gen = ImageDataGenerator(
            rescale=1./255,
            shear_range=0.2,
            zoom_range=0.2,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True)

    test_gen = ImageDataGenerator(rescale=1./255)

    trainDir = dataDir
    testDir = os.path.join(dataDirBase, "TEST")

    image_size = (128, 128) # image re-sizing target
    print("TRAIN Data gen in progress")
    train_gen = data_gen.flow_from_directory(trainDir, 
                                 target_size = image_size, 
                                 color_mode = 'grayscale', 
                                 batch_size = batchSize, 
                                 class_mode="categorical",
                                 shuffle=True,
                                 seed=42)
    trainSamples = len(train_gen.filenames)
    print("Count of train samples :", trainSamples)
    # Access the class indices
    class_indices = train_gen.class_indices
    # Print the number of unique classes
    num_class_labels = len(class_indices)
    print("Number of unique classes:", num_class_labels)
    print("Class indices:", class_indices)

    print("Valid Data gen in progress")
    test_gen = test_gen.flow_from_directory(testDir, 
                                 target_size = image_size, 
                                 color_mode = 'grayscale', 
                                 batch_size = batchSize, 
                                 class_mode="categorical",
                                 shuffle=False,
                                 seed=42)
    testSamples = len(test_gen.filenames)
    print("Count of test samples :", testSamples)
    
    
    
    
    ## On to the fun stuff! Create a convolutional neural network model to train from scratch

    # Create CNN model
    # Will use a combination of convolutional, max pooling, and dropout layers for this purpose
    model = Sequential()

    #RAD - image shape hardcoded
    model.add(Conv2D(filters = 8, kernel_size = 3, padding = 'same', activation = 'relu', input_shape = (128, 128, 1) ))
    #model.add(Conv2D(filters = 8, kernel_size = 3, padding = 'same', activation = 'relu', input_shape = test_X.shape[1:]))
    model.add(MaxPooling2D(pool_size = 2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters = 16, kernel_size = 3, padding = 'same', activation = 'relu'))
    model.add(MaxPooling2D(pool_size = 2))
    model.add(Dropout(0.2))
              
    model.add(Conv2D(filters = 32, kernel_size = 3, padding = 'same', activation = 'relu'))
    model.add(MaxPooling2D(pool_size = 2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters = 64, kernel_size = 3, padding = 'same', activation = 'relu'))
    model.add(MaxPooling2D(pool_size = 2))
    model.add(Dropout(0.2))
              
    model.add(Conv2D(filters = 128, kernel_size = 3, padding = 'same', activation = 'relu'))
    model.add(MaxPooling2D(pool_size = 3))
    model.add(Dropout(0.2))

    # add in fully connected dense layers to model, then output classifiction probabilities using a softmax activation function
    model.add(Flatten())
    model.add(Dense(500, activation = 'relu'))
    model.add(Dropout(0.2))
    model.add(Dense(num_class_labels, activation = 'softmax'))
    
    opt = Adam(learning_rate=1e-03)
    print("Optimizer is :", opt)

    # compile model, run summary
    #model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    
    model.summary()
    
    
    # Adding swarm callback
    # In SwarmCallBack following parameter is provided to enable displaying training
    # progress or ETA of training on the SLM UI.
    # 'totalEpochs' - Total epochs used in local training.
    swarmCallback = SwarmCallback(syncFrequency=512,
                                  minPeers=minPeers,
                                  adsValData = test_gen,
                                  #adsValData=(test_X, test_Y), 
                                  adsValBatchSize=batchSize,
                                  mergeMethod='mean',
                                  totalEpochs=maxEpoch)
    

    loopback_flag = os.getenv('SWARM_LOOPBACK', "False")

    if(loopback_flag == "True"):
        swarm_active = "NO_SWARM"
    else:
        swarm_active = "SWARM"
    scratchDir = os.path.join(scratchDir, swarm_active)
    
    os.makedirs(scratchDir, exist_ok=True)
    
    # set up a checkpoint for model training
    # https://keras.io/callbacks/
    #checkpointer = ModelCheckpoint(
    #filepath=os.path.join(scratchDir,'weights.best.{epoch:02d}-{val_loss:.2f}.hdf5'), 
    #verbose=1, 
    #save_best_only = True)
    #callbacks_list = [swarmCallback, checkpointer]
    metricsCB = analysisCallback(test_gen=test_gen, log_freq=10)
    callbacks_list = [swarmCallback, metricsCB]

    ## Fit the model!
    print("completed Model quick fit")
    
    print("Model fit with test Generator ")
    model.fit(train_gen, 
                        steps_per_epoch = trainSamples/batchSize, 
                        epochs = maxEpoch, 
                        validation_data = test_gen, 
                        validation_steps=testSamples/batchSize,
                        callbacks = callbacks_list)

    print("completed Model quick fit")
    
    os.path.join(scratchDir)
    #printMetrics(model, test_gen)
    auc_analysis(model, test_gen, plotdiagrams=True, saveDir=os.path.join(scratchDir))
    
    model_path = os.path.join(scratchDir, modelName)
    model.save(model_path)

    print('Saved the trained model!')


if __name__ == '__main__':
    main()
