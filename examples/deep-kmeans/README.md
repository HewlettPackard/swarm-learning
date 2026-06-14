# Deep K-Means: Federated Anomaly Detection for Network Intrusion

Federated network intrusion detection using Deep K-Means (DEC) on the NSL-KDD dataset, running on HPE Swarm Learning with TensorFlow 2.7.

**Reference:** Fard et al., *Deep k-Means: Jointly Clustering with k-Means and Learning Representations* (arXiv:1806.10069)

## Overview

This example trains a federated anomaly detector that learns what **normal** network traffic looks like — without sharing raw data between nodes. At inference time, traffic that doesn't fit the learned normal profile is flagged as an intrusion.

The approach uses Deep K-Means (DEC), which reformulates clustering as a neural network so it can be federated:

- An **autoencoder** (122→64→32→10→32→64→122) learns a compact latent representation of network traffic through reconstruction loss — capturing the statistical signature of normal traffic
- A **ClusteringLayer** holds K cluster centroids as trainable weights updated via backpropagation
- The combined loss `L = MSE(reconstruction) + λ · KLD(soft assignments)` drives both representation learning and cluster separation
- HPE Swarm Learning's `SwarmCallback` syncs all weights (encoder, decoder, centroids) across nodes after every `syncFrequency` batches

No raw traffic data leaves any node. The federated model learns from all nodes' traffic patterns while preserving data privacy.

### Two-Phase Training

| Phase | Scope | Epochs | Loss | Swarm sync? |
|-------|-------|--------|------|-------------|
| 1 — Pretrain | Each node independently | 30 | MSE (reconstruction) | No |
| 2 — Joint | All nodes federated | 30 | λ·KLD + MSE | Yes |

Phase 1 trains an autoencoder locally on each node's traffic data, bootstrapping a meaningful latent space without federation. Phase 2 initialises cluster centroids with K-Means on the pretrained embeddings, then trains the full model with `SwarmCallback` active — federating both the representation and the clustering across all nodes.

### Architecture

```
Encoder:     Input(122) → Dense(64,relu) → Dense(32,relu) → Dense(10,linear)
Autoencoder: Encoder → Dense(32,relu) → Dense(64,relu) → Dense(122,linear)
Combined:    Input(122) → Encoder(10) ─┬─ ClusteringLayer(K=5) → cluster_out  [KLD]
                                        └─ Dense(32)→Dense(64)→Dense(122)  → recon_out [MSE]
```

## Directory Structure

```
deep-kmeans/
├── model/
│   ├── autoencoder.py       # Main training script (SwarmCallback integrated)
│   ├── evaluate.py          # Post-training binary detection accuracy + NMI
│   ├── predict.py           # Binary intrusion detection using saved model
│   └── standalone_run.py    # Single-node run for quick testing
├── data-prep/
│   ├── prepare_data.py      # Creates non-IID node splits from KDDTrain+_full.txt
│   └── encoders.pkl         # Saved preprocessing state
├── data-and-scratch{1..4}/  # Node N private data + output scratch directory
│   └── app-data/
│       └── KDDTrain+.txt    # Node N training split (non-IID)
├── swci/
│   ├── swci-init            # SWCI orchestration script
│   └── taskdefs/
│       ├── user_env_dkm_build_task.yaml   # Builds user Docker image
│       └── swarm_dkm_task.yaml            # Swarm training task definition
├── swop/
│   └── swop1_profile.yaml   # SWOP node profile (nodes, certs, data mounts)
└── data-prep/
    └── prepare_data.py      # Non-IID data split generator
```

## Prerequisites

- HPE Swarm Learning 2.3.0 (SN, SWOP, SWCI, SL images)
- AutoPass License Server (APLS) running with a valid Swarm Learning license
- Docker with a shared network (e.g. `host-1-net`)
- Certificates generated for SN, SWOP, SWCI, and SL nodes (a single `sl-1` cert/key pair works for all SL nodes on one host)

## Quick Start — Swarm Mode

