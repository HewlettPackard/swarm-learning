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

import os
import sys
import scipy
from tqdm import tqdm
import cv2
import numpy as np
from PIL import Image
import random
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical

def Dataset_loader(DIR, RESIZE, sigmaX=10):
    IMG = []
    read = lambda imname: np.asarray(Image.open(imname).convert("RGB"))
    for IMAGE_NAME in tqdm(os.listdir(DIR)):
        PATH = os.path.join(DIR,IMAGE_NAME)
        _, ftype = os.path.splitext(PATH)
        if ftype == ".png":
            img = read(PATH)
           
            img = cv2.resize(img, (RESIZE,RESIZE))
           
            IMG.append(np.array(img))
    return IMG

if __name__ == "__main__":

    dir = sys.argv[1]

    dir_benign=dir+"/BreaKHis_v1/histology_slides/breast/benign/SOB"
    dir_malig=dir+"/BreaKHis_v1/histology_slides/breast/malignant/SOB" 

    ben=[]
    for i in os.listdir(dir_benign):
        for j in os.listdir(dir_benign+'/'+i):
            ben.append(dir_benign+'/'+i+'/'+j+'/40X')

    benign=[]
    for i in ben:
        benign.append(np.array(Dataset_loader(i,224)))

    mal=[]
    for i in os.listdir(dir_malig):
        for j in os.listdir(dir_malig+'/'+i):
            mal.append(dir_malig+'/'+i+'/'+j+'/40X')

    malig=[]
    for i in mal:
        malig.append(np.array(Dataset_loader(i,224)))

    Benign=[]
    for i in benign:
        for j in i:
            Benign.append(j)
    Malign=[]
    for i in malig:
        for j in i:
            Malign.append(j)

    random.shuffle(Benign)
    benign_train, benign_test = train_test_split(Benign, train_size=0.75, test_size=0.25)

    random.shuffle(Malign)
    malign_train, malign_test = train_test_split(Malign, train_size=0.75, test_size=0.25)

    # Skin Cancer: Malignant vs. Benign
    # Create labels
    benign_train_label = np.zeros(len(benign_train))
    malign_train_label = np.ones(len(malign_train))
    benign_test_label = np.zeros(len(benign_test))
    malign_test_label = np.ones(len(malign_test))

    # Merge data 
    X_train_1 = np.concatenate((benign_train, malign_train), axis = 0)
    Y_train_1 = np.concatenate((benign_train_label, malign_train_label), axis = 0)
    X_test_1 = np.concatenate((benign_test, malign_test), axis = 0)
    Y_test_1 = np.concatenate((benign_test_label, malign_test_label), axis = 0)

    # Shuffle train data
    s = np.arange(X_train_1.shape[0])
    np.random.shuffle(s)
    X_train_1 = X_train_1[s]
    Y_train_1 = Y_train_1[s]

    # Shuffle test data
    s = np.arange(X_test_1.shape[0])
    np.random.shuffle(s)
    X_test_1 = X_test_1[s]
    Y_test_1 = Y_test_1[s]

    # To categorical
    Y_train_1 = to_categorical(Y_train_1, num_classes= 2)
    Y_test_1 = to_categorical(Y_test_1, num_classes= 2)

    np.savez('./workspace/breakhis/ml-context/train.npz', X_train_1, Y_train_1)
    np.savez('./workspace/breakhis/ml-context/test', X_test_1, Y_test_1)

    
