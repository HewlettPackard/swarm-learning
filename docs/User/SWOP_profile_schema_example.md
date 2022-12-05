# <a name="GUID-E34AFBFE-8DE3-4E6F-AB51-C87C98CFAF15"/> SWOP profile schema example

```
######################################################################
## (C)Copyright 2022 Hewlett Packard Enterprise Development LP
######################################################################

groupname: reverse-proxy-demo
taskrunner: defaulttaskbb.taskdb.sml.hpe
network: default
policyuri: ~
resourcemgr:
    mgrtype: DOCKER
    accessinfo:
        accesstype: FROMENV
apls:
    locator:
        host: 172.1.1.1
        port: ~
apisrv:
    locator:
        host: ~
        port: ~
        service: api.sn-1.swarm
envvars: ~
dns:
    - 172.2.2.2
nodes:
    - slnodedef:
        idx: 0
        identity:
            - attribute:
                aType: KEY
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/cert/sl-1-key.pem"
                tgt: "/swarm-cert/swarm-key.pem"
                subPath: null
            - attribute:
                aType: CERT
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/cert/sl-1-cert.pem"
                tgt: "/swarm-cert/swarm-cert.pem"
                subPath: null
            - attribute:
                aType: CAPATH
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/cert/ca/capath"
                tgt: "/swarm-cert/capath"
                subPath: null
        slhostname: null
        slhostip: null
        slport: null
        slfsservice: fs.sl-1.swarm
        slenvvars: null
        usrhostname: user1
        usrenvvars: null
        privatedata :
            src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/app-data"
            mType : BIND
    - slnodedef:
        idx: 1
        identity:
            - attribute:
                aType: KEY
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/cert/sl-2-key.pem"
                tgt: "/swarm-cert/swarm-key.pem"
                subPath: null
            - attribute:
                aType: CERT
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/cert/sl-2-cert.pem"
                tgt: "/swarm-cert/swarm-cert.pem"
                subPath: null
            - attribute:
                aType: CAPATH
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/cert/ca/capath"
                tgt: "/swarm-cert/capath"
                subPath: null
        slhostname: null
        slhostip: null
        slport: null
        slfsservice: fs.sl-2.swarm
        slenvvars: null
        usrhostname: user2
        usrenvvars: null
        privatedata :
            src: "<CURRENT-PATH>/workspace/reverse-proxy/mnist/app-data"
            mType : BIND
        slenvvars : null
        usrenvvars : null
        usrcontaineropts :
            - gpus : "device=3,5" #To run on GPUs 3 and 5
```

