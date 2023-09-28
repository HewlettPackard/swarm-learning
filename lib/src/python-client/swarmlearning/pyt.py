#######################################################################
## (C)Copyright 2023 Hewlett Packard Enterprise Development LP
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
#######################################################################


##################################################################
# This file is the main entry point for Swarm Learning for Pytorch
# platform. Users can integrate Swarm framework into their 
# model code by creating an instance of the SwarmCallback class and 
# calling its methods at different phases of training.
##################################################################

from __future__ import print_function
import torch
from swarmlearning.client.swarm import SwarmCallbackBase, SLPlatforms

import torchmetrics
import sys

# Default Training contract used for learning if not specified by user. 
# Any update to default contract needs similar modifications 
# in all applicable ML platforms (TF, PYT, etc)
DEFAULT_TRAINING_CONTRACT = 'defaultbb.cqdb.sml.hpe'

class SwarmCallback(SwarmCallbackBase):
    '''
    This is the customized callback class sub-classed from 
    SwarmCallbackBase class that implements different swarm 
    functionalities. It implements the methods like 
    on_train_begin, on_batch_end etc and calls different 
    methods of SwarmCallbackBase.
    '''

    # Creating Pytorch context
    # Put all artifacts needed to interface with ML platform here
    class pyTorchContext:
        def __init__(self, model):
            self.model = model


    def __init__(self, syncFrequency, minPeers, trainingContract=DEFAULT_TRAINING_CONTRACT, **kwargs):
        '''
        This function initializes the various Swarm network parameters, which 
        are described below -
        :param syncFrequency: Batches of local training to be performed between 
                              2 swarm sync rounds. If adaptive sync enabled, this 
                              is the frequency to be used at the start.
        :param minPeers: Min peers required during each sync round for Swarm to 
                          proceed further.
        :param trainingContract: Training contract associated with this learning. 
                                 Default value is 'defaultbb.cqdb.sml.hpe'.
        :param useAdaptiveSync: Modulate the next interval length post each sync 
                                  round based on perf on validation data.
        :param adsValData: Validation dataset - (X,Y) tuple or generator - used 
                             for adaptive sync
        :param adsValBatch_size: Validation data batch size
        :param checkinModelOnTrainEnd: Indicates which model to check-in once 
                                           local model training ends at a node.
                                           Allowed values: ['inactive', 'snapshot', 
                                           'active']
        :param mergeMethod: Indicates the type of merge technique used for swarm merge. 
        :param nodeWeightage: A number between 1-100 to indicate the relative 
                               importance of this node compared to others
        :param mlPlatform: 'Pytorch' ML Platform
        :param model: Pytorch model
        :param logger: Basic Python logger. SwarmCallback class will invoke info, 
                       debug and error methods of this logger to fulfil its need.
                       If no logger is passed, then SwarmCallback class will create 
                       its own logger from basic python logger. If required, user 
                       can get hold of this logger instance to change the log level 
                       as follows -
                       import logging
                       from swarmlearning.pyt import SwarmCallback                       
                       swCallback = SwarmCallback(syncFrequency=128, minPeers=3)
                       swCallback.logger.setLevel(logging.DEBUG)
        :param totalEpochs: Total epochs used in local training. 
                            This is needed to display training progress or ETA of training.
                            WARNING: "With out this, training progress display might have some limitations."
        :param lossFunction: Name of the loss function to be used for loss computation.
                             Loss computed will be used for display and adaptive sync frequency.
                             WARNING : "User is responsible to pass the same loss function used for 
                             local training. If the loss function is not matching, it can result in differences 
                             in loss displayed by Swarm and actual loss used in the local model training."
                             lossFunction string should match with loss function class defined in pyTorch
                             https://pytorch.org/docs/stable/nn.html#loss-functions
                             For example, to use CLASS torch.nn.NLLLoss() - lossFunction value is "NLLLoss"
        :param lossFunctionArgs: Dictionary with parameters (as keys) to be used in lossFunction.
                                 https://pytorch.org/docs/stable/nn.html#loss-functions
                                 For example, to use CLASS torch.nn.NLLLoss(weight=None, size_average=None, 
                                                           ignore_index=- 100, reduce=None, reduction='mean')
                                 lossFunctionArgs is used to pass any mandatory parameters or 
                                 overwrite any default parameters defined in class. 
                                 If 'reduction' needs to be of 'sum', then 
                                 create dictionary - lFArgsDict={} ; lFArgsDict['reduction']='sum' 
                                 pass it through SwarmCallback - 
                                 SwarmCallback(...
                                    lossFunction="NLLLoss",
                                    lossFunctionArgs=lFArgsDict
                                    ...)
        :param metricFunction: Name of metric function to be used for metrics computation.
                               Metrics computed will be used for display.
                               WARNING : "User is responsible to pass the same metric function used for 
                               local training. If the metric function is not matching, it can result in differences 
                               in metrics displayed by Swarm and actual metrics used in the local model training."
                               metricFunction string should match with metric function class defined in 
                               torchmetrics - https://torchmetrics.readthedocs.io/en/stable/all-metrics.html
                               For example, to use CLASS torchmetrics.Accuracy() - metricFucntion value is "Accuracy"
        :param metricFunctionArgs: Dictionary with parameters (as keys) to be used in metricFunction.
                                   https://torchmetrics.readthedocs.io/en/stable/all-metrics.html
                                   For example, to use 
                                   CLASS torchmetrics.Accuracy(task: Literal['binary', 'multiclass', 'multilabel'], 
                                                               threshold: float= 0.5, 
                                                               num_classes: Optional[int] = None, 
                                                              ...)
                                    metricFunctionArgs is used to pass any mandatory parameters or 
                                    overwrite any default parameters defined in class. 
                                    While running mnist training which is a multi class with 10 classes application,
                                    dictionary should be created like below. 
                                    create dictionary -  mFArgsDict={}
                                                         mFArgsDict['task']="multiclass"
                                                         mFArgsDict['num_classes']=10
                                    pass it through SwarmCallback - 
                                    SwarmCallback(...
                                        metricFunction="Accuracy",
                                        metricFunctionArgs=mFArgsDict
                                     ...)

        '''
        SwarmCallbackBase.__init__(self, syncFrequency, minPeers, trainingContract, kwargs)        
        self._verifyAndSetPlatformContext(kwargs)
        self._swarmInitialize()
        
        # lossFunction and lossFunctionArgs requested through swarm callback should match with 
        # loss function class defined in pyTorch
        # https://pytorch.org/docs/stable/nn.html#loss-functions
        self.lossFunction = kwargs.get('lossFunction', None)
        self.lossFunctionArgs = kwargs.get('lossFunctionArgs', None)
        
        # metricFunction and metricFunctionArgs requested through swarm callback should match with 
        # metric function class defined in torchmetrics.
        # https://torchmetrics.readthedocs.io/en/stable/all-metrics.html
        self.metricFunction = kwargs.get('metricFunction', None)
        self.metricFunctionArgs = kwargs.get('metricFunctionArgs', None)
        
        if(self.valData == None):
            self.logger.info("=============================================================")
            self.logger.info("WARNING: valData is not available to compute Loss and metrics")
            self.logger.info("=============================================================")

    
    def on_train_begin(self):
        '''
        Pytorch specific on_train_begin implementation
        '''
        self._swarmOnTrainBegin()
    

    def on_batch_end(self, batch=None):
        '''
        Pytorch specific on_batch_end implementation
        '''
        self._swarmOnBatchEnd()


    def on_epoch_end(self, epoch=None):
        '''
        Pytorch specific on_epoch_end implementation
        '''
        self._swarmOnEpochEnd()

    
    def on_train_end(self):
        '''
        Pytorch specific on_train_end implementation
        '''
        self._swarmOnTrainEnd()


    def _verifyAndSetPlatformContext(self, params):
        '''
        Pytorch specific implementation of abstract method
        _verifyAndSetPlatform in SwarmCallbackBase class.
        It is the verification and initialization code specific 
        to Pytorch.
        '''
        ml_platform = params.get('ml_platform', SLPlatforms.PYTORCH.name)
        if ml_platform not in [SLPlatforms.PYTORCH.name]:
            self._logAndRaiseError("Invalid ml platform type: %s" % (ml_platform))
        self.mlPlatform = SLPlatforms[ml_platform]
        self.model = params.get('model', None)
        if self.model is None:
            self._logAndRaiseError("Pytorch model is None")
        else:
            self.__setMLContext(pytorchModel=self.model)


    def _getValidationDataForAdaptiveSync(self, valData, valBatchSize):
        '''
        Pytorch specific implementation of abstract method
        _getValidationDataForAdaptiveSync in SwarmCallbackBase class.
        '''
        valGen = validationSteps = valX = valY = valSampleWeight = None
        
        if(not valData):
            #valData is an optional parameter if not available, then performance data won't be supported
            return valGen, validationSteps, valX, valY, valSampleWeight
        
        # No need to unpack valData for pyTorch. 
        # pyTorch supports only DataLoader object as valData
        # expecting valdata of type "torch.utils.data.DataLoader"
        if(not isinstance(valData, torch.utils.data.DataLoader)):
            self._logAndRaiseError("adsValData type passed is %s, not matching with torch.utils.data.DataLoader" %(type(valData)))
        
        # Following return of all Nones is to be in consistency with other ML platforms
        # valData object will be unpacked during loss/metrics computations
        return valGen, validationSteps, valX, valY, valSampleWeight


    def _saveModelWeightsToDict(self):
        '''
        Pytorch specific implementation of abstract method
        _saveModelWeightsToDict in SwarmCallbackBase class.
        Saves the model passed to it inside its context, along with 
        the list of key weightNames of model's weights.
        This is later used in the loadModel function for loading the 
        updated set of weights as a flat dictionary
        '''
        inDict = {}
        self.weightNames = []
        model = self.mlCtx.model
        # in pytorch model weights are stored in a orderedDict 
        # hence we dont need to ensure ordering, it should work as is.
        for wTensor in model.state_dict():
            # Hoewever weights are Tensors , we have change it to numpy types
            # wTensor is a str so we can use it as is.
            if (model.state_dict()[wTensor].is_cuda):
                #TypeError: can't convert cuda:0 device type tensor to numpy. 
                #Use Tensor.cpu() to copy the tensor to host memory first.
                inDict[wTensor] = model.state_dict()[wTensor].cpu().numpy()
            else:
                inDict[wTensor] = model.state_dict()[wTensor].numpy()

            self.weightNames.append(wTensor)
        return inDict


    def _loadModelWeightsFromDict(self, inDict):
        '''
        Pytorch specific implementation of abstract method
        _loadModelWeightsFromDict in SwarmCallbackBase class.
        This function in tightly intertwined with saveModelWeightstoDict 
        function, updating the same model that was passed to the last call 
        of the save model function. Hence please use carefully
        :param inDict: The flat model weights' dictionary to be loaded in the model
        :return: Nothing is returned, the saved model is updated in-place
        '''
        # https://pytorch.org/tutorials/beginner/saving_loading_models.html
        # Partially loading a model or loading a partial model are common scenarios 
        # when transfer learning or training a new complex model. 
        # Leveraging trained parameters, even if only a few are usable, 
        # will help to warmstart the training process and hopefully help your model 
        # converge much faster than training from scratch.
        # Whether you are loading from a partial state_dict, which is missing some keys, 
        # or loading a state_dict with more keys than the model that you are loading into, 
        # you can set the strict argument to False in the load_state_dict() function 
        # to ignore non-matching keys.

        model = self.mlCtx.model
        tempDict = {}
        for k in self.weightNames:
            tempDict[k] = torch.Tensor(inDict[k])
        model.load_state_dict(tempDict, strict=False)


        # IMP NOTE: model.train() or mode.eval or model.no_grads() 
        # needs to be called by the caller, to ensure weights are 
        # useful otherwise dropout, BatchNormalization may not work
        # as expected.
        # https://stackoverflow.com/questions/52945427/pytorch-manually-setting-weight-parameters-with-numpy-array-for-gru-lstm
        # https://stackoverflow.com/questions/60018578/what-does-model-eval-do-in-pytorch
        # use model.training to check status


    def _calculateLocalLossAndMetrics(self):
        '''
        Pytorch specific implementation of abstract method
        _calculateLocalLossAndMetrics in SwarmCallbackBase class.
        '''
        valLoss = 0
        totalMetrics = 0
        
        if(self.valData == None):
            return valLoss, totalMetrics
        
        try: 
            # LOSS FUNCTION in pyTorch
            # requested lossFunction string should match with loss function class defined in pyTorch
            # https://pytorch.org/docs/stable/nn.html#loss-functions
            # Logic is to construct callable loss function using passed in lossFunction string. 
            lossModName = "torch.nn"
            lossFunctionClass = getattr(sys.modules[lossModName], self.lossFunction)
            # loss functions are defined as classes, so create object for lossfuntion
            # **self.lossFunctionArgs - is used for unpacking a dictionary and passing it as 
            # keyword arguments during the call
            lossFunctionObj = lossFunctionClass(**self.lossFunctionArgs)
            
            # METRICS FUNCTION in pyTorch
            # requested metricsFunction string should match with metric function class defined in torchmetrics
            # https://torchmetrics.readthedocs.io/en/stable/all-metrics.html
            # Logic is to construct callable metric function using passed in metricFunction string. 
            metricsModName = "torchmetrics"
            metricFunctionClass = getattr(sys.modules[metricsModName], self.metricFunction)
            # metric functions are defined as classes, so create object for metric funtion
            # **self.metricFunctionArgs - is used for unpacking a dictionary and passing it as 
            # keyword arguments during the call
            metricFunctionObj = metricFunctionClass(**self.metricFunctionArgs)


            testLoader = self.valData
            useCuda = torch.cuda.is_available()
            device = torch.device("cuda" if useCuda else "cpu")  
            # Update the model, mertic and loss also to device specific object
            metricFunctionObj = metricFunctionObj.to(device)
            lossFunctionObj = lossFunctionObj.to(device)
            model = self.mlCtx.model.to(device)
            model.eval()
            
            with torch.no_grad():
                for data, target in testLoader:
                    data, target = data.to(device), target.to(device)
                    output = model(data)
                    batchLoss = lossFunctionObj(output, target)
                    self.logger.debug("batch loss : ", batchLoss)
                    valLoss += batchLoss
                    
                    # metric on current batch
                    batchMetrics = metricFunctionObj.forward(output, target)
                    #If printing batch metrics is not needed, just replace metric.forward with metric.update(preds, target)
                    self.logger.debug(f"{self.metricFunction} on this batch : {batchMetrics}")
                    
            valLoss /= len(testLoader.dataset)
            self.logger.debug(f"\n Local Loss : {self.lossFunction} on ValData: {valLoss}")
            
            # metrics on all batches using custom accumulation
            totalMetrics = metricFunctionObj.compute()
            self.logger.debug(f" Local Metrics: {self.metricFunction} on valData : {totalMetrics} \n")
            # Resetting internal state such that metric is ready for new data
            metricFunctionObj.reset()
        
        except Exception as emsg:
            self._logAndRaiseError("Exception in method pyt.py:_calculateLocalLossAndMetrics, error message - %s"%(emsg))
        
        return valLoss, totalMetrics


    def __setMLContext(self, **params):
        ctx = SwarmCallback.pyTorchContext(params['pytorchModel'])
        self.logger.debug("Initialized PyTorch context for Swarm")
        self.mlCtx = ctx
