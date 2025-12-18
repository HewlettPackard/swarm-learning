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
# This file is the main entry point for Swarm Learning for TF and 
# Keras platforms. Users can integrate Swarm framework into their 
# model code by creating an instance of the SwarmCallback class and 
# supplying it as a callback.
##################################################################

from __future__ import print_function
from tensorflow.keras.callbacks import Callback
from swarmlearning.client.swarm import SwarmCallbackBase, SLPlatforms

# Default Training contract used for learning if not specified by user. 
# Any update to default contract needs similar modifications 
# in all applicable ML platforms (TF, PYT, etc)
DEFAULT_TRAINING_CONTRACT = 'defaultbb.cqdb.sml.hpe'

class SwarmCallback(Callback, SwarmCallbackBase):
    '''
    This is the customized callback class sub-classed from Keras
    callback. It is also derived from SwarmCallbackBase class
    that implements different swarm functionalities. It overrides 
    keras callback methods like on_train_begin, on_batch_end etc 
    and calls different methods of SwarmCallbackBase
    '''

    # Tensorflow context
    class _TfContext:
        def __init__(self, tf, session):
            self.tf = tf
            self.tfSession = session
            self.assignHooks = self.createSwarmLearningHooksForParamters()

        def createSwarmLearningHooksForParamters(self):
            assignHooks = {}
            coll = self.tf.get_collection(self.tf.GraphKeys.TRAINABLE_VARIABLES)
            for v in coll:
                ph = self.tf.placeholder(v.dtype, v.shape)
                assign = self.tf.assign(v, ph)
                assignHooks[v.name] = (assign, ph)
            return assignHooks


    # Keras context
    class _KerasContext:
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
        :param mlPlatform: 'TF' or 'KERAS' ML Platform
        :param tf: Tensorflow context
        :param sess: Session context
        :param logger: Basic Python logger. SwarmCallback class will invoke info, 
                       debug and error methods of this logger to fulfil its need.
                       If no logger is passed, then SwarmCallback class will create 
                       its own logger from basic python logger. If required, user 
                       can get hold of this logger instance to change the log level 
                       as follows -
                       import logging
                       from swarmlearning.tf import SwarmCallback                       
                       swCallback = SwarmCallback(syncFrequency=128, minPeers=3)
                       swCallback.logger.setLevel(logging.DEBUG)
        :param totalEpochs: Total epochs used in local training. 
                            This is needed to display training progress or ETA of training.
                            WARNING: "With out this, training progress display might have some limitations."
        :param hfMode: Huggingface model type, either "full" or "peft"
                       For example, to use full model, pass hfMode="full"
                       For example, to use peft model, pass hfMode="peft"
                       This is expected to be used only in Huggingface Transformers use case.
                       For other use cases, this parameter is set to None and ignored.

        '''
        Callback.__init__(self)
        SwarmCallbackBase.__init__(self, syncFrequency, minPeers, trainingContract, kwargs)        
        self._verifyAndSetPlatformContext(kwargs)
        self._swarmInitialize()
        if(self.valData == None):
            self.logger.info("=============================================================")
            self.logger.info("WARNING: adsValData and adsValBatchSize are not available ")
            self.logger.info("to compute Loss and metrics")
            self.logger.info("=============================================================")

    
    def on_train_begin(self, logs=None):
        '''
        Overridden method on_train_begin of Keras Callback.
        '''
        if self.mlPlatform is SLPlatforms.KERAS:
            self.__setMLContext(kerasModel=self.model)
        self._swarmOnTrainBegin()
        if self.mlPlatform == SLPlatforms.KERAS and self.isSwarmTrainingOver:
            if not self.mlCtx.model.stop_training:
                self.logger.info('Swarm training is over. Stopping local training')
                self.mlCtx.model.stop_training = True
    

    def on_batch_end(self, batch, logs=None):
        '''
        Overridden method on_batch_end of Keras Callback.
        '''
        self._swarmOnBatchEnd()
        if self.mlPlatform == SLPlatforms.KERAS and self.isSwarmTrainingOver:
            if not self.mlCtx.model.stop_training:
                self.logger.info('Swarm training is over. Stopping local training')
                self.mlCtx.model.stop_training = True

    def on_epoch_end(self, epoch=None, logs=None):
        '''
        Overridden method on_epoch_end of Keras Callback.
        '''
        self._swarmOnEpochEnd()


    def on_train_end(self, logs=None):
        '''
        Overridden method on_train_end of Keras Callback.
        '''
        self._swarmOnTrainEnd()


    def _verifyAndSetPlatformContext(self, params):
        '''
        TF and Keras specific implementation of abstract method
        _verifyAndSetPlatformContext in SwarmCallbackBase class.
        It is the verification and initialization code specific 
        to TF / Keras.
        '''
        ml_platform = params.get('ml_platform', SLPlatforms.KERAS.name)
        if ml_platform not in [SLPlatforms.KERAS.name, SLPlatforms.TF.name]:
            self._logAndRaiseError("Invalid ml platform type: %s" % (ml_platform))
        self.mlPlatform = SLPlatforms[ml_platform]
        # This check is only for TF as keras model comes during on_train_begin
        if self.mlPlatform is SLPlatforms.TF:
            self.tf = params.get('tf', None)
            self.sess = params.get('sess', None)
            if self.tf is None or self.sess is None:
                self._logAndRaiseError("tf and sess params are must for Tensorflow platform")
            else:
                self.__setMLContext(tfobj=self.tf, tfsess=self.sess)
        # For TF and Keras, hfMode is not applicable, so set it to None
        self.hfMode = None
        if 'hfMode' in params:
            self.logger.info("hfMode is set to None, as this is TF/Keras platform")
            


    def _getValidationDataForAdaptiveSync(self, valData, valBatchSize):

        valGen = validationSteps = valX = valY = valSampleWeight = None
        self.logger.info("Allow valData for evaluation")
        self.logger.info("val data type is %s" %(type(valData)))
        if(valBatchSize is not None):
            self.logger.info("valBatchSize is %s" %(valBatchSize))
        return valGen, validationSteps, valX, valY, valSampleWeight


    def _saveModelWeightsToDict(self):
        '''
        TF and Keras specific implementation of abstract method
        _saveModelWeightsToDict in SwarmCallbackBase class.
        Saves the model passed to it inside its context, along with 
        the list of key weightNames of model's weights.
        This is later used in the loadModel function for loading the 
        updated set of weights.
        :return: The weights as a flat dictionary
        '''
        paramsDict = {}
        self.weightNames = []
        if self.mlPlatform == SLPlatforms.KERAS:
            model = self.mlCtx.model
            self.weightNames = [weight.name for layer in model.layers for weight in layer.weights]
            weights = model.get_weights()
            # the self.weightNames are weights are organized in the same way as the dataflow graph.
            # Hence, its safe to assume we will get a 1-1 match.
            assert (len(self.weightNames) == len(weights))
            paramsDict = dict(zip(self.weightNames, weights))
        elif self.mlPlatform == SLPlatforms.TF:
            tf = self.mlCtx.tf
            sess = self.mlCtx.tfSession
            coll = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            for v in coll:
                paramsDict[v.name] = sess.run(v)
                self.weightNames.append(v.name)
        return paramsDict
    
    def _loadModelWeightsFromDict(self, paramsDict):
        '''
        TF and Keras specific implementation of abstract method
        _loadModelWeightsFromDict in SwarmCallbackBase class.
        This function in tightly intertwined with saveModelWeightstoDict 
        function, updating the same model that was passed to the last call 
        of the save model function. Hence use carefully
        :param paramsDict: The flat model weights' dictionary to be loaded in the model
        :return: Nothing is returned, the saved model is updated in-place
        '''
        if self.mlPlatform == SLPlatforms.KERAS:
            # Assign the merged data to local tensorflow graph
            assignOpList = []
            for key in self.weightNames:
                assignOpList.append(paramsDict[key])
            self.mlCtx.model.set_weights(assignOpList)
        elif self.mlPlatform == SLPlatforms.TF:
            sess = self.mlCtx.tfSession
            assignHooks = self.mlCtx.assignHooks
            assignOpList = []
            feedDict = {}
            for key in self.weightNames:
                # Each assignHook contains an assignOperation (tf.assign) and 
                # the placeholder pointer for that operation (ph)
                # The key for each assignHook is a trainable variable name
                assignOp, placeholder = assignHooks[key]
                assignOpList.append(assignOp)
                # Get the new value for input placeholder for weight update 
                # from the key
                feedDict[placeholder] = paramsDict[key]
            sess.run(assignOpList, feed_dict=feedDict)
            self.logger.debug('Executed Tensorflow Trainable variable Assignments')


    def _calculateLocalLossAndMetrics(self):
        '''
        TF and Keras specific implementation of abstract method
        _calculateLocalLoss in SwarmCallbackBase class.
        Calculating local loss is completely platform dependent
        so it has to be implemented for specific platform type.
        Currently loss is used only to adjust sync frequency if 
        useAdaptiveSync is enabled and is calculated only for 
        keras platform.
        '''
        valLoss = 0
        totalMetrics = 0
        scores = None
        if(self.valData == None):
            return valLoss, totalMetrics
        
        #Refer - https://www.tensorflow.org/api_docs/python/tf/keras/Model
        if self.mlPlatform == SLPlatforms.KERAS:
            # If the valData is tuple it should be arranged in 
            #  (inputs, targets) or (inputs, targets, sample_weights).
            # If valData length is not 2 or 3, means valData might be 
            # tf.Dataset or Generator so use it as is in evaluate call.
            if(len(self.valData) == 2):
                self.logger.debug("valData has 2 args")
                valX, valY = self.valData
                scores = self.mlCtx.model.evaluate( x=valX,
                                                    y=valY, 
                                                    batch_size=self.valBatchSize)
            elif (len(self.valData) == 3):
                self.logger.debug("valData has 3 arg")
                valX, valY, valSampleWeight = self.valData
                scores = self.mlCtx.model.evaluate( x=valX,
                                                    y=valY, 
                                                    sample_weight = valSampleWeight,
                                                    batch_size=self.valBatchSize)
            else:
                self.logger.debug("valData has 1 arg")
                scores = self.mlCtx.model.evaluate( self.valData, 
                                                    batch_size=self.valBatchSize)

            # The first element in the scores list is loss, second element is metrics
            self.logger.debug("\n loss, metrics are :{}".format(scores))
            if scores:
                valLoss = scores[0]
                totalMetrics = scores[1]
        elif self.mlPlatform == SLPlatforms.TF:
            # TODO: To be implemented later
            valLoss = 0
            totalMetrics = 0
        return valLoss, totalMetrics


    def __setMLContext(self, **params):
        if SLPlatforms.TF is self.mlPlatform:
            ctx = SwarmCallback._TfContext(params['tfobj'], params['tfsess'])
            self.mlCtx = ctx
            self.logger.debug("Initialized TF context for Swarm")
        else:
            ctx = SwarmCallback._KerasContext(params['kerasModel'])
            self.logger.debug("Initialized Keras context for Swarm")
            self.mlCtx = ctx
