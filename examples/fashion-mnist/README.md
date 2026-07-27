# Fashion-MNIST: CascadedDP with Non-Uniform Partitioning

This example trains a Fashion-MNIST classifier across a Two-ML-Node (both run on the same VM/Physical machine) HPE Swarm Learning setup using CascadedDP: training begins with Differential Privacy (DP) active, and DP is automatically dropped once convergence is detected via a decentralized weight parameter consensus protocol.The model is a standard small CNN (matching the TF Privacy / Opacus canonical DP-SGD benchmark architecture for MNIST/Fashion-MNIST), not a plain MLP.

To protect data privacy, the training process uses Differential Privacy (DP). This method introduces controlled noise into the learning process so that sensitive details of the underlying data cannot be inferred from the trained model. However, maintaining DP throughout the entire training process can reduce model accuracy and slow convergence. To address this, the project uses a technique called CascadedDP. Training begins with DP enabled, and DP is automatically disabled once the model reaches a stable state. This stable state is detected using a decentralized consensus protocol, in which the two nodes compare their model weight updates to determine when convergence has occurred.

To simulate realistic, real-world conditions, the training data can be distributed unevenly between the two nodes. It is partitioned using a Dirichlet distribution, which creates non-identical and unevenly distributed (non-IID) data across nodes. We can control this unevenness using a parameter alpha. Smaller values of alpha give progressively more uneven distributions. This means each node is exposed to a different distribution of clothing categories, reflecting the kind of data imbalance often seen in practical applications.

|<img width="1055" height="1125" alt="Cascaded DP Architecture Flowchart" src="https://github.com/user-attachments/assets/00cebdcc-2d3f-416a-af15-67eb87fa7ef5" />|
|:--:|
|<b>Figure 1: Cascaded DP Architecture Flowchart for the Fashion-MNIST Swarm Learning Example</b>|

The ML program is in `workspace/fashion-mnist/model` and is called `fashion-mnist_nonuniform.py`.
See the [`result.md/`](./result/results.md) folder for accuracy and runtime benchmarks.

**Stack:** TensorFlow · TensorFlow Privacy · HPE Swarm Learning

This example shows the Swarm training of a Fashion-MNIST classifier using two Machine Learning (ML) nodes launched directly via `run-sl`, without SWOP or SWCI. All nodes run on a single host. This example also shows how private data, scratch spaces, and model files can be mounted to Machine Learning nodes for Swarm training.

## Cluster Setup

The cluster setup for this example uses only one host, as shown in the figure below:
- host-1: 172.1.1.1

|<img width="1372" height="771" alt="Fashion-MNIST-cluster-setup" src="https://github.com/user-attachments/assets/52e11724-6b98-4ca7-9763-3b12f7edbcb1" />|
|:--:|
|<b>Figure 1: Cluster setup for the Cascaded DP Fashion MNIST example</b>|

* This example uses one Swarm Network (SN) node. The name of the docker container representing this node is `sn1`. `sn1` is also the Sentinel Node. `sn1` runs on host 172.1.1.1.
* Two Swarm Learning (SL) and two Machine Learning (ML) nodes are launched directly using `run-sl`. The names of the docker containers representing these nodes are `sl1` and `sl2`, with associated ML containers `ml1` and `ml2`. Both run on host 172.1.1.1.
* Training begins automatically once both SL nodes are up and the `MIN_PEERS` quorum is satisfied; no SWCI node is required.
* This example assumes that a License Server (APLS) already runs on host 172.1.1.1. All Swarm nodes connect to the License Server on its default port 5814.

## Project Structure

