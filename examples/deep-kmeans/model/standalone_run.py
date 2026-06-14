"""
Standalone runner — no Swarm Learning infrastructure needed.
Mocks SwarmCallback so autoencoder.py trains normally on node 1's local data.

Usage:
  python3 standalone_run.py
  python3 standalone_run.py --node 2        # run on node 2's data
  python3 standalone_run.py --quick         # 5 pretrain + 10 joint epochs (smoke test)
"""

import sys
import types
import os
import argparse

# ---------------------------------------------------------------------------
# Mock SwarmCallback before autoencoder.py imports it
# ---------------------------------------------------------------------------
class _MockSwarmCallback(
    __import__('tensorflow').keras.callbacks.Callback
):
    def __init__(self, **kwargs):
        super().__init__()
        print(f'[standalone] SwarmCallback mocked '
              f'(syncFrequency={kwargs.get("syncFrequency")}, '
              f'minPeers={kwargs.get("minPeers")}, '
              f'totalEpochs={kwargs.get("totalEpochs")})')

for _mod in ('swarmlearning', 'swarmlearning.tf'):
    _m = types.ModuleType(_mod)
    _m.SwarmCallback = _MockSwarmCallback
    sys.modules[_mod] = _m

# ---------------------------------------------------------------------------
# Now import autoencoder and predict
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import autoencoder as ae

HERE      = os.path.dirname(os.path.abspath(__file__))
EXAMPLE   = os.path.dirname(HERE)
DATA_ROOT = os.path.join(EXAMPLE, 'data-and-scratch{n}', 'app-data')
SCRATCH   = '/tmp/deep-kmeans-scratch'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node',  type=int, default=1,  help='which node dataset to use (1 or 2)')
    parser.add_argument('--quick', action='store_true',  help='smoke test: very few epochs')
    args = parser.parse_args()

    data_dir = DATA_ROOT.format(n=args.node)
    os.makedirs(SCRATCH, exist_ok=True)

    if args.quick:
        pretrain_epochs = 5
        max_epochs      = 10
    else:
        pretrain_epochs = ae.DEFAULT_PRETRAIN_EPOCHS
        max_epochs      = ae.DEFAULT_MAX_EPOCHS

    os.environ['DATA_DIR']        = data_dir
    os.environ['SCRATCH_DIR']     = SCRATCH
    os.environ['MAX_EPOCHS']      = str(max_epochs)
    os.environ['PRETRAIN_EPOCHS'] = str(pretrain_epochs)
    os.environ['MIN_PEERS']       = '1'
    os.environ['TRAIN_FILE']      = 'KDDTrain+.txt'

    print(f'[standalone] Node {args.node} | data: {data_dir}')
    print(f'[standalone] Pretrain epochs: {pretrain_epochs}  Joint epochs: {max_epochs}')
    print(f'[standalone] Scratch: {SCRATCH}')
    print()

    ae.main()

    # ── Run evaluation ───────────────────────────────────────────────────────
    print('\n' + '='*60)
    print('Running prediction / evaluation ...')
    print('='*60)
    import predict
    import numpy as np

    encoder, centroids = predict.load_model_artefacts(SCRATCH)

    X_train, y_train = ae.load_and_preprocess(data_dir, 'KDDTrain+.txt')
    X_test,  y_test  = ae.load_and_preprocess(data_dir, 'KDDTest+.txt')

    normal_cluster = predict.identify_normal_cluster(encoder, centroids, X_train, y_train)
    acc, recall, fpr = predict.evaluate(encoder, centroids, X_test, y_test, normal_cluster)

    print(f'\n[standalone] Final — Accuracy: {100*acc:.2f}%  '
          f'Attack recall: {100*recall:.2f}%  FPR: {100*fpr:.2f}%')


if __name__ == '__main__':
    main()
