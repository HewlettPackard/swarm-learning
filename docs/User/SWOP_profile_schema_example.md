# <a name="GUID-E34AFBFE-8DE3-4E6F-AB51-C87C98CFAF15"/> SWOP profile schema example

```
######################################################################
## (C)Copyright 2021 Hewlett Packard Enterprise Development LP
######################################################################
groupname  : demo
taskrunner : defaulttaskbb.taskdb.sml.hpe
policyuri  : ~
resourcemgr :
    mgrtype    : DOCKER
    accessinfo :
        accesstype : FROMENV
network    : host-1-net
apls :
    locator :
        host : 172.1.1.1
        port : ~
apisrv :
    locator :
        host : 172.1.1.1
        port : ~
# ENVVARs passed to the SL Container at start up
envvars :
    - SL_LOG_LEVEL : INFO
    - http_proxy : "http://web-proxy.x.y.z:8080"
    - https_proxy : "http://web-proxy.x.y.z:8080"
    - no_proxy : ~
    - HTTP_PROXY : ~
    - HTTPS_PROXY : ~
    - NO_PROXY : ~
# Docker image name and tag for the SL containers
# will come from tasks pre-reqs
# Docker user image name and tag for the USR containers
# will come from tasks pre-reqs

# Detail on the number and specification of each SL NODE
# this profile will create.
nodes :
    - slnodedef :
        idx : 0
        identity :
            - attribute :
                aType : KEY
                mType : BIND
                src : "<CURRENT-PATH>/workspace/mnist-pyt/cert/sl-1-key.pem"
                tgt : "/swarm-cert/sl-1-key.pem"
                subPath : null
            - attribute :
                aType : CERT
                mType : BIND
                src : "<CURRENT-PATH>/workspace/mnist-pyt/cert/sl-1-cert.pem"
                tgt : "/swarm-cert/sl-1-cert.pem"
                subPath : null
            - attribute :
                aType : CAPATH
                mType : BIND
                src : "<CURRENT-PATH>/workspace/mnist-pyt/cert/ca/capath"
                tgt : "/swarm-cert/capath"
                subPath : null
        slhostname : sl1
        slhostip   : 172.1.1.1
        slport : 16000
        usrhostname : user1
        privatedata :
            src: "<CURRENT-PATH>/workspace/mnist-pyt/user1/data-and-scratch"
            mType : BIND
        slenvvars : null
        usrenvvars : null
        usrcontaineropts :
            - gpus : "all" #To run on all available GPUs
    - slnodedef :
        idx : 1
        identity :
            - attribute :
                aType : KEY
                mType : BIND
                src : "<CURRENT-PATH>/workspace/mnist-pyt/cert/sl-1-key.pem"
                tgt : "/swarm-cert/sl-2-key.pem"
                subPath : null
            - attribute :
                aType : CERT
                mType : BIND
                src : "<CURRENT-PATH>/workspace/mnist-pyt/cert/sl-1-cert.pem"
                tgt : "/swarm-cert/sl-2-cert.pem"
                subPath : null
            - attribute :
                aType : CAPATH
                mType : BIND
                src : "<CURRENT-PATH>/workspace/mnist-pyt/cert/ca/capath"
                tgt : "/swarm-cert/capath"
                subPath : null
        slhostname : sl2
        slhostip   : 172.1.1.1
        slport : 17000
        usrhostname : user2
        privatedata :
            src: "<CURRENT-PATH>/workspace/mnist-pyt/user2/data-and-scratch"
            mType : BIND
        slenvvars : null
        usrenvvars : null
        usrcontaineropts :
            - gpus : "device=3,5" #To run on GPUs 3 and 5
```

