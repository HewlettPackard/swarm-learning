# <a name="GUID-108C02BD-5825-4642-BA99-5E77714F7A68"/> SWOP profile schema

<blockquote>
NOTE:

The source code of the profile schema \(`SWOP-profile-schema.yaml`\) is present in the same directory as the User Guide.

</blockquote>

```<a name="CODEBLOCK_NBD_FSY_CTB"/> 
######################################################################
## (C)Copyright 2021-2022 Hewlett Packard Enterprise Development LP
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
                        type : string
                    port : 
                        oneOf :  
                            - type : integer
                              minimum: 0 
                            - const : ~
                required : 
                    - host
                additionalProperties : false                    
        required : 
            - locator
        additionalProperties : false
    envvars    : 
        oneOf       : 
          - const   : ~
          - type    : array
            description : "List of global environmental variables as K-V pair common to all SL nodes"
            items       : 
                type        : object
                uniqueItems : true
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
                          type    : string
                          description : "Externally visible IPv4 Address or FDQN of the SL Container"
                          maxLength   : 240
                          minLength   : 2                          
                      slport      :
                          oneOf : 
                              - const   : ~
                              - type    : integer 
                                description : "FS Server port exposed by this SL NODE (default 30305)"
                                minimum : 0
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
                      usrhostname :
                          oneOf : 
                              - const   : ~
                              - type    : string
                                description : "Externally visible IPv4 Address or FDQN of the USR Container"
                                maxLength   : 240
                                minLength   : 2  
                      usrenvvars   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : "List of local environmental variables as K-V pair specific to USR Container.
                                               This will take precedence over environmental variables specified in run task definition."
                                items       : 
                                    type        : object
                                    uniqueItems : true
                      usrcontaineropts   : 
                          oneOf       : 
                              - const   : ~
                              - type    : array
                                description : "List of K-V pairs passed directly to docker while starting USR container.
                                               Key supported only 'gpus'. Refer below link to know how to specify the values. 
                                               https://docs.docker.com/config/containers/resource_constraints/#gpu "
                                items : 
                                    type : object
                                    uniqueItems : true
                  required   :
                      - idx
                      - identity
                      - slhostname
                      - slport 
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
```

