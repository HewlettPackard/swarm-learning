# <a name="GUID-BEFFCB5B-ACDA-45CC-A904-A79D02D60730"/> Task for creating a Docker volume of model program and data

```
Name: download-task-mnist-local
TaskType : MAKE_SWARM_USER_CONTENT
Author   : HPE-TEST
Prereq   : ROOTTASK
Outcome  : mnist-msn
Body     : 
    ContentType : SWARMCONTENT
    OpsList :
        - Operation : DOWNLOAD
#          Target    : "https://raw.githubusercontent.com/HewlettPackard/swarm-learning/master/examples/mnist-keras/model/mnist_tf.py"
          Target    : "http://172.2.2.2:9292/mnist/model/mnist_tf.py"
          Options   : 
            - Out   : "model/mnist_tf.py"
        - Operation : DOWNLOAD
#          Target    : "https://github.com/HewlettPackard/swarm-learning/raw/master/examples/mnist-keras/app-data/mnist.npz"
          Target    : "http://172.2.2.2:9292/mnist/data/mnist.npz"
          Options   : 
            - Out   : "data/mnist.npz"
```

