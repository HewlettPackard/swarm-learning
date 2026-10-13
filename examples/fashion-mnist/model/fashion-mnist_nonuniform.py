############################################################################
## (C)Copyright 2026 Hewlett Packard Enterprise Development LP
## Licensed under the Apache License, Version 2.0 (the "License"); you may
## not use this file except in compliance with the License. You may obtain
## a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations
## under the License.
############################################################################
import os
import json
import time
import numpy as np
import tensorflow as tf
from collections import deque
from sklearn.metrics import f1_score

# Standard TensorFlow Privacy utility library path
from tensorflow_privacy.privacy.analysis.compute_dp_sgd_privacy_lib import compute_dp_sgd_privacy
from swarmlearning.tf import SwarmCallback

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURABLE PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

batchSize = 32            # Fixed mini-batch size for both standard training and DP microbatching
defaultMaxEpoch = 50       # Fallback value if the MAX_EPOCHS environment variable is not set
defaultMinPeers = 2        # Fallback minimum peer count required for SwarmCallback to initiate a sync round

# ─────────────────────────────────────────────────────────────────────────────
# MODEL PARAMETER-BASED COUPLING LAYER
# ─────────────────────────────────────────────────────────────────────────────

class ConvergenceFlagLayer(tf.keras.layers.Layer):
    """
    Wraps a dummy, non-trainable weight within a Keras Layer so it is exposed
    under model.layers -> layer.weights. This aligns with how Swarm Learning's
    SwarmCallback enumerates weightNames. 
    
    Because call(x) passes x through unchanged, appending this layer to a 
    Sequential model preserves all predictions and metrics while establishing 
    a cross-host communication channel via standard weight-merging mechanisms.

    NOTE: This consensus mechanism relies on SwarmCallback's mergeMethod='mean'
    correctly averaging non-trainable weights along with trainable ones. If 
    SwarmCallback is modified to only merge trainable variables, this flag 
    will remain isolated at each node's local value, and global quorum will 
    never be detected.
    """
    def __init__(self):
        super().__init__(name="convergence_flag_layer")
        # Single scalar weight initialized to 0.0. Each node updates its local
        # copy to 1.0 upon achieving local convergence (see CascadedDPCallback).
        # Since SwarmCallback averages weights across peers, this scalar functions
        # as a distributed vote: the merged value reaches 1.0 only when all 
        # participating peers have voted, enabling decentralized quorum detection.
        self.flag = self.add_weight(
            name="convergence_flag",
            shape=(1,),
            initializer="zeros",
            trainable=False,   # Excludes this parameter from gradient calculations
        )

    def call(self, x):
        # Pass-through operation: This layer retains state without altering 
        # model activations, ensuring network outputs remain unaffected.
        return x

# ─────────────────────────────────────────────────────────────────────────────
# DECENTRALIZED CASCADED DP CALLBACK (SWARM PARAMETER CONSENSUS)
# ─────────────────────────────────────────────────────────────────────────────

