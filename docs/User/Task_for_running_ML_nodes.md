# <a name="GUID-A3DA5B27-3466-4C9F-9CB2-CE3CAA3B83F1"/> Task for running ML nodes

```
Name: swarm_mnist_task
TaskType: RUN_SWARM
Author: HPE-TEST
Prereq: user_env_tf_build_task
Outcome: swarm_mnist_task
Body:
    Command: model/mnist_tf.py
    Entrypoint: python3
    WorkingDir: /tmp/test
    Envvars: ["DATA_DIR": app-data, "MODEL_DIR": model, "MAX_EPOCHS": 2, "MIN_PEERS": 2]
    PrivateContent: /tmp/test/app-data
    SharedContent:
    -   Src: <CURRENT-PATH>/workspace/mnist/model
        Tgt: /tmp/test/model
        MType: BIND
```

