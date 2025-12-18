#######################################################################
## (C)Copyright 2025 Hewlett Packard Enterprise Development LP
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
# This file is the main entry point for Swarm Learning for Hugging Face Transformers.
# Users can integrate Swarm framework into their model code by creating an 
# instance of the SwarmCallback class and calling its methods at different phases of training.
##################################################################

from transformers import TrainerCallback
from swarmlearning.client.swarm import SwarmCallbackBase, SLPlatforms
import torch
from peft import get_peft_model_state_dict

# Default Training contract used for learning if not specified by user. 
# Any update to default contract needs similar modifications 
# in all applicable ML platforms (TF, PYT, HF etc)
DEFAULT_TRAINING_CONTRACT = 'defaultbb.cqdb.sml.hpe'

class SwarmCallback(SwarmCallbackBase, TrainerCallback):
    '''
    This is the customized callback class sub-classed from 
    SwarmCallbackBase class and TrainerCallback. It implements 
    different swarm functionalities for Hugging Face Transformers trainer class.
    '''

    class HuggingFaceContext:
        def __init__(self, model):
            self.model = model

    def __init__(self, syncFrequency, minPeers, trainingContract=DEFAULT_TRAINING_CONTRACT, **kwargs):
        '''
        Initializes the Swarm learning parameters and Hugging Face context.
        : param hfMode: Huggingface model type, either "full" or "peft"
                        For example, to use full model, pass hfMode="full"
                        For example, to use peft model, pass hfMode="peft"
                        This is expected to be used only in Huggingface Transformers use case.
                        For other use cases, this parameter is set to None and ignored.
                        By default, it is set to "full" for Hugging Face Transformers.
        '''
        TrainerCallback.__init__(self)
        SwarmCallbackBase.__init__(self, syncFrequency, minPeers, trainingContract, kwargs)
        self._verifyAndSetPlatformContext(kwargs)
        self._swarmInitialize()
        
        # TODO: Check if its applicable and fix it.
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

    # https://huggingface.co/transformers/v3.4.0/main_classes/callback.html#transformers.TrainerCallback
    # control (TrainerControl) – The object that is returned to the Trainer and can be used to make some decisions.
    def on_train_begin(self, args, state, control, **kwargs):
        '''
        Hugging Face specific on_train_begin implementation.
        '''
        self.logger.info("=============================================================")
        self.logger.info("HF-Swarm: Training starts")
        self.logger.info("=============================================================")
        self._swarmOnTrainBegin()
        # return control

    def on_step_end(self, args, state, control, **kwargs):
        self.logger.debug(f"HF-Swarm Step End - Step: {state.global_step}, Epoch: {state.epoch}")
        self._swarmOnBatchEnd()
        # return control

    def on_epoch_end(self, args, state, control, **kwargs):
        '''
        Hugging Face specific on_epoch_end implementation.
        Syncs model weights at the end of each epoch.
        '''
        self.logger.info(f"HF-Swarm Epoch End - Step: {state.global_step}, Epoch: {state.epoch}")
        self._swarmOnEpochEnd()
        # return control
        
    def on_train_end(self, args, state, control, **kwargs):
        '''
        Hugging Face specific on_train_end implementation.
        Finalizes Swarm Learning after training.
        '''
        self.logger.info(f"HF-Swarm Train End - Step: {state.global_step}, Epoch: {state.epoch}")
        self._swarmOnTrainEnd()
        # return control

    def _verifyAndSetPlatformContext(self, params):
        '''
        Hugging Face specific platform context initialization.
        '''
        ml_platform = params.get('ml_platform', SLPlatforms.HF_TRANSFORMER.name)
        if ml_platform not in [SLPlatforms.HF_TRANSFORMER.name]:
            self._logAndRaiseError("Invalid ML platform type: %s" % ml_platform)
        self.mlPlatform = SLPlatforms[ml_platform]
        if 'hfMode' in params:
            hfMode = params['hfMode']
            if hfMode not in ['full', 'peft']:
                self._logAndRaiseError("Invalid Hugging Face model type: %s" % hfMode)
            self.hfMode = hfMode
        else:
            self.hfMode = 'full'
        self.model = params.get('model', None)
        if self.model is None:
            self._logAndRaiseError("Hugging Face model is None")
        else:
            self.__setMLContext(model=self.model)
    
    # TODO: make AdaptiveSync work.
    def _getValidationDataForAdaptiveSync(self, valData, valBatchSize):
        '''
        Hugging Face specific implementation of abstract method
        _getValidationDataForAdaptiveSync in SwarmCallbackBase class.
        '''
        valGen = validationSteps = valX = valY = valSampleWeight = None
        
        if(not valData):
            #valData is an optional parameter if not available, then performance data won't be supported
            return valGen, validationSteps, valX, valY, valSampleWeight
        
     
    def _saveModelWeightsToDict(self):
        '''
        Hugging Face specific implementation of saving model weights to a dictionary.
        '''

        ## 2nd Approach
        inDict = {}
        self.weightNames = []
        model = self.mlCtx.model
        
        if self.hfMode == 'peft':
            # get_peft_model_state_dict returns a dict of adapter weights (e.g., LoRA)
            lora_weights = get_peft_model_state_dict(model)
            for k, v in lora_weights.items():
                if hasattr(v, "is_cuda") and v.is_cuda:
                    inDict[k] = v.cpu().numpy()
                else:
                    inDict[k] = v.numpy()
                self.weightNames.append(k)
            self.logger.info(f"HF-PEFT-Swarm: Saved model weights to dictionary with keys: {self.weightNames} and values: {list(inDict.values())}  ")
        else:
            # Underlying implementation for Transformers library is PyTorch, in pytorch model weights are stored in a orderedDict 
            # hence we dont need to ensure ordering, it should work as is.
            for wTensor in model.state_dict():
                # Hoewever weights are Tensors , we have change it to numpy types
                # wTensor is a str so we can use it as is.
                if (model.state_dict()[wTensor].is_cuda):
                    inDict[wTensor] = model.state_dict()[wTensor].cpu().numpy()
                else:
                    inDict[wTensor] = model.state_dict()[wTensor].numpy()

                self.weightNames.append(wTensor)
        return inDict


    def _loadModelWeightsFromDict(self, inDict):
        '''
        Hugging Face specific implementation of loading model weights from a dictionary.
        '''
        # # Load the new weights into the model
        # model.load_state_dict(new_state_dict, strict=False)
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

    # TODO: Implement this logic for HF
    def _calculateLocalLossAndMetrics(self):
        '''
        Hugging Face specific implementation of calculating local loss and metrics.
        '''
        valLoss = 0
        totalMetrics = 0
        model = self.mlCtx.model

        if self.valData is None:
            return valLoss, totalMetrics

        # Logic for computing loss and metrics similar to the one used in pyt.py
        # Adjustments will be made based on HuggingFace's methods and structures.

        return valLoss, totalMetrics

    def __setMLContext(self, **params):
        ctx = SwarmCallback.HuggingFaceContext(params['model'])
        self.logger.info("Initialized HuggingFace context for Swarm")
        self.mlCtx = ctx