```text
fashion-mnist/
├── cert/
├── ml-context/
│   ├── Dockerfile
│   └── requirements.txt
├── model/
│   └── fashion-mnist_nonuniform.py
├── result/
│   ├── Accuracy_Bar.png
│   ├── Runtime_Bar.png
│   └── results.md
├── tmp/
│   ├── sl1/
│   └── sl2/
└── README.md

```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `MAX_EPOCHS` | 50 | Total training epochs |
| `MIN_PEERS` | 2 | Minimum Swarm peers before sync |
| `NODE_ID` | 0 | Node index (0-based) |
| `NUM_NODES` | 2 | Total number of nodes |
| `OPTIMIZER` | sgd | sgd or adam |
| `LEARNING_RATE` | 0 | Override LR (0 = auto: 0.001 for Adam, 0.01 for SGD) |
| `DP_ENABLED` | true | Enable Differential Privacy |
| `NOISE_MULTIPLIER` | 0.0 | Gaussian noise multiplier for DP-SGD/DP-Adam |
| `L2_NORM_CLIP` | 1.0 | Gradient clipping norm for DP |
| `MICROBATCHES` | 32 | Microbatch size for DP optimizer |
| `CASCADED_DP` | false | Enable convergence-triggered DP drop |
| `DP_DROP_WINDOW` | 5 | Rolling window size for convergence signals |
| `MIN_DP_EPOCHS` | 5 | Minimum epochs before convergence checks begin (burn-in period; no drop is evaluated during this window) |
| `GRAD_THRESHOLD` | 0.01 | Fixed absolute threshold on the epoch-to-epoch rolling gradient-norm slope. Convergence requires this to fall below the threshold |
| `ACC_THRESHOLD` | 0.0005 | Fixed absolute threshold on windowed validation-accuracy variance. Convergence requires this to fall below the threshold |
| `DIRICHLET_ALPHA` | inf | Dirichlet alpha for partitioning (inf = IID) |
| `RESULT_FILE` | results.json | Output JSON filename under /results/ |

---

## Running the Fashion-MNIST CascadedDP Example

### Setup

1. **On host-1:** Change to the swarm-learning folder (the parent of the examples directory).
```bash
cd swarm-learning

```


2. **On host-1:** Create a workspace directory and copy the example and gen-cert utility into it.
```bash
mkdir -p workspace
cp -r examples/fashion-mnist workspace/
cp -r examples/utils/gen-cert workspace/fashion-mnist/

```


3. **On host-1:** Generate certificates for each Swarm component.
```bash
./workspace/fashion-mnist/gen-cert -e fashion-mnist -i 1
./workspace/fashion-mnist/gen-cert -e fashion-mnist -i 2

```


4. **On host-1:** Remove the SWOP and SWCI certificates that were auto-generated but are not needed for this setup.
```bash
cd workspace/fashion-mnist/cert
rm swop-* swci-*
cd ../../../

```


5. **On host-1:** Create a network called `host-1-net` using the docker network create command. This network will be used for SN, SL, and ML containers. Please ignore this step if this network is already created.
```bash
docker network create host-1-net

```


6. **On host-1:** Create separate temporary mount directories for each SL node and a results directory. Set appropriate permissions.
```bash
mkdir -p ./workspace/fashion-mnist/tmp/sl1
mkdir -p ./workspace/fashion-mnist/tmp/sl2
mkdir -p ./workspace/fashion-mnist/results
chmod -R 777 ./workspace/fashion-mnist/tmp
chmod -R 777 ./workspace/fashion-mnist/results

```


7. **On host-1:** Copy the SwarmLearning wheel file into the ML Docker build context.
```bash
cp ./lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl \
./workspace/fashion-mnist/ml-context/swarmlearning-0.0.1-py3-none-manylinux_2_24_x86_64.whl

```


8. **On host-1:** Build the ML Docker image that will be used to run the Fashion-MNIST model inside the ML containers.
```bash
docker build -t fashion-ml-env \
./workspace/fashion-mnist/ml-context

```


9. **On host-1:** Run the APLS license server container if it is not already running or not connected.
```bash
docker run -d \
--name apls \
--network host-1-net \
-v apls-volume:/hpe \
-p 5814:5814 \
--restart unless-stopped \
hub.myenterpriselicense.hpe.com/hpe_eval/autopass/apls:9.19

```


