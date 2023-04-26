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
# This file contains the swarm variables and functionalities that
# are common to both TF and PYT. It contains the base callback
# class SwarmCallbackBase that all platform specific callback 
# classes have to be derived from
##################################################################

from __future__ import print_function

import sys
import os
import logging
from enum import IntEnum
from abc import ABC, abstractmethod
from swarmlearning.client.app2if import APP2IF as SwarmStub

######################################
##### Define all constants below #####
# IMPORTANT NOTES:
# Before making any change to this constants
# ensure that similar change has been done
# in server side SL code also, because, the
# same constants are also defined there
######################################
# Swarm or ML related constants
NUMBER_OF_NODES = 1
class CheckinModel(IntEnum):
    inactive = 1
    active = 2
    snapshot = 3
# ML Platforms supported in SL framwork 
class SLPlatforms(IntEnum):
    TF = 1
    KERAS = 2
    PYTORCH = 3

MAX_PEERS = 0


class SwarmError(Exception):
    pass


class SwarmCallbackBase(ABC):
    '''
    This is the base class for all platform specific callback
    classes. All common variables and functionalities that are
    required for Swarm are implemented in this base class.
    Any platform that wants to integrate with Swarm has to
    implement all the abstract classes and call swarm functions
    at different phases of training.
    '''

    @staticmethod
    def safeCastType(val, toType, valDefault=None):
        # For safely handling type conversion
        # Utility method
        try:
            return toType(val)
        except (ValueError, TypeError):
            return valDefault


    def __init__(self, syncFrequency, minPeers, trainingContract, params):
        '''
        Constructor for SwarmCallbackBase class
        '''
        self.logger = params.get("logger", None)
        if self.logger == None:
            self.logger = self.__createLogger()
        self.logger.info('SwarmCallbackBase logger is set')
        self.syncFrequency = self.__getSyncFrequency(syncFrequency)        
        self.currentSyncFrequency = self.stepsBeforeNextSync = self.syncFrequency
        self.minPeers = self.__getMinPeers(minPeers)
        self.trainingContract = self.__getTrainingContract(trainingContract)
        self.maxPeers = self.__getMaxPeers(MAX_PEERS, minPeers)
        self.checkinModelOnTrainEnd = self.__getCheckinModel(params)
        self.nodeWeightage = self.__getNodeWeightage(params)
        ( self.useAdaptiveSync, self.valData, self.valBatchSize, self.valGen, 
          self.validationSteps, self.valX, self.valY, self.valSampleWeight ) \
          = self.__getAdaptiveSyncParams(params)
        # Initialize other variables
        self.isSwarmTrainingOver = False
        self.lastSuccessfulMergeDictInActTrng = None
        self.userMergeDone = False
        # Print all params
        self.__prints()
        '''
        SWARM_LOOPBACK environment variable is used to bypass Swarm
        Learning to help users to quickly develop, integrate and test
        their model code with Swarm Learning package.
        If SWARM_LOOPBACK environment variable is set as True, then 
        all Swarm functionalities will be bypassed except parameter
        validation. This can help user to verify and test integration 
        of model code with Swarm without spawning any Swarm container.
        '''
        self.loopback = os.getenv('SWARM_LOOPBACK', 'False').lower() == 'true'
        self.logger.info("*"*52)
        self.logger.info(f'***** Is Swarm callback in loopback mode: {self.loopback} *****')
        self.logger.info("*"*52)


    def getLoss(self, mergedParamsDict):
        '''
        Loss calculation of current model using validation data.
        This should be called from SL or server side Blackboard 
        implementation. It is required for adaptive sync.
        '''
        ########################################################
        # Very important:
        # _loadModelWeightsFromDict and lastSuccessfulMergeDictInActTrng
        # must be called and updated for each loss calculation.
        # This has to be done eveytime irrespective of platform
        # specific actual local loss is calculated or not, because
        # this is the only way merge parameters by swarm gets updated 
        # in the local model.
        ########################################################
        self._loadModelWeightsFromDict(mergedParamsDict)
        self.lastSuccessfulMergeDictInActTrng = mergedParamsDict
        # Call platform specific loss calculation only if useAdaptiveSync
        # is true and stepsBeforeNextSync is 0. Otherwise just return 0
        localLoss = 0
        if self.useAdaptiveSync and self.stepsBeforeNextSync == 0:
            # Calculate local loss is not implemented for all platforms.
            # Platforms for which ADS is supported, this method should be available. 
            # Platform specific loss calculation
            localLoss = self._calculateLocalLoss()
            self.logger.info("Calculated local loss using merged parameters = {}".format(localLoss))
        return localLoss


    def _swarmInitialize(self):
        '''
        Create FIFO pipes and call SL to initialize the blackboard
        '''
        # If loopback just return
        if self.loopback:
            self.logger.debug("SwarmInitialize: Bypassing Swarm Learning functionality as SWARM_LOOPBACK is True")
            return
        self.logger.debug("="*20 + " swarmInitialize : START " + "="*20)
        try:
            self.swarmStub = SwarmStub(
                syncInterval=self.currentSyncFrequency
              , minPeers=self.minPeers
              , maxPeers=self.maxPeers
              , useAdaptiveSync=self.useAdaptiveSync
              , checkinModelOnTrainEnd=self.checkinModelOnTrainEnd.name
              , nodeWeightage=self.nodeWeightage
              , trainingContract=self.trainingContract
              , callbackLossFunc=self.getLoss
              , logger=self.logger
            )
        except Exception as exp:
            self._logAndRaiseError('Init Swarm call to SL container failed - ' + str(exp))
        self.logger.debug("="*20 + " swarmInitialize : END " + "="*20)


    def _swarmOnTrainBegin(self):
        '''
        Call SL to merge local params so that all models start from 
        same state. Should be called to execute swarm functionality 
        during begining of local training
        '''
        # If loopback just return
        if self.loopback:
            self.logger.debug("OnTrainBegin: Bypassing Swarm Learning functionality as SWARM_LOOPBACK is True")
            return
        self.logger.debug("="*20 + " swarmOnTrainBegin : START " + "="*20)
        self.__doSync()
        self.logger.debug("="*20 + " swarmOnTrainBegin : END " + "="*20)


    def _swarmOnBatchEnd(self):
        '''
        Call SL to periodically merge local params of all models. 
        Should be called to execute swarm functionality at the end
        of each batch of local training
        '''
        # If loopback just return
        if self.loopback:
            self.logger.debug("OnBatchEnd: Bypassing Swarm Learning functionality as SWARM_LOOPBACK is True")
            return
        if self.stepsBeforeNextSync == 0 and not self.isSwarmTrainingOver:
            self.logger.debug("="*20 + " swarmOnBatchEnd : START " + "="*20)            
            self.__doSync()
            self.userMergeDone = True
            self.logger.debug("="*20 + " swarmOnBatchEnd : END " + "="*20)
        self.stepsBeforeNextSync -= 1


    def _swarmOnEpochEnd(self):
        '''
        Currently not used by Swarm Learning. Should be called to 
        execute swarm functionality at the end of each epoch of 
        local training. But currently platform specific implementation 
        may choose not to call this.
        '''
        # If loopback just return
        if self.loopback:
            self.logger.debug("OnEpochEnd: Bypassing Swarm Learning functionality as SWARM_LOOPBACK is True")
            return
        self.logger.debug("="*20 + " swarmOnEpochEnd : START " + "="*20)
        # NO Swarm related functionality is implemented here for now
        # Space holder for future use
        self.logger.debug("="*20 + " swarmOnEpochEnd : END " + "="*20)


    def _swarmOnTrainEnd(self):
        '''
        Call SL to merge params at the end of local training. Should be 
        called to execute swarm functionality at the end of local training
        '''
        # If loopback just return
        if self.loopback:
            self.logger.debug("OnTrainEnd: Bypassing Swarm Learning functionality as SWARM_LOOPBACK is True")
            return
        self.logger.debug("="*20 + " swarmOnTrainEnd : START " + "="*20)
        self.logger.info("Finished local training !!!")
        if not self.userMergeDone:
            self.logger.warning( f'No user merge done during swarm training.' +
                                 f' syncFrequency={self.syncFrequency} may be high.')
        self.logger.info("Swarm training may continue till trainings in min peers are done!")
        self.logger.debug('Extracting model weights for final syncing at train end ...')
        lastLocalDict = self._saveModelWeightsToDict()
        lastMergedDict = self.lastSuccessfulMergeDictInActTrng
        lastMergedDict = lastLocalDict if lastMergedDict is None else lastMergedDict
        '''
        IMPORTANT: ***** Needs To Be Reviewed *****
        ================================
        For isSwarmTrainingOver == TRUE:
        ================================
        In normal condition when this node is part of min peers, then
        isSwarmTrainingOver would be false. 
        endSync() --> SL --> rendezvous() --> getLoss()
        This ensures that local model is periodically updated with merged
        model so at the end all nodes has same Swarm model
        ================================
        For isSwarmTrainingOver == FALSE:
        ================================
        This can happen only when this node is not part of min peers and
        min peers and swarm already finished their training when this 
        node was busy doing local training. So we need to finalize which
        model to load now for this node - lastLocalDict or lastMergedDict.
        But remember neither model would match with the actual swarm model
        because this node did not participate in the last swarm merge.
        Currently we are loading the last merged model keeping the behavior
        same as earlier swarm implementation.
        '''
        if not self.isSwarmTrainingOver:
            self.__endSync(lastLocalDict, lastMergedDict)
        else:
            msg = "Swarm training is over before local training. Exit gracefully."
            self.logger.warning( msg )
            self.logger.info( "Loading the last merged swarm model")
            self._loadModelWeightsFromDict(lastMergedDict)
            # We need to inform SL that user model is done, there wont
            # be any end sync call as blackboard would be in completed
            # state. Send a kill message to SL to shutdown gracefully
            self.logger.info('Informing SL to shutdown gracefully')
            try:
                self.swarmStub._sendKillMsgWithOK(msg)
            except Exception as exp:
                self.logger.warning('Failed to inform SL. Reason - ' + str(exp))

        self.logger.info( "All peers and Swarm training rounds finished."
                        + " Final Swarm model was loaded.")
        self.logger.debug("="*20 + " swarmOnTrainEnd : END " + "="*20)


    def _logAndRaiseError(self, message):
        '''
        Log error and raise swarm exception
        '''
        self.logger.error(message)
        raise SwarmError(message)


    @abstractmethod
    def _verifyAndSetPlatformContext(self, params):
        '''
        Individual training platform has to implement this
        '''
        pass


    @abstractmethod
    def _getValidationDataForAdaptiveSync(self, valData, valBatchSize):
        '''
        Individual training platform has to implement this
        '''
        pass


    @abstractmethod
    def _saveModelWeightsToDict(self):
        '''
        Individual training platform has to implement this
        '''
        pass


    @abstractmethod
    def _loadModelWeightsFromDict(self, paramsDict):
        '''
        Individual training platform has to implement this
        '''
        pass


    @abstractmethod
    def _calculateLocalLoss(self):
        '''
        Individual training platform has to implement this
        '''
        pass


    def __createLogger(self):
        '''        
        ### Create and setup swarm callback logger ###
        '''
        logger = logging.getLogger('SwarmCallback')
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
        logger.setLevel(logging.INFO)
        # Add stream handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.flush = sys.stdout.flush
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        # Add file handler
        ### Commenting the code to write file log ###
        # Will uncomment only when we decide where to 
        # create the log file in user container
        '''
        logFile = 'swarm_callback.log'
        os.remove(logFile) if os.path.exists(logFile) else None
        file_handler = logging.FileHandler(logFile)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        '''
        return logger


    def __getSyncFrequency(self, syncFrequency):
        scbSyncFrequency = SwarmCallbackBase.safeCastType(syncFrequency, int)
        if scbSyncFrequency is None or scbSyncFrequency <= 0:
            self._logAndRaiseError("syncFrequency has to be a positive integer")
        return scbSyncFrequency


    def __getMinPeers(self, minPeers):
        scbMinPeers = SwarmCallbackBase.safeCastType(minPeers, int)
        if scbMinPeers is None or scbMinPeers <= 0:
            self._logAndRaiseError("minPeers have to be a positive integer")
        return scbMinPeers

    def __getTrainingContract(self, trainingContract):
        if trainingContract is None:
            self._logAndRaiseError("Invalid Training Contract")
        return trainingContract


    def __getMaxPeers(self, maxPeers, minPeers):
        scbMaxPeers = SwarmCallbackBase.safeCastType(maxPeers, int)
        if scbMaxPeers > 0 and scbMaxPeers <= minPeers:
            self._logAndRaiseError("Invalid maxPeers value, should be ZERO \
                                   or greater than minPeers")
        return scbMaxPeers


    def __getCheckinModel(self, params):
        scbCheckinModel = params.get('checkinModelOnTrainEnd', 
                                    CheckinModel.snapshot.name)
        if scbCheckinModel not in [member.name for member in CheckinModel]:
            self._logAndRaiseError("Invalid value checkinModelOnTrainEnd: " +
                                   str(scbCheckinModel)
                                   + ". Allowed values: "
                                   + str([member.name for member in CheckinModel])
                                   )
        return CheckinModel[scbCheckinModel]


    def __getNodeWeightage(self, params):
        nodeWeightage = params.get('nodeWeightage', 1)
        scbNodeWeightage = SwarmCallbackBase.safeCastType(nodeWeightage, int)
        if scbNodeWeightage is None or scbNodeWeightage <= 0 or scbNodeWeightage > 100:
            self._logAndRaiseError("Node weightage should be a number between 1-100. \
                                       Provided value: " + str(nodeWeightage))
        return scbNodeWeightage


    def __getAdaptiveSyncParams(self, params):
        useAdaptiveSync = params.get('useAdaptiveSync', False)
        valData = params.get('adsValData', None)
        valBatchSize = params.get('adsValBatchSize', 0)
        valGen = validationSteps = valX = valY = valSampleWeight = None
        if useAdaptiveSync:
            if valData == None or valBatchSize <= 0:
                self._logAndRaiseError(
                    "For adaptive sync, valid adsValData and " +
                    "valid adsValBatchSize (a positive integer) are mandatory"
                    )
            ( valGen, validationSteps, valX, valY, valSampleWeight ) \
            = self._getValidationDataForAdaptiveSync(valData, valBatchSize)
        return useAdaptiveSync, valData, valBatchSize, valGen, \
            validationSteps, valX, valY, valSampleWeight


    # Log print
    def __prints(self) :
        self.logger.info("***Swarm Callback Params: Inside SwarmCallbackBase at user side***")
        self.logger.info("syncFrequency: %d" % self.syncFrequency)
        self.logger.info("minPeers: %d" % self.minPeers)
        self.logger.info("trainingContract: %s" % self.trainingContract)
        self.logger.info("maxPeers: %d" % self.maxPeers)
        self.logger.info("valBatchSize: %d" % self.valBatchSize)
        self.logger.info("useAdaptiveSync: %s" % self.useAdaptiveSync)
        self.logger.info("checkinModelOnTrainEnd: %s" % self.checkinModelOnTrainEnd)
        self.logger.info("nodeWeightage: %d" % self.nodeWeightage)
        self.logger.info("="*30)


    def __doSync(self):
        self.logger.debug('Extracting model weights for syncing ...')
        localParamsDict = self._saveModelWeightsToDict()
        self.logger.info("Starting Swarm merging round ...")
        # We pass numNodes (1 for leaf clique, #nodes in clique for non-leaf clique) 
        # as arg to rendezvous function. This is packed as part of the weights 
        # dictionary by SwarmBlackBoard. We don't pack the value here itself as the 
        # extraction needs to happen at SwarmBlackBoard end; hence, it is good to let
        # the same file decide how to pack this value. Note that, the mergedDict will 
        # just be having the weights and no additional keys will be present in it that 
        # may have been added by Swarmblackboard.
        try:
            self.stepsBeforeNextSync, self.isSwarmTrainingOver = \
                self.swarmStub._sync(
                    localParamsDict
                  , self.nodeWeightage
                  , NUMBER_OF_NODES
                  )
        except Exception as exp:
            self._logAndRaiseError('Sync Swarm call to SL container failed - ' + str(exp))
        self.logger.info("Merge Done: RVInt [cur: %s Nxt: %s]"%
                                        (self.currentSyncFrequency, 
                                        self.stepsBeforeNextSync))
        self.currentSyncFrequency = self.stepsBeforeNextSync


    def __endSync(self, lastLocalDict, lastMergedDict):        
        # Default: Use latest model weights lastLocalDict for snapshot
        dictToSync = lastLocalDict
        # Use merged weights for active
        if self.checkinModelOnTrainEnd == CheckinModel.active:
            dictToSync = lastMergedDict
        # Node weightage is 0 for inactive. So don't bother for dictToSync value
        elif self.checkinModelOnTrainEnd == CheckinModel.inactive:
            self.nodeWeightage = 0
        self.logger.info( "Final merging starts at training end. Waiting for other peers"
                        + " to complete ...")
        # We pass numNodes (1 for leaf clique, #nodes in clique for non-leaf clique) 
        # as arg to rendezvous function. This is packed as part of the weights 
        # dictionary by SwarmBlackBoard. We don't pack the value here itself as the 
        # extraction needs to happen at SwarmBlackBoard end; hence, it is good to let
        # the same file decide how to pack this value. Note that, the mergedDict will 
        # just be having the weights and no additional keys will be present in it that 
        # may have been added by Swarmblackboard.
        try:
            self.stepsBeforeNextSync, self.isSwarmTrainingOver = \
                self.swarmStub._closeSession(
                    dictToSync
                  , self.nodeWeightage
                  , NUMBER_OF_NODES
                  )
        except Exception as exp:
            self._logAndRaiseError('End Swarm call to SL container failed - ' + str(exp))
