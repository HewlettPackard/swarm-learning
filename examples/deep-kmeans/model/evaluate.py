"""
Evaluate the trained Deep K-Means NSL-KDD model.

Loads encoder + centroids saved by autoencoder.py, preprocesses KDDTest+.txt,
and reports NMI, clustering accuracy (Hungarian match), and per-class breakdown.

Usage:
  python3 evaluate.py [--scratch-dir DIR] [--data-dir DIR] [--test-file FILE]
"""

import os
import argparse
import numpy as np
import tensorflow as tf
from sklearn.metrics import normalized_mutual_info_score, accuracy_score
from sklearn.preprocessing import LabelEncoder
from scipy.optimize import linear_sum_assignment
from autoencoder import ClusteringLayer, load_and_preprocess

BATCH_SIZE = 512


def load_encoder_and_centroids(scratch_dir):
    import shutil
    model_base = os.path.join(scratch_dir, 'deep-kmeans')
    keras_path = model_base + '_encoder.keras'
    h5_path    = model_base + '_encoder.h5'

    custom = {'ClusteringLayer': ClusteringLayer}
    if os.path.exists(keras_path):
        # TF 2.7 (container) saves .keras as HDF5; local Keras 3 expects zip.
        # Try native load first, then fall back to copying as .h5 for h5py.
        try:
            encoder = tf.keras.models.load_model(keras_path, custom_objects=custom)
        except Exception:
            tmp = keras_path + '.tmp.h5'
            shutil.copy2(keras_path, tmp)
            try:
                encoder = tf.keras.models.load_model(tmp, custom_objects=custom)
            finally:
                try: os.remove(tmp)
                except OSError: pass
    elif os.path.exists(h5_path):
        encoder = tf.keras.models.load_model(h5_path, custom_objects=custom)
    else:
        raise FileNotFoundError(f'No encoder model found in {scratch_dir}')

    centroids = np.load(model_base + '_centroids.npy')
    return encoder, centroids


def hungarian_match(y_pred, y_true, n_true_classes):
    """Map cluster IDs to true class IDs via the Hungarian algorithm.

    Works when K > n_true_classes by padding the confusion matrix to square.
    """
    n_pred_clusters = int(y_pred.max()) + 1
    n = max(n_pred_clusters, n_true_classes)
    confusion = np.zeros((n, n), dtype=int)
    for p, t in zip(y_pred, y_true):
        confusion[p][t] += 1
    row_ind, col_ind = linear_sum_assignment(-confusion)
    mapping = {r: c for r, c in zip(row_ind, col_ind)}
    return np.array([mapping.get(p, 0) for p in y_pred])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scratch-dir', default=os.getenv('SCRATCH_DIR', '/tmp/deep-kmeans-scratch'))
    parser.add_argument('--data-dir',    default=os.getenv('DATA_DIR',    '/platform/data'))
    parser.add_argument('--test-file',   default='KDDTest+.txt')
    args = parser.parse_args()

    print('Loading model artefacts...')
    encoder, centroids = load_encoder_and_centroids(args.scratch_dir)
    print(f'  Encoder loaded | Centroids shape: {centroids.shape}')

    print('\nLoading test data...')
    X_test, y_test_raw = load_and_preprocess(args.data_dir, args.test_file)

    le = LabelEncoder()
    y_true = le.fit_transform(y_test_raw)
    print(f'  True classes: {le.classes_}')

    print('\nGetting cluster assignments...')
    z = encoder.predict(X_test, batch_size=BATCH_SIZE, verbose=0)
    diff = z[:, np.newaxis, :] - centroids[np.newaxis, :, :]
    dist_sq = np.sum(diff ** 2, axis=2)
    q = 1.0 / (1.0 + dist_sq)
    q = q / q.sum(axis=1, keepdims=True)
    cluster_assignments = np.argmax(q, axis=1)

    n_classes = len(le.classes_)
    matched = hungarian_match(cluster_assignments, y_true, n_classes)

    nmi = normalized_mutual_info_score(y_true, cluster_assignments)
    acc = accuracy_score(y_true, matched)

    # Binary detection: normal vs. attack
    # The cluster Hungarian-matched to "normal" is treated as the "normal" cluster;
    # all other clusters are treated as "attack". This is the practically useful metric
    # because the system needs only to flag traffic as normal or suspicious.
    normal_idx = le.transform(['normal'])[0] if 'normal' in le.classes_ else -1
    # Find which cluster was mapped to the "normal" class
    row_ind, col_ind = linear_sum_assignment(
        -np.array([[np.sum((cluster_assignments == r) & (y_true == c))
                    for c in range(n_classes)]
                   for r in range(int(cluster_assignments.max()) + 1)])
    )
    normal_cluster = next((r for r, c in zip(row_ind, col_ind) if c == normal_idx), None)

    y_bin_pred = np.where(cluster_assignments == normal_cluster, 0, 1)
    y_bin_true = np.where(y_true == normal_idx, 0, 1)
    binary_acc = accuracy_score(y_bin_true, y_bin_pred)
    tp = np.sum((y_bin_pred == 1) & (y_bin_true == 1))
    tn = np.sum((y_bin_pred == 0) & (y_bin_true == 0))
    fp = np.sum((y_bin_pred == 1) & (y_bin_true == 0))
    fn = np.sum((y_bin_pred == 0) & (y_bin_true == 1))
    attack_recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    normal_precision = tn / (tn + fp) if (tn + fp) > 0 else 0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0

    print(f"\n{'='*70}")
    print(f'RESULTS ON TEST SET ({len(X_test):,} rows)')
    print(f"{'='*70}")
    print(f'Binary Detection Accuracy (normal vs. attack): {binary_acc*100:.1f}%')
    print(f'  Attack Recall   (attacks flagged as not-normal): {attack_recall*100:.1f}%')
    print(f'  Normal Precision (normal traffic kept as normal): {normal_precision*100:.1f}%')
    print(f'  False Positive Rate (normal misclassified as attack): {false_positive_rate*100:.1f}%')
    print(f'NMI  (Normalized Mutual Information): {nmi:.4f}')
    print(f"{'='*70}")

    print('\nPer-class count:')
    print(f"{'True Label':<12} {'Count':>8} {'Predicted Not-Normal':>22}")
    print('-' * 44)
    for i, cls in enumerate(le.classes_):
        mask = y_true == i
        total = mask.sum()
        flagged = np.sum(y_bin_pred[mask] == 1)
        print(f'{cls:<12} {total:>8,} {flagged:>22,}')

    print(f"\n{'='*70}")
    print('EVALUATION COMPLETE')
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