10. **On host-1:** Declare and assign values to the environment variables. The values mentioned here are for illustration purposes only. Use appropriate values as per your swarm network (check your machine's IP using `hostname -I`).
```bash
export HOST_IP=172.1.1.1
export SN_IP=172.1.1.1
export APLS_IP=172.1.1.1
export SN_API_PORT=30304

```


11. **On host-1:** Run the Swarm Network node (`sn1`), which serves as the Sentinel node.
```bash

./scripts/bin/run-sn -d --name=sn1 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sentinel \
--sn-api-port=${SN_API_PORT} \
--key=workspace/fashion-mnist/cert/sn-1-key.pem \
--cert=workspace/fashion-mnist/cert/sn-1-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--apls-ip=${APLS_IP}

```



Use the `docker logs` command to monitor the Sentinel SN node and wait for the node to finish initializing. The Sentinel node is ready when this message appears in the log output:

```text
swarm.blCnt : INFO : Starting SWARM-API-SERVER on port: 30304

```

---

### Running Experiments

> **Note:** Before starting each new experiment, stop and remove containers from the previous run:
> ```bash
> docker rm -f sn1 sl1 sl2 ml1 ml2 2>/dev/null
> 
> ```
> 
> 
> Then re-run the SN node (step 11 above) and wait for it to initialize before launching SL nodes.

#### Experiment 1: Baseline (No DP)

* **On host-1: Run SL1**
```bash
./scripts/bin/run-sl -d --name=sl1 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=16000 \
--key=workspace/fashion-mnist/cert/sl-1-key.pem \
--cert=workspace/fashion-mnist/cert/sl-1-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--ml-image=fashion-ml-env \
--ml-name=ml1 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fashion-mnist_nonuniform.py \
-v ~/swarm-learning/workspace/fashion-mnist/tmp/sl1:/tmp/hpe-swarm \
--ml-v ~/swarm-learning/workspace/fashion-mnist/model:/tmp/test/model \
--ml-v ~/swarm-learning/workspace/fashion-mnist/results:/results \
--ml-e RESULT_FILE=exp_baseline_sl1.json \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=50 \
--ml-e NODE_ID=0 \
--ml-e NUM_NODES=2 \
--ml-e DIRICHLET_ALPHA=inf \
--ml-e OPTIMIZER=adam \
--ml-e LEARNING_RATE=0.001 \
--ml-e DP_ENABLED=false \
--apls-ip=${APLS_IP}

docker logs -f ml1 > \
./workspace/fashion-mnist/results/exp_baseline_ml1.log 2>&1 &

```


* **On host-1: Run SL2**
```bash
./scripts/bin/run-sl -d --name=sl2 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=17000 \
--key=workspace/fashion-mnist/cert/sl-2-key.pem \
--cert=workspace/fashion-mnist/cert/sl-2-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--ml-image=fashion-ml-env \
--ml-name=ml2 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fashion-mnist_nonuniform.py \
-v ~/swarm-learning/workspace/fashion-mnist/tmp/sl2:/tmp/hpe-swarm \
--ml-v ~/swarm-learning/workspace/fashion-mnist/model:/tmp/test/model \
--ml-v ~/swarm-learning/workspace/fashion-mnist/results:/results \
--ml-e RESULT_FILE=exp_baseline_sl2.json \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=50 \
--ml-e NODE_ID=1 \
--ml-e NUM_NODES=2 \
--ml-e DIRICHLET_ALPHA=inf \
--ml-e OPTIMIZER=adam \
--ml-e LEARNING_RATE=0.001 \
--ml-e DP_ENABLED=false \
--apls-ip=${APLS_IP}

docker logs -f ml2 > \
./workspace/fashion-mnist/results/exp_baseline_ml2.log 2>&1 &

```



#### Experiment 2: Full DP (No Drop)

* **On host-1: Run SL1**
```bash
./scripts/bin/run-sl -d --name=sl1 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=16000 \
--key=workspace/fashion-mnist/cert/sl-1-key.pem \
--cert=workspace/fashion-mnist/cert/sl-1-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--ml-image=fashion-ml-env \
--ml-name=ml1 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fashion-mnist_nonuniform.py \
-v ~/swarm-learning/workspace/fashion-mnist/tmp/sl1:/tmp/hpe-swarm \
--ml-v ~/swarm-learning/workspace/fashion-mnist/model:/tmp/test/model \
--ml-v ~/swarm-learning/workspace/fashion-mnist/results:/results \
--ml-e RESULT_FILE=exp_full_dp_sl1.json \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=50 \
--ml-e NODE_ID=0 \
--ml-e NUM_NODES=2 \
--ml-e DIRICHLET_ALPHA=inf \
--ml-e OPTIMIZER=adam \
--ml-e LEARNING_RATE=0.001 \
--ml-e DP_ENABLED=true \
--ml-e NOISE_MULTIPLIER=1.0 \
--ml-e L2_NORM_CLIP=1.0 \
--ml-e MICROBATCHES=32 \
--ml-e CASCADED_DP=false \
--apls-ip=${APLS_IP}

docker logs -f ml1 > \
./workspace/fashion-mnist/results/exp_full_dp_ml1.log 2>&1 &

```


* **On host-1: Run SL2**
```bash
./scripts/bin/run-sl -d --name=sl2 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=17000 \
--key=workspace/fashion-mnist/cert/sl-2-key.pem \
--cert=workspace/fashion-mnist/cert/sl-2-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--ml-image=fashion-ml-env \
--ml-name=ml2 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fashion-mnist_nonuniform.py \
-v ~/swarm-learning/workspace/fashion-mnist/tmp/sl2:/tmp/hpe-swarm \
--ml-v ~/swarm-learning/workspace/fashion-mnist/model:/tmp/test/model \
--ml-v ~/swarm-learning/workspace/fashion-mnist/results:/results \
--ml-e RESULT_FILE=exp_full_dp_sl2.json \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=50 \
--ml-e NODE_ID=1 \
--ml-e NUM_NODES=2 \
--ml-e DIRICHLET_ALPHA=inf \
--ml-e OPTIMIZER=adam \
--ml-e LEARNING_RATE=0.001 \
--ml-e DP_ENABLED=true \
--ml-e NOISE_MULTIPLIER=1.0 \
--ml-e L2_NORM_CLIP=1.0 \
--ml-e MICROBATCHES=32 \
--ml-e CASCADED_DP=false \
--apls-ip=${APLS_IP}

docker logs -f ml2 > \
./workspace/fashion-mnist/results/exp_full_dp_ml2.log 2>&1 &

```



#### Experiment 3: CascadedDP (Convergence-Triggered DP Drop)

* **On host-1: Run SL1**
```bash
./scripts/bin/run-sl -d --name=sl1 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=16000 \
--key=workspace/fashion-mnist/cert/sl-1-key.pem \
--cert=workspace/fashion-mnist/cert/sl-1-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--ml-image=fashion-ml-env \
--ml-name=ml1 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fashion-mnist_nonuniform.py \
-v ~/swarm-learning/workspace/fashion-mnist/tmp/sl1:/tmp/hpe-swarm \
--ml-v ~/swarm-learning/workspace/fashion-mnist/model:/tmp/test/model \
--ml-v ~/swarm-learning/workspace/fashion-mnist/results:/results \
--ml-e RESULT_FILE=exp_cascaded_dp_sl1.json \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=50 \
--ml-e NODE_ID=0 \
--ml-e NUM_NODES=2 \
--ml-e DIRICHLET_ALPHA=inf \
--ml-e OPTIMIZER=adam \
--ml-e LEARNING_RATE=0.001 \
--ml-e DP_ENABLED=true \
--ml-e NOISE_MULTIPLIER=1.0 \
--ml-e L2_NORM_CLIP=1.0 \
--ml-e MICROBATCHES=32 \
--ml-e CASCADED_DP=true \
--ml-e DP_DROP_WINDOW=5 \
--ml-e MIN_DP_EPOCHS=5 \
--ml-e GRAD_THRESHOLD=0.4 \
--ml-e ACC_THRESHOLD=0.0005 \
--apls-ip=${APLS_IP}

docker logs -f ml1 > \
./workspace/fashion-mnist/results/exp_cascaded_dp_ml1.log 2>&1 &

```


* **On host-1: Run SL2**
```bash
./scripts/bin/run-sl -d --name=sl2 \
--network=host-1-net \
--host-ip=${HOST_IP} \
--sn-ip=${SN_IP} \
--sn-api-port=${SN_API_PORT} \
--sl-fs-port=17000 \
--key=workspace/fashion-mnist/cert/sl-2-key.pem \
--cert=workspace/fashion-mnist/cert/sl-2-cert.pem \
--capath=workspace/fashion-mnist/cert/ca/capath \
--ml-image=fashion-ml-env \
--ml-name=ml2 \
--ml-entrypoint=python3 \
--ml-cmd=/tmp/test/model/fashion-mnist_nonuniform.py \
-v ~/swarm-learning/workspace/fashion-mnist/tmp/sl2:/tmp/hpe-swarm \
--ml-v ~/swarm-learning/workspace/fashion-mnist/model:/tmp/test/model \
--ml-v ~/swarm-learning/workspace/fashion-mnist/results:/results \
--ml-e RESULT_FILE=exp_cascaded_dp_sl2.json \
--ml-e MIN_PEERS=2 \
--ml-e MAX_EPOCHS=50 \
--ml-e NODE_ID=1 \
--ml-e NUM_NODES=2 \
--ml-e DIRICHLET_ALPHA=inf \
--ml-e OPTIMIZER=adam \
--ml-e LEARNING_RATE=0.001 \
--ml-e DP_ENABLED=true \
--ml-e NOISE_MULTIPLIER=1.0 \
--ml-e L2_NORM_CLIP=1.0 \
--ml-e MICROBATCHES=32 \
--ml-e CASCADED_DP=true \
--ml-e DP_DROP_WINDOW=5 \
--ml-e MIN_DP_EPOCHS=5 \
--ml-e GRAD_THRESHOLD=0.4 \
--ml-e ACC_THRESHOLD=0.0005 \
--apls-ip=${APLS_IP}

docker logs -f ml2 > \
./workspace/fashion-mnist/results/exp_cascaded_dp_ml2.log 2>&1 &

```



Swarm training will end with the following log message at the end:

```text
SwarmCallback : INFO : All peers and Swarm training rounds finished. Final Swarm model was loaded.

```

Result JSON files will be saved under `workspace/fashion-mnist/results/`. To clean up, stop and remove all containers and remove the workspace directory.

---

## How CascadedDP Works

Training starts with the DP optimizer active. During the first `MIN_DP_EPOCHS` epochs (burn-in), each node simply collects gradient-norm and validation-accuracy samples every epoch; no convergence check is run yet, and no per-node noise floor is estimated. Convergence is judged against fixed, absolute thresholds (`GRAD_THRESHOLD`, `ACC_THRESHOLD`), which remain the same for every run regardless of dataset or architecture noise; so these are the values to sweep if the drop is triggering too early or too late.

After burn-in, and once the rolling window has filled to `DP_DROP_WINDOW` epochs, each node checks two signals every epoch:

1. **Gradient norm slope:** The absolute change between the last two rolling-mean gradient-norm values (mean gradient norm over the last `DP_DROP_WINDOW` epochs), compared against `GRAD_THRESHOLD`.
2. **Validation accuracy variance:** The variance of validation accuracy over the same `DP_DROP_WINDOW`-epoch window, compared against `ACC_THRESHOLD`.

When both signals fall below their thresholds, the node sets `local_converged = True` and writes 1.0 into an internal, non-trainable tracking model parameter via a custom model layer (`ConvergenceFlagLayer`). If either signal is not yet satisfied, the node re-asserts 0.0 on that parameter every epoch. This re-assertion matters because otherwise a partially-merged flag value from a Swarm sync round (e.g., 0.5) would sit uncorrected and creep toward quorum on its own.

During Swarm parameter synchronization rounds, the Swarm learning mechanism aggregates these tracking weights across all participants by averaging, weighted by each node's `nodeWeightage` (its share of the total training data):

$$\text{Global Consensus Value} = \sum_{i=1}^{N} w_i \cdot \text{Node Flag}_i$$

Because the merge is weighted by data share rather than a simple headcount average, under a skewed Dirichlet split the flag value read back by a node reflects the weighted fraction of data that has converged, not a raw count of converged nodes. It is still only treated as full consensus once it reaches $\ge 0.999$ (a tolerance for floating-point rounding, not a literal exact match to 1.0).

Once quorum is detected, every node recompiles its model with a standard, non-private optimizer (dropping the DP wrapper) and clears its cached Keras training/test/predict functions so the new optimizer takes effect immediately.

Privacy accounting (epsilon) is computed only for the exact epochs in which DP was actively running (`dp_drop_epoch`, or the full `MAX_EPOCHS` if DP was never dropped). **Known limitation:** Stage 2 (post-drop) currently runs with zero noise, so this $\varepsilon$ does not cover the full training run.

---

## Notes

* **TensorFlow:** 2.7.0
* **TensorFlow Privacy:** 0.7.3
* Adjust `DIRICHLET_ALPHA` to sweep heterogeneity levels across experiments. Lower values produce more skewed class distributions.


## References
[1] H. Xiao, K. Rasul and R. Vollgraf, "Fashion-MNIST: a Novel Image Dataset for Benchmarking Machine Learning Algorithms," arXiv:1708.07747, 2017. [Online]. Available:
https://arxiv.org/abs/1708.07747

[2] https://www.tensorflow.org/tutorials/quickstart/beginner
