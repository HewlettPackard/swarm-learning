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

import datetime
import numpy as np
import os
from swarm import SwarmCallback
import time
import torch 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import pdb
default_max_epochs = 5
default_min_peers = 2
# maxEpochs = 2
trainPrint = True
# tell swarm after how many batches
# should it Sync. We are not doing 
# adaptiveRV here, its a simple and quick demo run
swSyncInterval = 128 

class mnistNet(nn.Module):
    def __init__(self):
        super(mnistNet, self).__init__()
        self.dense = nn.Linear(784, 512)
        self.dropout = nn.Dropout(0.2)
        self.dense1 = nn.Linear(512, 10)
        
    def forward(self, x):
        x = torch.flatten(x, 1)        
        x = self.dense(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.dense1(x)
        output = F.log_softmax(x, dim=1)
        return output
        
def loadData(dataDir):
    # load data from npz format to numpy 
    path = os.path.join(dataDir,'mnist.npz')
    with np.load(path) as f:
        xTrain, yTrain = f['x_train'], f['y_train']
        xTest, yTest = f['x_test'], f['y_test']
        xTrain, xTest = xTrain / 255.0, xTest / 255.0        
        
    # transform numpy to torch.Tensor
    xTrain, yTrain, xTest, yTest = map(torch.tensor, (xTrain.astype(np.float32), 
                                                      yTrain.astype(np.int_), 
                                                      xTest.astype(np.float32),
                                                      yTest.astype(np.int_)))    
    # convert torch.Tensor to a dataset
    yTrain = yTrain.type(torch.LongTensor)
    yTest = yTest.type(torch.LongTensor)
    trainDs = torch.utils.data.TensorDataset(xTrain,yTrain)
    testDs = torch.utils.data.TensorDataset(xTest,yTest)
    return trainDs, testDs
    
def doTrainBatch(model,device,trainLoader,optimizer,epoch,swarmCallback):
    model.train()
    for batchIdx, (data, target) in enumerate(trainLoader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if trainPrint and batchIdx % 100 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                  epoch, batchIdx * len(data), len(trainLoader.dataset),
                  100. * batchIdx / len(trainLoader), loss.item()))
        # Swarm Learning Interface
        if swarmCallback is not None:
            swarmCallback.on_batch_end()        

def test(model, device, testLoader):
    model.eval()
    testLoss = 0
    correct = 0
    with torch.no_grad():
        for data, target in testLoader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            testLoss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    testLoss /= len(testLoader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        testLoss, correct, len(testLoader.dataset),
        100. * correct / len(testLoader.dataset)))    

def main():
    dataDir = os.getenv('DATA_DIR', './data')
    modelDir = os.getenv('MODEL_DIR', './model')
    max_epochs = int(os.getenv('MAX_EPOCHS', str(default_max_epochs)))
    min_peers = int(os.getenv('MIN_PEERS', str(default_min_peers)))
    batchSz = 128 # this gives 97% accuracy on CPU
    trainDs, testDs = loadData(dataDir)
    useCuda = torch.cuda.is_available()
    device = torch.device("cuda" if useCuda else "cpu")  
    model = mnistNet().to(device)
    model_name = 'mnist_pyt'
    opt = optim.Adam(model.parameters())
    trainLoader = torch.utils.data.DataLoader(trainDs,batch_size=batchSz)
    testLoader = torch.utils.data.DataLoader(testDs,batch_size=batchSz)
    
    # Create Swarm callback
    swarmCallback = None
    swarmCallback = SwarmCallback(sync_interval=swSyncInterval,
                                  min_peers=min_peers,
                                  val_data=testDs,
                                  val_batch_size=batchSz,
                                  model_name=model_name,
                                  model=model)
    # initalize swarmCallback and do first sync 
    swarmCallback.on_train_begin()
        
    for epoch in range(1, max_epochs + 1):
        doTrainBatch(model,device,trainLoader,opt,epoch,swarmCallback)      
        test(model,device,testLoader)
        swarmCallback.on_epoch_end(epoch)

    # handles what to do when training ends        
    swarmCallback.on_train_end()

    # Save model and weights
    model_path = os.path.join(modelDir, model_name, 'saved_model.pt')
    # Pytorch model save function expects the directory to be created before hand.
    os.makedirs(os.path.join(modelDir, model_name), exist_ok=True)
    torch.save(model, model_path)
    print('Saved the trained model!')
  
if __name__ == '__main__':
  main()
