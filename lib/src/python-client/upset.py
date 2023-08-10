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

import os


__swarmVer__ = (
    os.getenv("SWARMVER"
  , os.getenv("swarmver"
  , os.getenv("SwarmVer"
  , os.getenv("SWARM_VER"
  , os.getenv("swarm_ver"
  , None
))))))


if __swarmVer__ is None:
    with open("../../../releases/current") as currRel:
        __swarmVer__ = currRel.read()


# __buildBase__ = (
    # os.getenv("BUILDBASE"
  # , os.getenv("buildbase"
  # , os.getenv("BuildBase"
  # , os.getenv("BUILD_BASE"
  # , os.getenv("build_base"
  # , "/tmp/swarmlearning"
# ))))))

# os.makedirs(__buildBase__, exist_ok=True)
