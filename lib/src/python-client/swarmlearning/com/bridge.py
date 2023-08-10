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


from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import TypeVar, Union

import os
import stat
import time

import swarmlearning.com.swifrpc_pb2 as spb


MessageBody = Union[
    spb.Status
  , spb.SessionRequest
  , spb.SessionResponse
  , spb.SyncRequest
  , spb.SyncResponse
  , spb.LossRequest
  , spb.LossResponse
]

BridgeLaneDirection = TypeVar("Bridge.LaneDirection")


class Bridge:
    class LaneDirection(IntEnum):
        NorthBound = 1
        SouthBound = 2

    def __init__(self, isSL=False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__setAPIVersion()
        
        # createPipes is set to True for SL container.
        # WARNING: If it is set to True from ML container,
        #          then ML call to mkfifo might fail as ML runs with limited privileges.
        self._createPipes = isSL

        self._lanes = {}
        self._openLanes = {}
        self.__makeBridgeLanes()

        # These values must be non-zero. Zero values get optimized out, giving
        # us a serialized size that is smaller than what we want.
        dummyHeader = spb.Header(apiVersion=self._apiVer, msgType=1, msgSize=1)
        self._serializedHeaderSize = len(
            dummyHeader.SerializeToString(deterministic=True)
        )

        # self.__logIt(f"HEADER SIZE = {self._serializedHeaderSize}")

        return

    def __setAPIVersion(self) -> None:
        # Fetching the api version from the dynamically generated proto code.
        apiVerFrmProto = spb.DESCRIPTOR.GetOptions().Extensions[spb.apiVersion]
        # Building _apiVer as spb.APIVersion structure type. This will be used to 
        # set the api version inside the header of _send method.
        self._apiVer = spb.APIVersion(apiVersion=apiVerFrmProto, minVersion=apiVerFrmProto)
        return

    def _verifyAPIVersion(self, verionFromHeader: spb.APIVersion) -> None:
        # Left side is the api version from the header of the _recv method
        # Right side is the api version from the dynamically generated proto file
        if verionFromHeader.apiVersion != self._apiVer.apiVersion:
            raise RuntimeError(f"Mismatch in the Swarm API version between ML and SL containers. Expected version {self._apiVer.apiVersion}, but the version received from the header is {verionFromHeader.apiVersion}")
        return

    def _verifyMessageType(self, msgType: spb.MessageType) -> None:
        if (
            (msgType <= spb.MessageType.MsgTypeFirst) or
            (msgType >= spb.MessageType.MsgTypeLast)
           ):
            raise RuntimeError(f"unsupported message type: {msgType}")

        return

    def _sendRecv(
        self
      , sendLane: BridgeLaneDirection
      , recvLane: BridgeLaneDirection
      , msgType: int
      , request: MessageBody
    ) -> (spb.MessageType, MessageBody):
        self._send(sendLane, msgType, request)
        resp = self._recv(recvLane)

        return resp

    def _send(
        self, sendLane: BridgeLaneDirection, msgType: int, request: MessageBody
    ) -> None:
        body = request.SerializeToString(deterministic=True)
        header = spb.Header(
            apiVersion=self._apiVer, msgType=msgType, msgSize=len(body)
        )
        # message = spb.Message(header=header, body=body)

        # chunk the message into 2GB blocks.
        lane = self._openLanes[sendLane]

        # Send the header and body separately until we understand the protobuf
        # serialization format a little better and figure how to send the whole
        # message but, receive and extract only the header.
        lane.write(header.SerializeToString(deterministic=True))
        lane.write(body)
        # lane.write(message.SerializeToString(deterministic=True))
        lane.flush()

        return

    def _recv(
        self, recvLane: BridgeLaneDirection
    ) -> (spb.MessageType, MessageBody):
        serializedHeader = self._read(recvLane, self._serializedHeaderSize)
        header = spb.Header()
        header.ParseFromString(serializedHeader)
        # self.__logIt(f"Header = <{type(header)}> = <{header}>")

        self._verifyAPIVersion(header.apiVersion)
        self._verifyMessageType(header.msgType)

        if header.msgType == spb.MessageType.MsgTypeStatus:
            body = spb.Status()
        elif header.msgType == spb.MessageType.MsgTypeOpenSessionRequest:
            body = spb.SessionRequest()
        elif header.msgType == spb.MessageType.MsgTypeOpenSessionResponse:
            body = spb.SessionResponse()
        elif header.msgType == spb.MessageType.MsgTypeCloseSessionRequest:
            body = spb.SyncRequest()
        elif header.msgType == spb.MessageType.MsgTypeCloseSessionResponse:
            body = spb.SyncResponse()
        elif header.msgType == spb.MessageType.MsgTypeSyncRequest:
            body = spb.SyncRequest()
        elif header.msgType == spb.MessageType.MsgTypeSyncResponse:
            body = spb.SyncResponse()
        elif header.msgType == spb.MessageType.MsgTypeGetLossRequest:
            body = spb.LossRequest()
        elif header.msgType == spb.MessageType.MsgTypeGetLossResponse:
            body = spb.LossResponse()
        elif header.msgType == spb.MessageType.MsgTypeKillSessionRequest:
            body = spb.KillSessionRequest()
        else:
            # Should not get here. We have already validated the message type.
            raise RuntimeError(f"unsupported message type: {header.msgType}")

        serializedBody = self._read(recvLane, header.msgSize)
        body.ParseFromString(serializedBody)

        return header.msgType, body

    def _read(self, recvLane: BridgeLaneDirection, nBytes: int) -> bytes:
        lane = self._openLanes[recvLane]
        msg = lane.read(nBytes)
        if len(msg) != nBytes:
            raise RuntimeError(
                f"wanted: {nBytes} bytes, got {len(msg)} bytes: pipe closed?"
            )

        return msg

    def _openBridgeLanes(
        self, *, northBoundMode: str, southBoundMode: str
    ) -> None:
        def openLane(direction: BridgeLaneDirection, mode: str) -> None:
            # self.__logIt(f"Opening [{direction}] = <{self._lanes[direction]}> in <{mode}> mode")
            self._openLanes[direction] = open(self._lanes[direction], mode)
            # self.__logIt(f"Opened [{direction}] = <{self._lanes[direction]}> in <{mode}> mode")
            return

        openLane(self.LaneDirection.NorthBound, northBoundMode)
        openLane(self.LaneDirection.SouthBound, southBoundMode)

        return

    def __makeBridgeLanes(self) -> None:
        def getPath(envvar: str) -> str:
            pipePath = os.getenv(envvar)

            if pipePath is None or len(pipePath) == 0:
                raise RuntimeError(
                    f"{envvar}: bad environment variable; cannot create bridge"
                )

            return Path(pipePath).resolve().as_posix()

        def makeLane(lane: str, direction: BridgeLaneDirection) -> None:
            try:
                self._lanes[direction] = lane
                # self.__logIt(f"Creating [{direction}] = <{self._lanes[direction]}>")
                if(self._createPipes):
                    os.mkfifo(lane, 0o777)
                    self.__logIt(f"{lane}: pipe created")
                else:
                    while(not(os.path.exists(lane))):
                        self.__logIt(f"{lane}: waiting for pipes to be created")
                        time.sleep(1)
                # self.__logIt(f"Created [{direction}] = <{self._lanes[direction]}>")

            except FileExistsError:
                self.__logIt(f"{lane}: File exists")
            except BaseException as be:
                self.__logIt(f"{lane}: {be}")

            if not stat.S_ISFIFO(os.stat(lane).st_mode):
                raise RuntimeError(f"{lane}: cannot create pipe")

        # The default umask seems to be 022. It is applied to the mode specified
        # in mkfifo. Therefore, even though we ask for 777, what we actually get
        # is 755. This prevents the two ends of the bridge from having different
        # user IDs - the second party will not have the requisite permissions to
        # open the FIFO is write mode. We workaround this by disabling the mask,
        # creating the pipes, and then, restoring the mask.
        currMask = os.umask(0)

        makeLane(getPath("SL_REQUEST_CHANNEL"), self.LaneDirection.SouthBound)
        makeLane(getPath("SL_RESPONSE_CHANNEL"), self.LaneDirection.NorthBound)

        os.umask(currMask)

        return

    def __logIt(self, *args, **kwargs):
        print(datetime.now().isoformat(), *args, **kwargs, flush=True)
        return
