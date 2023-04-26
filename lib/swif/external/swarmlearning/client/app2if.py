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



# System imports.
from pathlib import Path
from typing import Callable, Dict, List

import logging
import numpy as np
import os
import stat
import time
import traceback

# Our imports.
from swarmlearning.com.bridge import Bridge, MessageBody

import swarmlearning.com.swifrpc_pb2 as spb
import swarmlearning.com.util as slutil


class APP2IF:
    def __init__(
        self
      , *args
      , syncInterval: int
      , minPeers: int
      , maxPeers: int
      , useAdaptiveSync: bool
      , checkinModelOnTrainEnd: str
      , nodeWeightage: int
      , trainingContract: str
      , callbackLossFunc: Callable
      , logger: logging.Logger
      , **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.__callbackLossFunc = callbackLossFunc
        self.__logger = logger
        self.__sequenceCounters = {"Sync": 0, "Close": 0}
        self.__bridge = Bridge(isSL=False)
        self.__bridge._openBridgeLanes(northBoundMode="rb", southBoundMode="wb")

        self.__openSession(
            syncInterval
          , minPeers
          , maxPeers
          , useAdaptiveSync
          , checkinModelOnTrainEnd
          , nodeWeightage
          , trainingContract
        )

        return

    def _sync( self
             , params: Dict[str, np.ndarray]
             , nodeWeightage: int
             , numberOfNodes: int
    ) -> (int, bool):
        return self.__sendParams(
            spb.MessageType.MsgTypeSyncRequest
          , spb.MessageType.MsgTypeSyncResponse
          , params
          , nodeWeightage
          , numberOfNodes
          , ["Sync"]
        )

    def _closeSession( self
                     , params: Dict[str, np.ndarray]
                     , nodeWeightage: int
                     , numberOfNodes: int
    ) -> (int, bool):
        return self.__sendParams(
            spb.MessageType.MsgTypeCloseSessionRequest
          , spb.MessageType.MsgTypeCloseSessionResponse
          , params
          , nodeWeightage
          , numberOfNodes
          , ["Close"]
        )

    def _sendKillMsgWithOK(self, msg):
        reqType = spb.MessageType.MsgTypeKillSessionRequest
        reason = spb.Status(code=spb.Status.StatusOK, msg=msg)
        killReq = spb.KillSessionRequest(
            sessionID=self.__sessionID
          , reason=reason
          )
        self.__bridge._send(Bridge.LaneDirection.SouthBound, reqType, killReq)
        
    def __openSession(
        self
      , syncInterval: int
      , minPeers: int
      , maxPeers: int
      , useAdaptiveSync: bool
      , checkinModelOnTrainEnd: str
      , nodeWeightage: int
      , trainingContract: str
    ) -> None:
        sessionReq = spb.SessionRequest(
            syncInterval=syncInterval
          , minPeers=minPeers
          , maxPeers=maxPeers
          , useAdaptiveSync=useAdaptiveSync
          , checkinModelOnTrainEnd=checkinModelOnTrainEnd
          , nodeWeightage=nodeWeightage
          , trainingContract=trainingContract
        )

        _, sessionResp = self.__sendRecv(
            spb.MessageType.MsgTypeOpenSessionRequest, sessionReq
        )

        # Handle error response. Can be of 2 types - error during 
        # execution of core swarm function or out of bound error
        # due to network etc.
        # Functional error comes as part of SessionResponse with 
        # error status while out of bound error comes as part new
        # Status message
        if not isinstance(sessionResp, spb.SessionResponse):
            if ( isinstance(sessionResp, spb.Status) 
            and  sessionResp.code != spb.Status.StatusOK ):
                raise RuntimeError('SL error: ' + sessionResp.msg)
            else:
                raise RuntimeError("{}: bad response: wanted {}, got {}".format(
                    "open-session", "SessionResponse", type(sessionResp)
            ))
        if sessionResp.status.code != spb.Status.StatusOK:
            raise RuntimeError('SL error: ' + sessionResp.status.msg)

        # Swarm call was successful
        self.__sessionID = sessionResp.sessionID

        return

    def __sendParams(
        self
      , requestType: spb.MessageType
      , responseType: spb.MessageType
      , params: Dict[str, np.ndarray]
      , nodeWeightage: int
      , numberOfNodes: int
      , sequenceNames: List[str]
    ) -> (int, bool):
        for seq in sequenceNames:
            self.__sequenceCounters[seq] += 1

        # Produces strings like "[Sync-13]" and "[Close-17][Loss-73]". Used in
        # log messages.
        counter = "".join(
            [f"[{seq}-{self.__sequenceCounters[seq]}]" for seq in sequenceNames]
        )

        paramWeights = slutil.toWeights(params)
        syncReq = spb.SyncRequest(
            sessionID=self.__sessionID
            # See if we can do better here. Currently, we need the field names
            # in a fixed order.
          , syncSeqNum=self.__sequenceCounters[sequenceNames[0]]
          , nodeWeightage=nodeWeightage
          , numberOfNodes=numberOfNodes
          , inputParams=paramWeights
        )

        _, resp = self.__sendRecv(requestType, syncReq)

        # Handling loss request
        while isinstance(resp, spb.LossRequest):
            lossReq = resp
            try:
                loss = self.__computeLoss(lossReq, syncReq, sequenceNames, counter)
                status = spb.Status(code=spb.Status.StatusOK, msg="StatusOK")
                lossResp = spb.LossResponse(
                    sessionID=lossReq.sessionID
                  , syncSeqNum=lossReq.syncSeqNum
                  , lossSeqNum=lossReq.lossSeqNum
                  , status=status
                  , loss=loss
                  )
                  # Send response and wait again to recv
                _, resp = self.__sendRecv(
                    spb.MessageType.MsgTypeGetLossResponse
                  , lossResp
                )
            except Exception as e:
                loss = -1 # Just a initialization. Would not be used
                errMsg = "Loss computation failed. " + str(e)
                print(errMsg)
                status = spb.Status(code=spb.Status.ErrorInUser, msg=errMsg)
                lossResp = spb.LossResponse(
                    sessionID=lossReq.sessionID
                  , syncSeqNum=lossReq.syncSeqNum
                  , lossSeqNum=lossReq.lossSeqNum
                  , status=status
                  , loss=loss
                  )
                # Send error response and raise exception to exit
                try:
                    self.__bridge._send(
                        Bridge.LaneDirection.SouthBound
                      , spb.MessageType.MsgTypeGetLossResponse
                      , lossResp
                      )
                except Exception as eignore:
                    # Suppress the context i.e. "during handling another exception"
                    # Details - https://stackoverflow.com/questions/24752395/python-raise-from-usage
                    raise e from None
                else:
                    raise

        # Handling final response of sync message

        # Handle error response. Can be of 2 types - error during 
        # execution of core swarm function or out of bound error
        # due to network etc.
        # Functional error comes as part of SyncResponse with 
        # error status while out of bound error comes as part new
        # Status message
        if not isinstance(resp, spb.SyncResponse):
            if( isinstance(resp, spb.Status) 
            and  resp.code != spb.Status.StatusOK ):
                raise RuntimeError('SL error: ' + resp.msg)
            else:
                raise RuntimeError("{}: bad response: wanted {}, got {}".format(
                    counter, "SyncResponse", type(resp)))

        if resp.status.code != spb.Status.StatusOK:
            raise RuntimeError('SL error: ' + resp.status.msg)

        if resp.syncSeqNum != syncReq.syncSeqNum:
            raise RuntimeError("{}: bad sync seq num: wanted {}, got {}".format(
                counter, syncReq.syncSeqNum, resp.syncSeqNum
            ))
        
        # Swarm sync call was successful
        return resp.nextSyncInterval, resp.trainingOver

    def __computeLoss(
        self
      , lossReq: spb.LossRequest
      , syncReq: spb.SyncRequest
      , sequenceNames: List[str]
      , counter: str
    ) -> float:
        if lossReq.sessionID != syncReq.sessionID:
            raise RuntimeError(
                "{}: get-loss: bad session ID: wanted {}, got {}".format(
                    counter, syncReq.sessionID, lossReq.sessionID
                )
            )

        if lossReq.syncSeqNum != syncReq.syncSeqNum:
            raise RuntimeError(
                "{}: get-loss: bad sync seq num: wanted {}, got {}".format(
                    counter, syncReq.syncSeqNum, lossReq.syncSeqNum
                )
            )

        mergedParams = slutil.fromWeights(lossReq.mergedParams)
        loss = self.__callbackLossFunc(mergedParams)
        # self.__log(f"{counter} Loss = {loss}")

        return loss

    def __sendRecv(
        self, msgType: spb.MessageType, msgBody: MessageBody
    ) -> (spb.MessageType, MessageBody):
        return self.__bridge._sendRecv(
            Bridge.LaneDirection.SouthBound
          , Bridge.LaneDirection.NorthBound
          , msgType
          , msgBody
        )

    def __printEx(
        self, be: BaseException, *, counter=None, reraise=True
    ) -> None:
        self.__log(
            "{} Caught exception: {}".format(
                counter if counter is not None else "UNCOUNTED", be
            )
          , level="error"
        )
        traceback.print_exception(type(be), be, be.__traceback__)

        if reraise == True:
            raise be

        return

    def __log(
        self, *args, flush: bool = True, useLogger: bool = True, level="debug"
    ) -> None:
        if useLogger:
            getattr(self.__logger, level)(*args)
        else:
            print(*args, flush=flush)

        return
