# <a name="GUID-C19A68F3-7509-413C-8F50-EE9DC29D95DB"/> SWOP task schema

<blockquote>
NOTE:

The source code of the task schema [SWOP-task-schema.yaml](/docs/SWOP-task-schema.yaml).

</blockquote>

```<a name="CODEBLOCK_MTZ_3S1_DTB"/> 
######################################################################
## (C)Copyright 2021,2022 Hewlett Packard Enterprise Development LP
######################################################################
"$schema"   : "https://json-schema.org/draft/2020-12/schema"
title       : "SWOP TASK definition"
description : "Describes a task structure"
type        : object
# ALL FREE STRINGS are MAX of 160 chars long
# we use utf-8 encoding followed by base64 encoding
# to make strings safe for transmission and storage.
# All string are stored in 256 byte containers in 
# the blockchain. Base64 encoding bloats string by 
# ~33%. Hence 160 char long utf-8 sting will become 
# 213 ,8-bit chars. 160 is chosen so that we have 
# some space for internal appends ~32 more chars. 
properties  :
    Name     :
        description : "Name of the Task being deployed" 
        type        : string
        maxLength   : 160  
        minLength   : 1
    TaskType : 
       description  : "Type of the task one the above enum values"
       type         : "string"
       enum         : 
           - RUN_SWARM 
           - MAKE_SWARM_USER_CONTENT
           - MAKE_USER_CONTAINER
           - PULL_IMAGE
    Author   :
        description : "Author of this task" 
        type        : string
        maxLength   : 160
        minLength   : 1
    Prereq   : 
        description : "Name of the prerequisite task for this task" 
        type        : string
        maxLength   : 160
        minLength   : 1
    Outcome  :
        description : "Identifier of the outcome of this task" 
        type        : string
        maxLength   : 160
        minLength   : 1
    Body     :
        description : "Specification of the task, that matches the type of the task"
        oneOf : 
            - type     : object
              description : "FORMAT FOR MAKE_USER_CONTAINER"
              properties  :
                BuildContext :
                    oneOf:
                        - const  : ~
                        - type   : string
                          description : "Name of the volume containing the context for this build" 
                          # NOTE: contents of this volume will be copied into the build context 
                          # temp dir before that actual build process begins
                          maxLength : 160
                          minLength : 3                                        
                BuildSteps :
                    type     : array
                    description : "BUILD STEPS FOR MAKE_USER_CONTAINER" 
                    items    :
                        type      : string
                        maxLength : 160
                        minLength : 0                                        
                    minItems : 1
                    maxItems : 80
                BuildType  :
                    type : string
                    description : "Specifies the nature of BuildSteps, IF INLINE BuildSteps is Contents of docker File, IF REMOTE its an URL pointing to the Docker file (currently not implemented)"
                    enum : 
                        - INLINE
                        - REMOTE                    
              required    :
                - BuildContext
                - BuildSteps
                - BuildType
              additionalProperties : false                    
            - type     : object
              description : "FORMAT FOR RUN_SWARM"
              properties  :
                Command         : 
                    type        : string 
                    description : "Command string to execute Ex: mnist.py --minpeers=3"
                    maxLength   : 160 
                    minLength   : 1
                Entrypoint      : 
                    type        : string 
                    description : "Entrypoint used to execute Ex: python3, bash"
                    maxLength   : 160 
                    minLength   : 1   
                WorkingDir      :     
                    type        : string 
                    description : "Absolute path with in the container to set as Working directory"
                    maxLength   : 160 
                    minLength   : 2  
                Envvars         : 
                    oneOf:
                        - const : ~
                        - type : array
                          description : "List of environmental values as K-V pair"
                          items : 
                            type : object
                            uniqueItems : true                   
                PrivateContent  :
                    oneOf:
                        - const       : ~                    
                        - type        : string 
                          description : "The mount point the USR container where the private data will be mounted"
                          maxLength   : 160 
                          minLength   : 2                    
                SharedContent   :
                    oneOf:
                        - const       : ~
                        - type        : array
                          description : "list of user content volume to be mounted on the user image"
                          items : 
                                - type : object
                                  description : "Mount information"
                                  properties  :
                                        Src :
                                            type        : string
                                            description : "Source Volume or directory"
                                            maxLength   : 160
                                            minLength   : 2
                                        Tgt : 
                                            type        : string
                                            description : "destination directory within container"
                                            maxLength   : 160
                                            minLength   : 2 
                                        MType :
                                            type : string
                                            description : "Type of mount to be used to mount the user data"
                                            enum : 
                                                - BIND
                                                - VOLUME                                         
                                  required : 
                                    - Src
                                    - Tgt
                                    - MType
                                  additionalProperties : false  
                          maxItems   : 10
                          minItems   : 1
              required    :
                - Command
                - Entrypoint
                - SharedContent
                - WorkingDir
                - Envvars
                - PrivateContent
              additionalProperties : false
            - type     : object
              description : "FORMAT FOR PULL_IMAGE"
              properties  :
                Tag             : 
                    type        : string 
                    description : "image tag , Ex: latest, 0.3.0, 1.0.0, GA-release"
                    maxLength   : 160
                    minLength   : 1
                RepoName        : 
                    type        : string 
                    description : "Name of the repository in which the tag is defined"
                    maxLength   : 160
                    minLength   : 1   
                OrgAndReg       : 
                    type        : string 
                    description : "Org and Registry under which the repository is hosted"
                    maxLength   : 160
                    minLength   : 1                    
                Auth :
                    oneOf:
                        - const       : ~
                        - type        : string 
                          description : "Path to custom config.json"
                          maxLength   : 160
                          minLength   : 1
                        - type        : object
                          description : "USERNAME and PASSWORD"
                          properties  :
                            Username : 
                                type : string 
                                maxLength : 160 
                                minLength : 1 
                            Password :
                                type : string 
                                maxLength : 160 
                                minLength : 0
                          required    :
                                - Username
                                - Password
                          additionalProperties : false    
              required    :
                - Tag
                - RepoName
                - OrgAndReg
                - Auth
              additionalProperties : false              
            - type     : object 
              description : "FORMAT FOR MAKE_SWARM_USER_CONTENT"
              properties : 
                  ContentType : 
                      type : string
                      description : "Purpose of the volume being created"
                      # Note: if contenttype is 'BUILDCONTENT, 
                      # only one copy of the volume is made.
                      # if contenttype is 'SWARMCONTENT', 
                      # many copies are made depending on SWOP profile.
                      enum : 
                        - BUILDCONTENT
                        - SWARMCONTENT            
                  OpsList     : 
                      description : "Content to populate in model dir or docker build content dir, etc" 
                      type        : array
                      minItems    : 1               
                      maxItems    : 20
                      items       :
                          - type       : object 
                            properties : 
                                Operation : 
                                    description  : "Type of the sub-task"
                                    type         : "string"
                                    enum         : 
                                        - DOWNLOAD 
                                        - EXTRACT
                                Target    :
                                    type        : string
                                    description : "URI to perform the actions"
                                    maxLength   : 160
                                    minLength   : 1
                                Options  :
                                    type        : array 
                                    description : "options that is passed to OPERATION : format key:value"
                                    # Currently we support "Out" option for both the tasks 
                                    items       :
                                        type  : object
                                    uniqueItems : true      
                                    minItems    : 0
                            required   :
                                - Target
                                - Options
                                - Operation
                            additionalProperties : false                  
              required    :
                - ContentType
                - OpsList
              additionalProperties : false                            
required    : 
    - Name
    - TaskType 
    - Author
    - Prereq
    - Outcome
    - Body
additionalProperties : false