All commands run from the `swarm-learning/` root directory.

### 1. Workspace setup

```bash
mkdir -p workspace
cp -r examples/deep-kmeans workspace/
```

### 2. Prepare data

Download the NSL-KDD dataset (`KDDTrain+_20Percent.txt` or the full `KDDTrain+.txt`) from the [UNB NSL-KDD page](https://www.unb.ca/cic/datasets/nsl.html) and run:

```bash
cd examples/deep-kmeans
python3 data-prep/prepare_data.py --input /path/to/KDDTrain+_full.txt --nodes 4
```

This creates `data-and-scratch{1..4}/app-data/KDDTrain+.txt` — non-IID splits where each node receives a different traffic mix (normal-heavy, DoS-heavy, probe-heavy, mixed). Copy the same `KDDTest+.txt` into each node's `app-data/` for evaluation.


### 3. Generate certificates

```bash
cd workspace/deep-kmeans && bash gen-cert -e deep-kmeans -i 1 && cd -
```

This produces `workspace/deep-kmeans/cert/` with keys and certs for sn-1, swop-1, swci-1, sl-1.

### 4. Create Docker network

```bash
docker network create host-1-net
```

### 5. Substitute placeholders in config files

```bash
APLS_IP=<your-apls-server-ip>
CURRENT_PATH=$(pwd)

# Task definition: model source path
sed -i "s|<CURRENT-PATH>|${CURRENT_PATH}|g" \
    workspace/deep-kmeans/swci/taskdefs/swarm_dkm_task.yaml

# SWOP profile: network, cert paths, data paths, APLS
sed -i \
  -e "s|<SWARM-NETWORK>|host-1-net|g" \
  -e "s|<CURRENT-PATH>|${CURRENT_PATH}|g" \
  -e "s|<PROJECT-CERTS>|${CURRENT_PATH}/workspace/deep-kmeans/cert|g" \
  -e "s|<PROJECT-CACERTS>|${CURRENT_PATH}/workspace/deep-kmeans/cert/ca/capath|g" \
  -e "s|<LICENSE-SERVER-ADDRESS>|${APLS_IP}|g" \
  workspace/deep-kmeans/swop/swop1_profile.yaml

# Set apisrv host to the SN container name
sed -i "/apisrv/,/port/{s|host : ~|host : sn1|}" \
  workspace/deep-kmeans/swop/swop1_profile.yaml
```

### 6. Start APLS (if not already running)

```bash
docker run -d --name apls --restart=unless-stopped \
  --network host-1-net \
  -v apls-data:/var/lib/autopass/apls \
  hub.myenterpriselicense.hpe.com/hpe_eval/autopass/apls:9.19
```

### 7. Start the Sentinel Network node

```bash
./scripts/bin/run-sn \
  --name=sn1 --network=host-1-net \
  --host-ip=sn1 --sentinel \
  --sn-api-port=30304 \
  --key=workspace/deep-kmeans/cert/sn-1-key.pem \
  --cert=workspace/deep-kmeans/cert/sn-1-cert.pem \
  --capath=workspace/deep-kmeans/cert/ca/capath \
  --apls-ip ${APLS_IP}
```

### 8. Start the SWOP node

```bash
./scripts/bin/run-swop \
  --name=swop1 --network=host-1-net \
  --usr-dir=workspace/deep-kmeans \
  --profile-file-name=swop/swop1_profile.yaml \
  --key=workspace/deep-kmeans/cert/swop-1-key.pem \
  --cert=workspace/deep-kmeans/cert/swop-1-cert.pem \
  --capath=workspace/deep-kmeans/cert/ca/capath \
  -e http_proxy= -e https_proxy= \
  --apls-ip ${APLS_IP}
```

### 9. Run SWCI to orchestrate training

```bash
./scripts/bin/run-swci \
  --rm --name=swci1 --network=host-1-net \
  --usr-dir=workspace/deep-kmeans/swci \
  --init-script-name=swci-init \
  --key=workspace/deep-kmeans/cert/swci-1-key.pem \
  --cert=workspace/deep-kmeans/cert/swci-1-cert.pem \
  --capath=workspace/deep-kmeans/cert/ca/capath \
  -e http_proxy= -e https_proxy= \
  --apls-ip ${APLS_IP}
```

SWCI will automatically:
1. Build the `user-env-tf2.7.0-dkm` Docker image (TF 2.7 + scikit-learn + Swarm client)
2. Launch SL + ML container pairs, one per node
3. Run Phase 1 pretrain independently on each node, then Phase 2 federated joint training
4. Sync weights across nodes ~2 times per epoch via `SwarmCallback`

Training duration: ~30–45 minutes on CPU for 30 pretrain + 30 joint epochs.

### 10. Monitor training

Training output is captured to `data-and-scratch{N}/startup.log` on the host (persists after containers exit):

```bash
tail -f workspace/deep-kmeans/data-and-scratch1/startup.log
```

Training is complete when you see:
```
All peers and Swarm training rounds finished. Final Swarm model was loaded.
Phase 2 training done!
Saved encoder and centroids to scratch/
```

### 11. Evaluate

```bash
cd examples/deep-kmeans/model
for i in 1 2 3 4; do
  echo "=== Node $i ==="
  python3 evaluate.py \
    --scratch-dir /path/to/workspace/deep-kmeans/data-and-scratch${i}/scratch \
    --data-dir    /path/to/workspace/deep-kmeans/data-and-scratch${i}/app-data \
    --test-file   KDDTest+.txt
done
```

Reports binary detection accuracy (normal vs. attack), attack recall, false positive rate, and NMI for each node.

## Standalone (No Swarm Infrastructure)

```bash
cd examples/deep-kmeans/model

DATA_DIR=/path/to/data-and-scratch1/app-data \
SCRATCH_DIR=/tmp/dkm-scratch \
TRAIN_FILE=KDDTrain+.txt \
python3 standalone_run.py
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATA_DIR` | `app-data` | Directory inside the container containing training data |
| `SCRATCH_DIR` | `scratch` | Output directory for saved model and logs |
| `TRAIN_FILE` | `KDDTrain+.txt` | Training file name inside DATA_DIR |
| `PRETRAIN_EPOCHS` | `30` | Phase 1 local autoencoder epochs |
| `MAX_EPOCHS` | `30` | Phase 2 federated joint-training epochs |
| `MIN_PEERS` | `2` | Minimum peers for SwarmCallback to proceed |
| `N_CLUSTERS` | `5` | Number of internal clusters (tunable) |
| `LATENT_DIM` | `10` | Encoder output / embedding dimension |
| `LAMBDA_COEFF` | `0.5` | Weight of clustering (KLD) loss relative to reconstruction (MSE) |

## Output Artefacts

After training, each node's `data-and-scratch{N}/scratch/` contains:

| File | Description |
|---|---|
| `deep-kmeans_encoder.keras` | Trained encoder (TF 2.7 HDF5 format) |
| `deep-kmeans_centroids.npy` | Cluster centroid matrix (K × latent_dim) |
| `startup.log` | Full training log from the container |
| `training_error.log` | Traceback if Phase 2 crashed (only present on failure) |

> **Note:** The `.keras` file is saved by TF 2.7 as HDF5, not as the Keras 3 zip format. `evaluate.py` handles this automatically; if loading manually with a newer Keras version, rename the file to `.h5` first.

## Dataset

**NSL-KDD** — 41-feature network traffic records, 5 traffic categories:
`normal`, `dos`, `probe`, `r2l`, `u2r`

Preprocessing produces **122 features**: 3 categorical columns (protocol, service, flag) one-hot encoded with fixed category lists (3 + 70 + 11 = 84 binary features) + 38 numeric columns standardised. Fixed lists are hardcoded in `autoencoder.py` so all nodes produce identical feature shapes — required for federated weight averaging.

Node splits are non-IID to simulate real-world data heterogeneity:

| Node | Rows | Dominant traffic |
|------|------|-----------------|
| 1 | 20,000 | 70% normal |
| 2 | 19,447 | 67% DoS |
| 3 | 13,256 | 55% probe |
| 4 | 15,000 | 67% normal |

To regenerate splits from the full NSL-KDD archive:
```bash
python3 data-prep/prepare_data.py --input KDDTrain+_full.txt --nodes 4
```

## Results

Results from a 4-node federated run (30 pretrain + 30 joint epochs, λ=0.5, single host, CPU only). All nodes produce **identical results** after federated weight averaging — this confirms the federation protocol is working correctly.

### Binary Anomaly Detection (Normal vs. Attack)

The primary evaluation metric is binary detection: does the model correctly identify traffic as **normal** or **not normal**? An attack sample classified into any non-normal cluster is a successful detection.

| Metric | Value |
|--------|-------|
| Binary Detection Accuracy | **78.7%** |
| Normal Precision (normal traffic correctly kept as normal) | **91.5%** |
| False Positive Rate (normal traffic misclassified as attack) | **8.5%** |
| Attack Recall (attack traffic flagged as not-normal) | **68.9%** |

Evaluation set: KDDTest+ (22,544 samples — 9,711 normal, 12,831 attack across DoS, probe, r2l, u2r families).

Per-attack-family detection:

| Attack Family | Samples | Flagged as Attack | Detection Rate |
|---------------|---------|-------------------|----------------|
| DoS | 7,458 | 5,735 | 76.9% |
| Probe | 2,421 | 2,240 | 92.5% |
| R2L | 2,885 | 831 | 28.8% |
| U2R | 67 | 42 | 62.7% |

DoS and Probe attacks are strongly detected. R2L attacks (remote-to-local exploits) involve individual connections that can closely resemble normal traffic, making them harder to separate in the latent space without labeled supervision.

### How It Works at Inference

The federated encoder maps any traffic sample to a 10-dimensional latent vector. The ClusteringLayer computes soft assignment scores (Student-t distribution) to each of the K=5 learned cluster centroids. The cluster whose centroid was learned predominantly from normal traffic acts as the "normal" reference. Any sample that soft-assigns predominantly to a different cluster is flagged as anomalous.

This means the system does **not** need to know in advance what attack traffic looks like — it only needs to learn what normal looks like, which is precisely what the reconstruction loss (Phase 1) optimises for.

## Known Issues and Design Decisions

**Functional API required for SwarmCallback:** TF 2.7's `SwarmCallback` collects weight names via `model.layers` and asserts they match `model.get_weights()`. Subclassed models with metric trackers as attributes cause a count mismatch (`AssertionError`). This example uses the Functional API throughout.

**Single `fit()` call for all epochs:** `SwarmCallback` fires `on_train_end` once per `fit()` call, which signals the SL that training is complete. Calling `fit()` in a loop (one call per epoch) causes the SL to shut down after the first call. We use a `keras.utils.Sequence` generator to update the target distribution `P` every 5 epochs while keeping a single `fit()` call.

**Contract reset between runs:** Failed runs leave `trainingOver: true` in the Swarm blockchain, causing subsequent runs to fail with "Admin not found". The `swci-init` script resets the contract (`RESET CONTRACT defaultbb.cqdb.sml.hpe`) before each training run.

**`apisrv` host in SWOP profile:** Must be set to the SN container hostname (`sn1`); the placeholder `~` causes SWOP to fail with "Missing apisrv host".

## References

- Fard, M. M., Thonet, T., & Gaussier, E. (2020). *Deep k-Means: Jointly Clustering with k-Means and Learning Representations.* Pattern Recognition Letters. [arXiv:1806.10069](https://arxiv.org/abs/1806.10069)
- [HPE Swarm Learning GitHub](https://github.com/HewlettPackard/swarm-learning)
- [NSL-KDD Dataset](https://www.unb.ca/cic/datasets/nsl.html)
