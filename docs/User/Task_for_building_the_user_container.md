# <a name="GUID-089572CD-4EEA-478F-AB54-87C96135585B"/> Task for building the user container

```
Name: user_env_tf_build_task
TaskType: MAKE_USER_CONTAINER
Author: HPE-TEST
Prereq: ROOTTASK
Outcome: user-env-tf2.7.0-swop
Body:
    BuildContext: sl-cli-lib    #A docker volume that is created by User. 
                                #It should have the Swarm Learning wheel 
                                #file copied in to it.
    BuildType: INLINE    
    BuildSteps:
    - FROM tensorflow/tensorflow:2.7.0
    - ' '
    - RUN pip3 install --upgrade pip && pip3 install \
    - '   keras matplotlib opencv-python pandas protobuf==3.15.6 sklearn'
    - ' '
    - RUN mkdir -p /tmp/hpe-swarmcli-pkg
    - COPY swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl /tmp/hpe-swarmcli-pkg/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
    - RUN pip3 install /tmp/hpe-swarmcli-pkg/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
```