class CascadedDPCallback(tf.keras.callbacks.Callback):
    """
    Monitors local training dynamics at the end of each epoch to determine when 
    DP noise is no longer required (i.e., when gradients flatten and validation 
    accuracy plateaus). It leverages the swarm-averaged ConvergenceFlagLayer 
    to ensure global consensus across all nodes before disabling DP and 
    recompiling the model with a standard, non-private optimizer.
    """
    def __init__(self, val_ds, node_id, num_nodes, flag_layer, optimizer_type='sgd', 
                 learning_rate=0.01, window_size=5, grad_threshold=0.01, 
                 acc_threshold=0.0005, min_dp_epochs=5):
        super().__init__()
        self.val_ds = val_ds                              # Held-out dataset used for gradient-norm evaluation and convergence verification
        self.node_id = node_id                             # Current node index, utilized for logging purposes
        self.num_nodes = num_nodes                         # Total number of peers; used to map the averaged flag value to a vote consensus
        self.flag_layer = flag_layer                       # Shared non-trainable weight synchronized via SwarmCallback weight-merging
        self.optimizer_type = optimizer_type               # Target optimizer architecture ('sgd' or 'adam') to use post-DP
        self.learning_rate = learning_rate                 # Learning rate applied to the standard optimizer after DP is disabled
        self.window_size = window_size                     # Rolling window size (epochs) for tracking gradient-norm means and accuracy variance
        self.grad_threshold = grad_threshold               # Fixed absolute threshold on epoch-to-epoch rolling grad-norm slope
        self.acc_threshold = acc_threshold                 # Fixed absolute threshold on windowed validation-accuracy variance
        self.min_dp_epochs = min_dp_epochs                 # Enforced minimum DP training epochs before convergence checks begin

        self.grad_norm_window = deque(maxlen=window_size)   # Rolling buffer for per-epoch gradient norms
        self.acc_window = deque(maxlen=window_size)          # Rolling buffer for per-epoch validation accuracy
        self.grad_history = []                               # Complete history of raw gradient norms
        self.rolling_history = []                            # Complete history of windowed rolling mean gradient norms
        self.acc_history = []                                 # Complete history of validation accuracy scores
        self.dp_active = True                                 # Flag tracking whether differential privacy is currently enabled
        self.dp_drop_epoch = None                             # Tracked epoch (1-indexed) where DP was disabled (used for epsilon accounting)
        self.dp_drop_reason = None                            # Metadata snapshot capturing the specific metrics that triggered the DP transition
        self.local_converged = False                          # State guard preventing redundant updates to the local flag weight

        # Dedicated loss function instance for tracking gradient magnitudes without impacting training loss
        self._measure_loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)

    def _compute_grad_norm(self):
        """
        Samples the current gradient magnitude across a small subset of validation 
        batches to extract a metric indicating total model updates. The result is 
        averaged over 5 batches to mitigate transient batch noise. training=True is 
        explicitly set to ensure regularization layers match training behavior.
        """
        norms = []
        for x, y in self.val_ds.take(5):
            with tf.GradientTape() as tape:
                preds = self.model(x, training=True)
                loss_val = self._measure_loss(y, preds)
            grads = tape.gradient(loss_val, self.model.trainable_variables)
            grad_norm = tf.linalg.global_norm(grads).numpy()
            norms.append(float(grad_norm))
        return float(np.mean(norms))

    def _drop_dp(self, epoch):
        """
        Invoked upon reaching a global swarm quorum. Swaps the active DP optimizer 
        for a standard alternative and forces Keras to recompile its internal 
        execution graphs, clearing the cached DP microbatching step tracking functions.
        """
        print(f"\n***** CascadedDP: [Node {self.node_id}] SWARM PARAMETER QUORUM UNLOCKED *****")
        print(f"***** CascadedDP: dropping DP globally at epoch {epoch + 1} *****")

        # Instantiate a standard, non-private optimizer version matching the run configuration
        if self.optimizer_type == 'adam':
            new_optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        else:
            new_optimizer = tf.keras.optimizers.SGD(learning_rate=self.learning_rate, momentum=0.9, nesterov=True)

        # Recompile the model with a fresh optimizer state, resetting loss back to standard 
        # categorical cross-entropy rather than the unreduced variant required for DP microbatching.
        self.model.compile(loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False),
                           optimizer=new_optimizer,
                           metrics=[tf.keras.metrics.CategoricalAccuracy(name='accuracy')])

        # Explicitly clear cached execution graphs to ensure the new training loop updates 
        # reflect the newly attached standard optimizer configuration.
        if hasattr(self.model, 'train_function'):
            self.model.train_function = None
            self.model.test_function = None
            self.model.predict_function = None
            for x_sample, y_sample in self.val_ds.take(1):
                self.model.make_train_function()
                self.model.make_test_function()
                self.model.make_predict_function()

        self.dp_active = False
        self.dp_drop_epoch = epoch + 1
        
        # Capture precise snapshot metrics for output logging and diagnostic validation
        self.dp_drop_reason = {
            "epoch": epoch + 1,
            "grad_threshold": self.grad_threshold,
            "acc_threshold": self.acc_threshold,
            "rolling_mean": float(np.mean(self.grad_norm_window)),
            "val_acc_window": list(self.acc_window)
        }

        print(f"***** CascadedDP: low-level execution graphs forcefully rebuilt *****")
        print(f"***** CascadedDP: model recompiled with standard optimizer *****\n")

    def on_epoch_end(self, epoch, logs=None):
        # Terminate evaluation tracking if this local node has already successfully transitioned away from DP
        if not self.dp_active: return

        val_acc = (logs or {}).get('val_accuracy')
        if val_acc is None: return

        # Advance local metrics: Monitor tracking stability for both gradient norms and target accuracy
        grad_norm = self._compute_grad_norm()
        self.grad_norm_window.append(grad_norm)
        self.acc_window.append(val_acc)
        self.grad_history.append(float(grad_norm))
        
        rolling_mean = float(np.mean(self.grad_norm_window))
        self.rolling_history.append(rolling_mean)
        self.acc_history.append(float(val_acc))

        print(
            f"  [CascadedDP] Node={self.node_id} | epoch={epoch + 1} | "
            f"grad_norm={grad_norm:.6f} | rolling_mean={rolling_mean:.6f} | val_acc={val_acc:.4f}"
        )

        # Burn-in Phase: Skip convergence checks until the minimum DP epoch count has elapsed
        if epoch + 1 <= self.min_dp_epochs:
            return

        # Enforce evaluation constraints until rolling windows match configured sizing definitions
        if len(self.grad_norm_window) < self.window_size: return

        # Read the current swarm consensus weight state. This evaluates cross-host sync changes 
        # from preceding intervals rather than capturing un-merged local modifications. 
        # Note: If data splits across nodes are highly skewed (e.g., Dirichlet splits), 
        # the flag represents a weighted data-fraction rather than an absolute node headcount.
        global_flag_value = float(self.flag_layer.flag.numpy()[0])
        print(f"  [CascadedDP-Quorum] Node {self.node_id} tracking global weighted flag value: "
              f"{global_flag_value:.4f} (this is a weightage-weighted average, not a literal node count; "
              f"only == 1.0 implies every node has actually converged)")

        # Evaluate complete swarm consensus. A value threshold of 0.999 is applied to avoid floating-point rounding issues.
        if global_flag_value >= 0.999:
            self._drop_dp(epoch)
            return

        # Calculate absolute slope variance across recent sliding windows relative to baseline boundaries
        grad_slope = abs(self.rolling_history[-2] - self.rolling_history[-1]) if len(self.rolling_history) >= 2 else float('inf')
        acc_variance = float(np.var(self.acc_window))

        slope_trigger = grad_slope < self.grad_threshold
        plateau_trigger = acc_variance < self.acc_threshold

        # Log active telemetry indicators mapping current convergence states
        print(
            f"  [CascadedDP-Trigger] Node={self.node_id} | epoch={epoch + 1} | "
            f"grad_slope={grad_slope:.6f} (thresh {self.grad_threshold:.6f}, {'PASS' if slope_trigger else 'fail'}) | "
            f"acc_variance={acc_variance:.8f} (thresh {self.acc_threshold:.8f}, {'PASS' if plateau_trigger else 'fail'}) | "
            f"local_converged={self.local_converged}"
        )

        # Update local tracking flags. Since incoming Swarm updates continually overwrite 
        # tracking metrics, nodes must continuously reaffirm their local convergence status 
        # until a global sync acknowledges completion.
        if slope_trigger and plateau_trigger:
            self.local_converged = True

        if self.local_converged:
            self.flag_layer.flag.assign([1.0])
            print(f"  [CascadedDP-Consensus] Node {self.node_id} re-asserting local flag = 1.0 "
                  f"(local_converged={self.local_converged})")
        else:
            # Without this, a merge round overwrites this node's flag with the
            # partially-merged value (e.g. 0.5), and since local_converged is
            # still False nothing corrects it back down. The next merge then
            # averages that stale, already-inflated value against a converged
            # peer's 1.0, producing a creeping 0.5 -> 0.75 -> 0.875 -> ...
            # sequence that eventually crosses quorum on its own, even though
            # this node never actually satisfied the convergence triggers.
            # Re-asserting 0.0 every epoch keeps this node's true (unconverged)
            # vote intact through every merge round.
            self.flag_layer.flag.assign([0.0])
            print(f"  [CascadedDP-Consensus] Node {self.node_id} re-asserting local flag = 0.0 "
                  f"(local_converged={self.local_converged})")

