# SWOP profile schema example using reverse proxy parameters

``` {#CODEBLOCK_JWF_42V_PVB}
######################################################################
## (C)Copyright 2022,2023 Hewlett Packard Enterprise Development LP
######################################################################

groupname: demo
taskrunner: defaulttaskbb.taskdb.sml.hpe
network: <NETWORK-NAME>
policyuri: ~
resourcemgr:
    mgrtype: DOCKER
    accessinfo:
        accesstype: FROMENV
apls:
    locator:
        host: <APLS-IP>
        port: ~
apisrv:
    locator:
        host: ~
        port: ~
        service: ~
envvars: 
    - SL_LOG_LEVEL : INFO
    - http_proxy : ~
    - https_proxy : ~
    - no_proxy : ~
    - HTTP_PROXY : ~
    - HTTPS_PROXY : ~
    - NO_PROXY : ~
dns: 
    - <Bind9-IP>
    - <Host-DNS-IP>
nodes:
    - slnodedef:
        idx: 0
        identity:
            - attribute:
                aType: KEY
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/cifar10/cert/sl-1-key.pem"
                tgt: "/swarm-cert/swarm-key.pem"
                subPath: null
            - attribute:
                aType: CERT
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/cifar10/cert/sl-1-cert.pem"
                tgt: "/swarm-cert/swarm-cert.pem"
                subPath: null
            - attribute:
                aType: CAPATH
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/cifar10/cert/ca/capath"
                tgt: "/swarm-cert/capath"
                subPath: null
        slhostname: sl-1.swarm
        slhostip: ~
        slport: ~
        slfsservice: fs.sl-1.swarm
        slenvvars: null
        slnetworkopts:
            - ip: <SL-IP-1>
        usrhostname: ml-1
        usrenvvars: null
        usrnetworkopts:
            - ip: <ML-IP-1>
        privatedata : ~
    - slnodedef:
        idx: 1
        identity:
            - attribute:
                aType: KEY
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/cifar10/cert/sl-1-key.pem"
                tgt: "/swarm-cert/swarm-key.pem"
                subPath: null
            - attribute:
                aType: CERT
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/cifar10/cert/sl-1-cert.pem"
                tgt: "/swarm-cert/swarm-cert.pem"
                subPath: null
            - attribute:
                aType: CAPATH
                mType: BIND
                src: "<CURRENT-PATH>/workspace/reverse-proxy/cifar10/cert/ca/capath"
                tgt: "/swarm-cert/capath"
                subPath: null
        slhostname: sl-2.swarm
        slhostip: ~
        slport: ~
        slfsservice: fs.sl-2.swarm
        slenvvars: null
        slnetworkopts:
            - ip: <SL-IP-2>
        usrhostname: ml-2
        usrenvvars: null
        usrnetworkopts:
            - ip: <ML-IP-2>
        privatedata : ~
```

**Parent topic:**[Launch Swarm Learning using SWOP](Launch_Swarm_Learning_using_SWOP.md)

