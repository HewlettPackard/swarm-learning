# <a name="GUID-108C02BD-5825-4642-BA99-5E77714F7A68"/> SWOP profile schema

<blockquote>
NOTE:

The source code of the profile schema [SWOP-profile-schema.yaml](/docs/SWOP-profile-schema.yaml).

</blockquote>

```<a name="CODEBLOCK_NBD_FSY_CTB"/> 
######################################################################
## (C)Copyright 2021-2023 Hewlett Packard Enterprise Development LP
######################################################################
"$schema"   : "https://json-schema.org/draft/2020-12/schema"
title       : "SWOP Profile definition"
description : "Describes the structure of the profile file"
type        : object
properties  : 
    groupname  :
        type        : string
        description : "name of the profile group" 
    taskrunner : 
        type        : string
        description : "id of the taskrunner contract to use" 
    policyuri  : 
        description : "None (no policy accept all tasks) or uri to the policy engine" 
        oneOf : 
            - const : ~
            - type  : string
    resourcemgr     : 
        type         : object
        description  : "Specification of the underlying resourcemgr.
                        Currently only DOCKER is supported"
        properties   :
            mgrtype : 
                description  : "Identifies the resource manager type"
                type : string
                enum : 
                    - DOCKER
            accessinfo : 
                oneOf  :
                    - type  : object                        
                      description : "Specifies how to instantiate docker client 
                                     FROMENV - Return a client configured from environment variables. 
                                     The environment variables used are the same as those 
                                     used by the Docker command-line client. Currently FROMENV only supported.
                                     It can be extended to instantiate client that will allow you to communicate 
                                     with a Docker daemon through UNIX socket or SSL"
                      properties  :
                          accesstype: 
                              type : string 
                              enum : 
                                  - FROMENV 
                      required    :
                          - accesstype
                      additionalProperties : false                      
        required     : 
            - mgrtype
            - accessinfo
        additionalProperties : false        
    network    :
        type        : string
        description : "Nework to attach the SL containers" 
    apls       : 
        type        : object
        description : "APLS object definition"
        properties  :
            locator : 
                type        : "object"
                properties  : 
                    host  : 
                        type : string
                    port : 
                        oneOf :  
                            - type : integer 
                              minimum: 0 
                            - const : ~
                required : 
                    - host
                additionalProperties : false                    
        required    : 
            - locator
        additionalProperties : false                      
    apisrv     :
        type         : object
        description  : "API SERVER object definition"
        properties   :
            locator  :
                type       : object
                properties :
                    host  :
                        oneOf:
                            - type: string
                              maxLength: 253
                              minLength: 1
                            - const : ~
                    port :
                        oneOf :
                            - type : integer
                              minimum: 0
                            - const : ~
                    service:
                        oneOf:
                            - type: string
                              maxLength: 253
                              minLength: 1
                            - const : ~
                required :
                    - host
                    - service
                additionalProperties : false
    envvars    : 
        oneOf       : 
          - const   : ~
          - type    : array
            description : "List of global environmental variables as K-V pair common to all SL nodes"
            items       : 
                type        : object
                uniqueItems : true

    # Allow service endpoints to be specified as domain names, rather than IPs.
    # Traffic can be routed through a reverse proxy or a web gateway by making
    # these name servers resolve the domain names into the IP of the reverse 
    # proxy and then, configuring the reverse proxy to forward to the appropriate 
    # service. This is at a global level for now - primarily because we cannot 
    # think of a use case for two containers on a production box wanting to use 
    # different name servers. If and when someone demonstrates the scenario, we 
    # can move this field down to the nodes section. To limit the current scope 
    # of work, we do not support any of the other related parameters, such as
    # dns-opt, dns-search and domain-name. Further, we feel we should explore
    # ways to create an open specification that can accept all valid parameters
    # and not just a chosen handful.
    dns:
        oneOf:
          - const: ~
          - type: array
            description: "List of custom DNS servers"
            items:
                type: string
                maxLength: 253
                minLength: 1
                uniqueItems: true

    nodes      : 
        type        : array
        description : "List of Node specifications managed by this SWOP entity"
        items       :
            - slnodedef : 
                  type       : object 
                  properties : 
                      idx         :
                          type    : integer 
                          description : "Identifier for the SL node in this SWOP profile"
                          # this index is provided by user it has to start with 0 
                          # and be positive integer only
                          minimum : 0
                      identity    :
                        type        : array
                        description : "Information about identity of this node"
                        items       :
                            - attribute  :  
                                type        : object
                                description : "Specification of the certificates or spiffe endpoint"
                                properties  :
                                    aType       :
                                        type        : string                        
                                        description : "Identity specification attribute type" 
                                        enum        : 
                                            - KEY
                                            - CERT 
                                            - CACERT
                                            - CAPATH
                                            - SPIFFE_SOCKETPATH
                                    mType       :
                                        type        : string
                                        description : "Type of mount to be used to mount the user data"
                                        enum        : 
                                            - BIND
                                            - VOLUME
                                    src          : 
                                        type        : string
                                        description : "Host directory or fullpath or Volume name to be used for Mount"
                                        maxLength   : 240
                                        minLength   : 2 
                                    tgt          : 
                                        type        : string
                                        description : "Target directory or fullpath inside container"
                                        maxLength   : 240
                                        minLength   : 2 
                                    subPath         : 
                                        oneOf : 
                                            - const   : ~
                                            - type        : string
                                              description : "Optional sub-path to the resource realtive to tgt"
                                              maxLength   : 240
                                              minLength   : 2
                                required    : 
                                    - aType
                                    - mType
                                    - src
                                    - tgt
                                    - subpath
                                additionalProperties : false
                      slhostip    :
                          oneOf:
                              - const: ~
                              - type    : string
                                description : "Externally visible IPv4 Address or FQDN of the SL Container"
                                maxLength   : 240
                                minLength   : 2                          
                      slport      :
                          oneOf : 
                              - const   : ~
                              - type    : integer 
                                description : "FS Server port exposed by this SL NODE (default 30305)"
                                minimum : 0
                      slfsservice:
                          oneOf:
                              - const: ~
                              - type: string
                                description: "FQDN and optional port of the FS service for the SL Container"
                                # https://stackoverflow.com/a/32294443.
                                maxLength: 253
                                minLength: 2
                      slhostname :
                          oneOf : 
                              - const   : ~
                              - type    : string
                                description : "Docker host name for the SL container"
                                maxLength   : 240
                                minLength   : 2                                                          
                      privatedata :          
                          oneOf : 
                              - const   : ~
                              - type    : object 
                                description : "Private data store this node exposes as bind or volume mount"
                                properties:
                                    src :
                                        type        : string
                                        description : "Source Volume or directory"
                                        maxLength   : 240
                                        minLength   : 2
                                    # destination will come from the RUN-SWARM task definition 
                                    # the program will decide where in the Filesystem this dir 
                                    # will be mounted to.
                                    mType :
                                        type : string
                                        description : "Type of mount to be used to mount the user data"
                                        enum : 
                                            - BIND
                                            - VOLUME                                
                                required:
                                    - src
                                    - mType
                                additionalProperties: false
                      slenvvars   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : "List of local environmental variables as K-V pair specific to SL node.
                                               This will take precedence over global environmental variables."
                                items       : 
                                    type        : object
                                    uniqueItems : true

                      # In our practice, we are using labels only for the SPIFFE selector not envvars.
                      sllabels:
                          oneOf:
                            - const: ~
                            - type: object
                              description: "Dictionary of labels for the Swarm Learning container"
                              items:
                                  uniqueItems: true
                            - type: array
                              description: "List of labels with empty values for the Swarm Learning container"
                              items:
                                  type: string
                                  uniqueItems: true
                      # This attribute helps in starting SL container with pre-defined python docker network SDK option called "ipv4_address"
                      # Added as part of reverse proxy multi-host scenario where instead of using hostIP with in nginx configuration we can
                      # now use continer IP's for easier and simpler IP and port mapping.
                      slnetworkopts   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : "List of K-V pairs passed directly to connect SL docker container to specific network.
                                              This option is needed to start the SL container with a static IP. The IP address is 
                                              passed using 'ip' key inside slnetworkopts. This will get converted to ipv4_address 
                                              argument of the python docker sdk network connect method. This is same as passing '--ip' 
                                              argument to the docker cli run command.
                                              "
                                items : 
                                    type : object
                                    uniqueItems : true

                      usrhostname :
                          oneOf : 
                              - const   : ~
                              - type    : string
                                description : "Externally visible IPv4 Address or FQDN of the USR Container"
                                maxLength   : 240
                                minLength   : 2  
                      usrenvvars   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : "List of local environmental variables as K-V pair specific to USR Container.
                                               This will take precedence over global environmental variables specified in 
                                               run task definition."
                                items       : 
                                    type        : object
                                    uniqueItems : true

                      usrlabels:
                          oneOf:
                            - const: ~
                            - type: object
                              description: "Dictionary of labels for the user ML container"
                              items:
                                  uniqueItems: true
                            - type: array
                              description: "List of labels with empty values for the user ML container"
                              items:
                                  type: string
                                  uniqueItems: true
                      # This attribute helps in starting ML container with pre-defined python docker network SDK options called "ipv4_address"
                      # Added as part of reverse proxy multi-host scenario where instead of using hostIP with in nginx configuration we can
                      # now use continer IP's for easier and simpler IP and port mapping.
                      usrnetworkopts   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : "List of K-V pairs passed directly to connect user docker container to specific network.
                                              This option is needed to start the user container with a static IP. The IP address is 
                                              passed using 'ip' key inside usrnetworkopts. This will get converted to ipv4_address 
                                              argument of the python docker sdk network connect method. This is same as passing '--ip' 
                                              argument to the docker cli run command.
                                              "
                                items : 
                                    type : object
                                    uniqueItems : true
                      usrcontaineropts   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : |
                                               "List of K-V pairs passed directly to docker while starting USR container.
                                               These options are needed to use GPUs for user ML local training.
                                               These options are specific to GPU vendors. Refer options as applicable to your GPU vendor."
                                               1. Nvidia GPUs -   
                                               "Only 'gpus' key is supported. Refer below link to know how to specify the values. 
                                               https://docs.docker.com/config/containers/resource_constraints/#gpu "
                                               
                                               2. AMD GPUs - 
                                               "Keys supported are 'device', 'ipc', 'shm-size', 'group-add',
                                               'cap-add', 'security-opt', 'privileged'.
                                               Refer below link to know the options for AMD GPU access.
                                               https://developer.amd.com/resources/rocm-learning-center/deep-learning/
                                               
                                               Required options varies for tensorflow and pytorch.
                                               Tensorflow ====>> sudo docker run -it --network=host --device=/dev/kfd --device=/dev/dri 
                                               --ipc=host --shm-size 16G --group-add video --cap-add=SYS_PTRACE 
                                               --security-opt seccomp=unconfined -v $HOME/dockerx:/dockerx rocm/tensorflow:latest
                                               PyTorch ====>> sudo docker run -it -v $HOME:/data --privileged --rm --device=/dev/kfd 
                                               --device=/dev/dri --group-add video rocm/pytorch:rocm3.5_ubuntu16.04_py3.6_pytorch"
                                               
                                               Example for specifing values - 
                                               - device : ["/dev/kfd", "/dev/dri"] # (list of str) -> Expose host devices to the container, 
                                                                                     as a list of strings
                                               - ipc : "host"                      # (str) -> Set the IPC mode for the container
                                               - shm-size : "16G"                  # (str) -> Size of /dev/shm (e.g. 1G)
                                               - group-add : ["video"]             # (list of str) -> List of additional group names 
                                                                                     and/or IDs that the container process will run as.
                                               - cap-add : ["SYS_PTRACE"]          # (list of str) -> Add kernel capabilities. 
                                               - security-opt : ["seccomp=unconfined"] # (list of str) -> A list of string values to customize labels 
                                                                                         for MLS systems, such as SELinux.
                                               - privileged : True                 # (bool) -> Give extended privileges to this container.
                                               
                                items : 
                                    type : object
                                    uniqueItems : true
                  required   :
                      - idx
                      - identity
                      - slhostname
                      - privatedata
                      - slenvvars
                      - usrhostname
                      - usrenvvars
                  additionalProperties: false 
        uniqueItems : true

required    : 
    - groupname
    - taskrunner
    - policyuri
    - resourcemgr
    - network 
    - apls
    - apisrv
    - envvars
    - nodes
additionalProperties: false