# ─────────────────────────────────────────────────────────────────────────────
# FLAG-VALUE OBSERVER (Diagnostic callback utility)
# ─────────────────────────────────────────────────────────────────────────────

class FlagObserverCallback(tf.keras.callbacks.Callback):
    """
    Registered immediately after SwarmCallback to intercept updates during 
    on_train_batch_end, providing clear auditing info when swarm weight values shift.
    """
    def __init__(self, flag_layer, node_id):
        super().__init__()
        self.flag_layer = flag_layer
        self.node_id = node_id
        self._last_seen = None

    def on_train_batch_end(self, batch, logs=None):
        current = float(self.flag_layer.flag.numpy()[0])
        if self._last_seen is None or abs(current - self._last_seen) > 1e-9:
            print(f"  [FlagObserver] Node={self.node_id} | batch={batch} | "
                  f"flag changed: {self._last_seen} -> {current}")
            self._last_seen = current


def main():
    modelName = 'fashion-mnist'
    maxEpoch = int(os.getenv('MAX_EPOCHS', str(defaultMaxEpoch)))          # Enforced global training limit
    minPeers = int(os.getenv('MIN_PEERS', str(defaultMinPeers)))            # Minimum peers needed to proceed with updates
    dpEnabled = os.getenv('DP_ENABLED', 'false').lower() == 'true'          # Toggle switch specifying DP-SGD activation status
    noiseMultiplier = float(os.getenv('NOISE_MULTIPLIER', '0.0'))           # Magnitude of Gaussian noise added during DP steps
    l2NormClip = float(os.getenv('L2_NORM_CLIP', '1.0'))                    # Maximum clipping threshold for individual example gradients
    microbatches = int(os.getenv('MICROBATCHES', str(batchSize)))           # Number of distinct chunks used for gradient evaluation splits
    optimizerType = os.getenv('OPTIMIZER', 'sgd').lower()                   # Network optimizer configuration choice ('sgd' vs 'adam')
    learningRate = float(os.getenv('LEARNING_RATE', '0'))                   # Custom target learning rate setting override
    actual_lr = learningRate or (0.001 if optimizerType == 'adam' else 0.01)
    cascadedDp = os.getenv('CASCADED_DP', 'false').lower() == 'true'        # Toggle for the adaptive convergence-driven DP drop system
    dpDropWindow = int(os.getenv('DP_DROP_WINDOW', '5'))                    # Target tracking epoch window for convergence logic
    minDpEpochs = int(os.getenv('MIN_DP_EPOCHS', '5'))                      # Absolute minimum duration window required for initial DP steps
    gradThreshold = float(os.getenv('GRAD_THRESHOLD', '0.01'))               # Fixed absolute grad-norm slope threshold for convergence
    accThreshold = float(os.getenv('ACC_THRESHOLD', '0.0005'))               # Fixed absolute val-accuracy variance threshold for convergence
    nodeId = int(os.getenv('NODE_ID', '0'))                                 # Designated identification position index for this worker node
    numNodes = int(os.getenv('NUM_NODES', '2'))                             # Quantified total membership capacity of participating network nodes

    print('***** Starting model =', modelName)
    print('-' * 64)

    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.fashion_mnist.load_data()

    # ── PARTITIONING LOGIC ──
    # Enforce standard reproducibility keys across dataset shards
    rng = np.random.default_rng(seed=42)
    alpha_env = os.getenv('DIRICHLET_ALPHA', 'inf').lower()

    if alpha_env == 'inf':
        # Default IID strategy configuration: Uniform partition across available participants
        partitionMode = 'iid'
        perm = rng.permutation(len(x_train))
        x_train, y_train = x_train[perm], y_train[perm]
        split_size = len(x_train) // numNodes

        # Sample count for every node (last node gets the remainder), used
        # below to size syncFrequency off the smallest shard.
        all_node_sample_counts = [split_size if n != numNodes - 1 else (len(x_train) - split_size * (numNodes - 1)) for n in range(numNodes)]
        
        # Allocate any division remainders to the final node to prevent data loss
        start, end = nodeId * split_size, (len(x_train) if nodeId == numNodes - 1 else (nodeId + 1) * split_size)
        x_train, y_train = x_train[start:end], y_train[start:end]
        
        # Establish equal baseline weightage partitions under uniform conditions
        nodeWeightage = round(100 / numNodes)
        print(f"***** partition_mode=iid | node={nodeId}")
        print(f"***** Dynamic Node Weight Assignment: Node {nodeId} Weightage = {nodeWeightage}%")
        print(f"***** partition_mode=iid | node={nodeId} | samples={len(x_train)}")
        for class_index in range(10):
            count = int(np.sum(y_train == class_index))
            if count > 0:
                print(f"      Class {class_index:2d}: {count:5d}")
    else:
        # Non-IID Dirichlet distribution strategy mapping for heterogeneous data setups
        partitionMode = 'non_iid'
        alpha = float(alpha_env)
        node_idx = [[] for _ in range(numNodes)]
        for class_index in range(10):
            idx = np.where(y_train == class_index)[0]
            rng.shuffle(idx)
            proportions = rng.dirichlet(alpha=np.full(numNodes, alpha))
            splits = (proportions * len(idx)).astype(int)
            
            # Resolve rounding inconsistencies to guarantee exhaustive sample tracking
            splits[-1] = len(idx) - splits[:-1].sum()
            bounds = np.concatenate([[0], np.cumsum(splits)])
            for n in range(numNodes): node_idx[n].extend(idx[bounds[n]:bounds[n+1]])
        
        # Sample count for every node, used below to size syncFrequency off
        # the smallest shard (the most heterogeneous node's data volume).
        all_node_sample_counts = [len(node_idx[n]) for n in range(numNodes)]

        # Compute exact regional scaling attributes matching local slice distribution
        total = sum(len(node_idx[n]) for n in range(numNodes))
        nodeWeightage = int(round(100 * len(node_idx[nodeId]) / total))
        final_idx = np.array(node_idx[nodeId])
        rng.shuffle(final_idx)
        x_train, y_train = x_train[final_idx], y_train[final_idx]
        print(f"***** partition_mode=dirichlet (Dirichlet alpha={alpha_env}) | node={nodeId}")
        print(f"***** Dynamic Node Weight Assignment: Node {nodeId} Weightage = {nodeWeightage}%")
        print(f"***** partition_mode=dirichlet | node={nodeId} | samples={len(x_train)}")
        for class_index in range(10):
            count = int(np.sum(y_train == class_index))
            if count > 0:
                print(f"      Class {class_index:2d}: {count:5d}")

    x_train, x_test = x_train / 255.0, x_test / 255.0   # Scale pixels directly to the [0, 1] range
    num_train_samples = len(x_train)
    y_train_cat = tf.keras.utils.to_categorical(y_train, 10)  # Generate standard one-hot target matrices
    y_test_cat = tf.keras.utils.to_categorical(y_test, 10)

    # syncFrequency is set to the smallest node's batches-per-epoch (min
    # sample count across all nodes // batchSize, matching drop_remainder),
    # so every node syncs at least once per epoch even at its most
    # heterogeneous/smallest shard, with a floor of 1 to stay valid.
    min_node_samples = min(all_node_sample_counts)
    syncFrequency = max(1, min_node_samples // batchSize)
    print(f"***** Dynamic syncFrequency = {syncFrequency} (derived from smallest node shard = {min_node_samples} samples)")

    # Initialize the tracking layer instance before compilation to ensure shared reference integrity
    flag_layer = ConvergenceFlagLayer()

    # Standard CNN configuration structure typically utilized for DP-SGD validation
    model = tf.keras.models.Sequential([
        tf.keras.layers.Reshape((28, 28, 1), input_shape=(28, 28)),
        tf.keras.layers.Conv2D(16, 8, strides=2, padding='same', activation='relu'),
        tf.keras.layers.MaxPool2D(2, 1),
        tf.keras.layers.Conv2D(32, 4, strides=2, padding='valid', activation='relu'),
        tf.keras.layers.MaxPool2D(2, 1),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax'),
        flag_layer  # Intercepted into structural attributes for Swarm parameter processing
    ])

    if dpEnabled:
        # DP-SGD Pipeline configurations: Enforce constraints via per-example optimization structures
        from tensorflow_privacy.privacy.optimizers.dp_optimizer_keras import DPKerasAdamOptimizer, DPKerasSGDOptimizer
        optimizer = (DPKerasAdamOptimizer if optimizerType == 'adam' else DPKerasSGDOptimizer)(
            l2_norm_clip=l2NormClip, noise_multiplier=noiseMultiplier, 
            num_microbatches=microbatches, learning_rate=actual_lr)
        # Require unreduced loss evaluation mechanics to process isolated sample instances
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False, reduction=tf.keras.losses.Reduction.NONE)
        print(f"***** Using DP-{'Adam' if optimizerType == 'adam' else 'SGD'} optimizer")
    else:
        optimizer = tf.keras.optimizers.Adam(learning_rate=actual_lr) if optimizerType == 'adam' else tf.keras.optimizers.SGD(learning_rate=actual_lr, momentum=0.9, nesterov=True)
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
        print(f"***** Using standard {'Adam' if optimizerType == 'adam' else 'SGD'} optimizer")

    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train_cat)).shuffle(num_train_samples).batch(batchSize, drop_remainder=True).prefetch(tf.data.AUTOTUNE)
    val_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test_cat)).batch(batchSize).prefetch(tf.data.AUTOTUNE)

    # Initialize primary Swarm parameters controlling sync updates across structural loops
    callbacks = [SwarmCallback(syncFrequency=syncFrequency, useAdaptiveSync=False, minPeers=minPeers, adsValData=val_ds, adsValBatchSize=batchSize, mergeMethod='mean', nodeWeightage=nodeWeightage, totalEpochs=maxEpoch)]
    callbacks.append(FlagObserverCallback(flag_layer, nodeId))
    
    cdp = None
    if dpEnabled and cascadedDp:
        # Initialize adaptive cascading optimization triggers if conditions are met
        cdp = CascadedDPCallback(val_ds, nodeId, numNodes, flag_layer, optimizerType, actual_lr, dpDropWindow, gradThreshold, accThreshold, minDpEpochs)
        callbacks.append(cdp)

    print('Starting training ...')
    train_start = time.time()
    model.fit(train_ds, epochs=maxEpoch, validation_data=val_ds, callbacks=callbacks)
    training_time = round(time.time() - train_start, 2)

    # Evaluation Sequence
    print('\nRunning final post-training evaluation on test dataset...')
    eval_res = model.evaluate(val_ds, verbose=0)
    y_true = np.concatenate([np.argmax(y, axis=1) for _, y in val_ds])
    y_pred = np.concatenate([np.argmax(model.predict_on_batch(x), axis=1) for x, _ in val_ds])
    
    eps = None
    if dpEnabled and noiseMultiplier > 0:
        print('-' * 64)
        print('***** PRIVACY REPORT *****')
        delta = 1.0 / num_train_samples
        dp_epochs = cdp.dp_drop_epoch if (cdp and cdp.dp_drop_epoch) else maxEpoch
        eps, _ = compute_dp_sgd_privacy(n=num_train_samples, batch_size=batchSize, noise_multiplier=noiseMultiplier, epochs=dp_epochs, delta=delta)
        print(f"Final Epsilon (ε): {eps:.4f} | Final Delta (δ): {delta:.2e}")
        print('-' * 64)

    results = {
        "config": {"model_name": modelName, "node_id": nodeId, "num_nodes": numNodes, "epochs": maxEpoch, "batch_size": batchSize, "optimizer": optimizerType, "learning_rate": actual_lr, "dp_enabled": dpEnabled, "cascaded_dp": cascadedDp, "l2_norm_clip": l2NormClip, "noise_multiplier": noiseMultiplier, "microbatches": microbatches, "partition_mode": partitionMode, "num_train_samples": num_train_samples},
        "performance": {"training_time_seconds": training_time, "final_test_loss": float(eval_res[0]), "final_test_accuracy": float(eval_res[1]), "final_test_f1_macro": float(f1_score(y_true, y_pred, average='macro'))},
        "privacy": {"epsilon": round(eps, 4) if eps is not None else None, "delta": 1.0/num_train_samples if dpEnabled else None, "dp_drop_epoch": cdp.dp_drop_epoch if cdp else None, "grad_threshold": gradThreshold, "acc_threshold": accThreshold, "dp_drop_reason": cdp.dp_drop_reason if cdp else None}
    }
    
    with open(f"/results/{os.getenv('RESULT_FILE', 'results.json')}", 'w') as f: json.dump(results, f, indent=2)
    print('Saved the trained model and verified final test metrics JSON!')

if __name__ == '__main__': main()
