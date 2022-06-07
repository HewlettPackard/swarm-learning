# <a name="GUID-852B2D67-627E-409F-91E7-E4B239ED6932"/> Task for pulling a prebuilt Docker image

```
Name: pull-task-tf2
TaskType : PULL_IMAGE
Author   : HPE-TEST
Prereq   : ROOTTASK
Outcome  : "hub.docker.hpecorp.net/hub/tensorflow-tensorflow:2.7.0"
Body     : 
    Tag        : "2.7.0"
    RepoName   : "tensorflow-tensorflow"
    OrgAndReg  : "hub.docker.hpecorp.net/hub/"
    Auth       : ~
```

