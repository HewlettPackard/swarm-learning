"""
Inference and evaluation for the Deep K-Means NSL-KDD model.

Loads encoder + centroids saved by autoencoder.py, preprocesses KDDTrain+.txt
to identify the normal cluster, then evaluates on KDDTest+.txt.

Usage:
  python3 predict.py [--scratch-dir DIR] [--data-dir DIR]
"""

import os
import argparse
import numpy as np
import tensorflow as tf
from autoencoder import ClusteringLayer, load_and_preprocess

BATCH_SIZE = 512


# ---------------------------------------------------------------------------
# Load model artefacts
# ---------------------------------------------------------------------------
def load_model_artefacts(scratch_dir):
    model_base = os.path.join(scratch_dir, 'deep-kmeans')
    enc_path = model_base + '_encoder.keras'
    if not os.path.exists(enc_path):
        enc_path = model_base + '_encoder.h5'
    encoder = tf.keras.models.load_model(
        enc_path, custom_objects={'ClusteringLayer': ClusteringLayer},
    )
    centroids = np.load(model_base + '_centroids.npy')
    return encoder, centroids


# ---------------------------------------------------------------------------
# Inference helpers
# ---------------------------------------------------------------------------
def soft_assignments(encoder, centroids, X):
    z = encoder.predict(X, batch_size=BATCH_SIZE, verbose=0)
    diff = z[:, np.newaxis, :] - centroids[np.newaxis, :, :]
    dist_sq = np.sum(diff ** 2, axis=2)
    q = 1.0 / (1.0 + dist_sq)
    q = q / q.sum(axis=1, keepdims=True)
    return q


def identify_normal_cluster(encoder, centroids, X_train, y_train):
    q = soft_assignments(encoder, centroids, X_train)
    cluster_ids = np.argmax(q, axis=1)

    K = centroids.shape[0]
    print('\nCluster composition on training data:')
    print(f'  {"Cluster":>8} | {"Total":>7} | {"Normal%":>8} | '
          f'{"DoS%":>7} | {"Probe%":>7} | {"R2L%":>6} | {"U2R%":>6}')
    print('  ' + '-' * 65)

    normal_frac = np.zeros(K)
    for k in range(K):
        mask = cluster_ids == k
        if mask.sum() == 0:
            print(f'  {k:>8} | {"(empty)":>7}')
            continue
        cats = y_train[mask]
        n_total  = len(cats)
        n_normal = (cats == 'normal').sum()
        n_dos    = (cats == 'dos').sum()
        n_probe  = (cats == 'probe').sum()
        n_r2l    = (cats == 'r2l').sum()
        n_u2r    = (cats == 'u2r').sum()
        normal_frac[k] = n_normal / n_total
        print(f'  {k:>8} | {n_total:>7,} | {100*n_normal/n_total:>7.1f}% | '
              f'{100*n_dos/n_total:>6.1f}% | {100*n_probe/n_total:>6.1f}% | '
              f'{100*n_r2l/n_total:>5.1f}% | {100*n_u2r/n_total:>5.1f}%')

    normal_cluster = int(np.argmax(normal_frac))
    print(f'\n  → Normal cluster: {normal_cluster} '
          f'({100*normal_frac[normal_cluster]:.1f}% normal traffic)')
    return normal_cluster


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def evaluate(encoder, centroids, X_test, y_test, normal_cluster):
    q = soft_assignments(encoder, centroids, X_test)
    cluster_ids = np.argmax(q, axis=1)

    is_normal_gt   = y_test == 'normal'
    is_attack_gt   = ~is_normal_gt
    is_normal_pred = cluster_ids == normal_cluster
    is_attack_pred = ~is_normal_pred

    tp = int((is_attack_gt  & is_attack_pred).sum())
    tn = int((is_normal_gt  & is_normal_pred).sum())
    fp = int((is_normal_gt  & is_attack_pred).sum())
    fn = int((is_attack_gt  & is_normal_pred).sum())

    total          = len(y_test)
    accuracy       = (tp + tn) / total
    attack_recall  = tp / max(1, tp + fn)
    false_pos_rate = fp / max(1, fp + tn)

    print('\n' + '=' * 50)
    print('Evaluation on test set')
    print('=' * 50)
    print(f'  Total samples : {total:,}')
    print(f'  Normal (GT)   : {is_normal_gt.sum():,}')
    print(f'  Attack (GT)   : {is_attack_gt.sum():,}')
    print()
    print(f'  Accuracy      : {100*accuracy:.2f}%')
    print(f'  Attack recall : {100*attack_recall:.2f}%   (attacks correctly detected)')
    print(f'  False pos rate: {100*false_pos_rate:.2f}%  (normal flagged as attack)')
    print(f'  TP={tp:,}  TN={tn:,}  FP={fp:,}  FN={fn:,}')

    print('\nPer-category detection:')
    for cat in ['dos', 'probe', 'r2l', 'u2r']:
        mask = y_test == cat
        if mask.sum() == 0:
            continue
        detected = is_attack_pred[mask].sum()
        print(f'  {cat:8s}: {detected:4,}/{mask.sum():4,} detected '
              f'({100*detected/mask.sum():.1f}%)')

    return accuracy, attack_recall, false_pos_rate


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scratch-dir', default=os.getenv('SCRATCH_DIR', '/platform/scratch'))
    parser.add_argument('--data-dir',    default=os.getenv('DATA_DIR',    '/platform/data'))
    parser.add_argument('--train-file',  default=os.getenv('TRAIN_FILE',  'KDDTrain+.txt'))
    parser.add_argument('--test-file',   default='KDDTest+.txt')
    args = parser.parse_args()

    print('Loading model artefacts ...')
    encoder, centroids = load_model_artefacts(args.scratch_dir)
    print(f'  Encoder loaded | Centroids shape: {centroids.shape}')

    print('\nLoading training data (for cluster identification) ...')
    X_train, y_train = load_and_preprocess(args.data_dir, args.train_file)

    print('\nLoading test data ...')
    X_test, y_test = load_and_preprocess(args.data_dir, args.test_file)

    normal_cluster = identify_normal_cluster(encoder, centroids, X_train, y_train)
    evaluate(encoder, centroids, X_test, y_test, normal_cluster)


if __name__ == '__main__':
    main()
