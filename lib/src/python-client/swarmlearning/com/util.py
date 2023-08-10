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
from datetime import datetime as dt
from typing import Dict

import numpy as np

# Our imports.
import swarmlearning.com.swifrpc_pb2 as spb


def fromWeights(weights: spb.Weights) -> Dict[str, np.ndarray]:
    # print(f"{dt.now().isoformat()} Deserializing weights", flush=True)

    params = {
        # repr(dtype) produces something like, "dtype(...)". Python does not
        # recognize a bare "dtype" - we must supply "np.dtype".
        name: np.ndarray(arr.shape, eval("np." + arr.dtype), arr.data)
        for name, arr in weights.weights.items()
    }

    # print(f"{dt.now().isoformat()} Deserialized weights", flush=True)

    return params


def toWeights(params: Dict[str, np.ndarray]) -> spb.Weights:
    # print(f"{dt.now().isoformat()} Serializing weights", flush=True)

    weightsDict = {
        name: spb.NDArray(
            dtype=repr(arr.dtype)
          , shape=arr.shape
          , data=arr.tobytes(order="C")
        )            
        for name, arr in params.items()
    }
    weights = spb.Weights(weights=weightsDict)

    # print(f"{dt.now().isoformat()} Serialized weights", flush=True)

    return weights
