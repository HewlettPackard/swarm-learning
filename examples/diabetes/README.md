## Diabetes Prediction
   
This example runs decentralized training on Diabetes dataset for diabetes clasification using TensorFlow based Swarm Learning framework.

The data is obtained from the [here](https://www.kaggle.com/datasets/tigganeha4/diabetes-dataset-2019 "here").
The data has been preprocessed by using the Label Encoding Techniques to change the textual data to numerical data.
Eg: Gender is a categorical feature, where Female is encoded to 0 and male is encoded to 1.
The preprocessed data is present in the ``swarm-learning/examples/diabetes/app-data/`` directory. With the dataset two scripts ``data_splitting.py`` and ``data_reset.py`` has  been provided. Their functions are:
- ``data_splitting.py`` - Splits the data into three parts before the experiment, to be executed before initialising the swarm environment.
- ``data_reset.py`` - Clears the data that had been splitted , to be executed after the experimentation is done.

The model program, after conversion to Swarm Learning, is in ``swarm-learning/examples/diabetes/model/`` and is called ``diabetes.py``. 

Before running the example, verify license server is running and valid license is installed. Refer [Installing licenses and starting license server](../../docs/setup.md#installing-licenses-and-starting-license-server).

## Running the example

1. Run the ``data_splitting.py`` and share the all the splits to all the three nodes. i.e one for each

2. On all the three hosts, navigate to swarm-learning folder \(that is, parent to examples directory\).

    ```
    cd swarm-learning
    ```
3. On both host-1, host-2 and host-3, create a temporary workspace directory and copy `diabetes` example.

    ```
    diabetes workspace
    cp -r examples/diabetes workspace/
    cp -r examples/utils/gen-cert workspace/diabetes/
    ```
4. On both host-1,host-2 and host-3, run the gen-cert utility to generate certificates for each Swarm component using the command \(`gen-cert -e <EXAMPLE-NAME> -i <HOST-INDEX>`\):

    On host-1:
    ```
    ./workspace/diabetes/gen-cert -e diabetes -i 1
    ```
    On host-2:
    ```
    ./workspace/diabetes/gen-cert -e diabetes -i 2
    ```
    On-host-3:
    ```
    ./workspace/diabetes/gen-cert -e diabetes -i 3
    ```
5. On all hosts, share the CA certificates between the hosts as follows:

    On host-1:
    ```
    scp host-2:<PATH>workspace/diabetes/cert/ca/capath/ca-2-cert.pem workspace/diabetes/cert/ca/capath
    ```
    On host-2:
    ```
    scp host-3:<PATH>workspace/diabetes/cert/ca/capath/ca-3-cert.pem workspace/diabetes/cert/ca/capath
    ```
    On host-3:
    ```
    scp host-1:<PATH>workspace/diabetes/cert/ca/capath/ca-1-cert.pem workspace/diabetes/cert/ca/capath
    ```
6.  On both host-1 and host-2, search and replace all occurrences of `<CURRENT-PATH>` tag in `swarm_diabetes_task.yaml` and `swop_profile.yaml` files with `$(pwd)`.

    ```
    sed -i "s+<CURRENT-PATH>+$(pwd)+g" workspace/diabetes/swop/swop*_profile.yaml workspace/diabetes/swci/taskdefs/swarm_diabetes_task.yaml
    ```
7.  On all three hosts, create a Docker volume and copy Swarm Learning wheel file.

    ```
    docker volume rm sl-cli-lib
    docker volume create sl-cli-lib
    docker container create --name helper -v sl-cli-lib:/data hello-world
    docker cp -L lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl helper:/data
    docker rm helper
    ```
8.  On all three hosts, create a Docker network for SN, SWOP, SWCI, SL, and user containers running in a host.

    On host-1:

    ```
    docker network create host-1-net
    ```

    On host-2:

    ```
    docker network create host-2-net
    ```
    On host-3:

    ```
    docker network create host-3-net
    ```
9.  On host-1, run SN node \(SN1\).

    ```
    ./scripts/bin/run-sn -d --rm --name=sn1 --network=host-1-net \
    --host-ip=172.1.1.1 --sentinel --sn-p2p-port=30303 \
    --sn-api-port=30304 --key=workspace/diabetes/cert/sn-1-key.pem \
    --cert=workspace/diabetes/cert/sn-1-cert.pem \
    --capath=workspace/diabetes/cert/ca/capath --apls-ip=172.1.1.1
    ```

    Use the Docker logs command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when these messages appear in the log output:

    ```
    swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304
    ```

    On host-2, run SN node (SN2).

    ```
    ./scripts/bin/run-sn -d --rm --name=sn2 --network=host-2-net \
    --host-ip=172.2.2.2
    --sentinel-ip=172.1.1.1 --sn-p2p-port=30303 \
    --sn-api-port=30304 --key=workspace/diabetes/cert/sn-2-key.pem \
    --cert=workspace/diabetes/cert/sn-2-cert.pem \
    --capath=workspace/diabetes/cert/ca/capath --apls-ip=172.1.1.1
    ```
    
    On host-3, run SN node (SN2).

    ```
    ./scripts/bin/run-sn -d --rm --name=sn2 --network=host-2-net \
    --host-ip=172.3.3.3 --sentinel-ip=172.1.1.1 --sn-p2p-port=30303 \
    --sn-api-port=30304 --key=workspace/diabetes/cert/sn-3-key.pem \
    --cert=workspace/diabetes/cert/sn-3-cert.pem \
    --capath=workspace/diabetes/cert/ca/capath --apls-ip=172.1.1.1
    ```
10.  On host-1, run SWOP node (SWOP1).
        ```
        ./scripts/bin/run-swop -d --rm --name=swop1 --network=host-1-net \
        --usr-dir=workspace/diabetes/swop --profile-file-name=swop1_profile.yaml \
        --key=workspace/diabetes/cert/swop-1-key.pem \
        --cert=workspace/diabetes/cert/swop-1-cert.pem \
        --capath=workspace/diabetes/cert/ca/capath -e http_proxy= -e \
        https_proxy= --apls-ip=172.1.1.1
        ```

        On host-2, run SWOP node (SWOP2).
        ```
            ./scripts/bin/run-swop -d --rm --name=swop2 --network=host-2-net \
        --usr-dir=workspace/diabetes/swop --profile-file-name=swop2_profile.yaml \
        --key=workspace/diabetes/cert/swop-2-key.pem \
        --cert=workspace/diabetes/cert/swop-2-cert.pem \
        --capath=workspace/diabetes/cert/ca/capath -e http_proxy= -e\
        https_proxy= --apls-ip=172.1.1.1
        ```
        On host-3, run SWOP node (SWOP3).
        ```
            ./scripts/bin/run-swop -d --rm --name=swop3 --network=host-3-net \
        --usr-dir=workspace/diabetes/swop --profile-file-name=swop3_profile.yaml \
        --key=workspace/diabetes/cert/swop-3-key.pem \
        --cert=workspace/diabetes/cert/swop-3cert.pem \
        --capath=workspace/diabetes/cert/ca/capath -e http_proxy= -e\
        https_proxy= --apls-ip=172.1.1.1
        ```
10. On host-1, run SWCI node. It creates, finalizes, and assigns two tasks sequentially for execution:

-   `user_env_tf_build_task` - builds TensorFlow based ML nodes with model and data.

-   `swarm_diabetes_task` - run Swarm training across for two ML nodes.

    ```
    ./scripts/bin/run-swci -ti --rm --name=swci1 --network=host-1-net \
    --usr-dir=workspace/diabetes/swci --init-script-name=swci-init \
    --key=workspace/diabetes/cert/swci-1-key.pem \
    --cert=workspace/diabetes/cert/swci-1-cert.pem \
    --capath=workspace/diabetes/cert/ca/capath \
    -e http_proxy= -e https_proxy= --apls-ip=172.1.1.1
    ```
11. On all hosts, three nodes of Swarm trainings are automatically started when the run task \(`swarm_diabetes_task`\) gets assigned and executed. Open a new terminal on the hosts and monitor the docker logs of ML nodes for Swarm training. Swarm training will end with the following log message:

    ```
    SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.
    ```

    Final Swarm model is saved inside `workspace/diabetes/model` directory on both the hosts. All the dynamically spawned SL and ML nodes exits after Swarm training. The SN and SWOP nodes continues to run.

12. On all the hosts, to clean up, run the `scripts/bin/stop-swarm` script on all the systems to stop and remove the container nodes of the previous run. If required, backup the container logs. Remove Docker networks \(`host-1-net` and `host-2-net` and `host-3-net`) and Docker volume \(`sl-cli-lib`\), and delete the workspace directory.

11. Finally after running all the nodes clear the data by running ``data_reset.py`` to reset the dataset.
