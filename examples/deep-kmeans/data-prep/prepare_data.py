"""
Prepare NSL-KDD data for Deep K-Means training.

Reads raw KDDTrain+.txt and KDDTest+.txt, applies label encoding and
MinMax scaling, then splits into two non-IID node datasets per slide 17:
  Node 1: 70% normal, 20% DoS,  5% Probe,  5% U2R+R2L
  Node 2: 50% normal, 10% DoS, 30% Probe, 10% U2R+R2L

Outputs (relative to this script's parent directory):
  data-and-scratch1/app-data/KDDTrain_node1.csv
  data-and-scratch2/app-data/KDDTrain_node2.csv
  data-and-scratch1/app-data/KDDTest.csv   (same file, copied to both nodes)
  data-and-scratch2/app-data/KDDTest.csv
  data-prep/encoders.pkl    (LabelEncoders + MinMaxScaler for inference)
"""

import os
import pickle
import shutil
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW_DIR = '/home/viv/swarm-learning/workspace/fraud-detection/data-and-scratch1/app-data'
TRAIN_RAW = os.path.join(RAW_DIR, 'KDDTrain+.txt')
TEST_RAW  = os.path.join(RAW_DIR, 'KDDTest+.txt')

OUT_NODE1 = os.path.join(ROOT, 'data-and-scratch1', 'app-data', 'KDDTrain_node1.csv')
OUT_NODE2 = os.path.join(ROOT, 'data-and-scratch2', 'app-data', 'KDDTrain_node2.csv')
OUT_TEST1 = os.path.join(ROOT, 'data-and-scratch1', 'app-data', 'KDDTest.csv')
OUT_TEST2 = os.path.join(ROOT, 'data-and-scratch2', 'app-data', 'KDDTest.csv')
OUT_ENC   = os.path.join(HERE, 'encoders.pkl')

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
FEATURE_COLS = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root',
    'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds',
    'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
    'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
    'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
    'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate',
]
CAT_COLS = ['protocol_type', 'service', 'flag']

ATTACK_MAP = {
    'normal': 'normal',
    # DoS
    'back': 'DoS', 'land': 'DoS', 'neptune': 'DoS', 'pod': 'DoS',
    'smurf': 'DoS', 'teardrop': 'DoS', 'apache2': 'DoS', 'udpstorm': 'DoS',
    'processtable': 'DoS', 'worm': 'DoS', 'mailbomb': 'DoS',
    # Probe
    'satan': 'Probe', 'ipsweep': 'Probe', 'nmap': 'Probe', 'portsweep': 'Probe',
    'mscan': 'Probe', 'saint': 'Probe',
    # U2R
    'buffer_overflow': 'U2R', 'loadmodule': 'U2R', 'perl': 'U2R',
    'rootkit': 'U2R', 'xterm': 'U2R', 'ps': 'U2R', 'sqlattack': 'U2R',
    # R2L
    'guess_passwd': 'R2L', 'ftp_write': 'R2L', 'imap': 'R2L', 'phf': 'R2L',
    'multihop': 'R2L', 'warezmaster': 'R2L', 'warezclient': 'R2L', 'spy': 'R2L',
    'xlock': 'R2L', 'xsnoop': 'R2L', 'snmpguess': 'R2L', 'snmpgetattack': 'R2L',
    'sendmail': 'R2L', 'named': 'R2L', 'httptunnel': 'R2L',
}

# Non-IID target ratios per slide 17
# U2R+R2L are combined because U2R has only ~52 samples in NSL-KDD training set
NODE1_RATIOS = {'normal': 0.70, 'DoS': 0.20, 'Probe': 0.05, 'minority': 0.05}
NODE2_RATIOS = {'normal': 0.50, 'DoS': 0.10, 'Probe': 0.30, 'minority': 0.10}
TARGET_PER_NODE = 20000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_raw(path):
    """Load raw KDD file, return DataFrame with FEATURE_COLS + label + category."""
    all_cols = FEATURE_COLS + ['label', 'difficulty']
    df = pd.read_csv(path, header=None, names=all_cols, on_bad_lines='skip')
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].str.strip()
    df['category'] = df['label'].map(lambda x: ATTACK_MAP.get(x, 'unknown'))
    df = df[df['category'] != 'unknown']
    return df[FEATURE_COLS + ['label', 'category']]


def encode_and_scale(train_df, test_df):
    """
    Fit LabelEncoders on train categorical columns and MinMaxScaler on all
    numeric output. Returns (X_train, y_train_cat, X_test, y_test_cat, encoders).
    """
    encoders = {}

    # Fit label encoders on train; handle unseen values in test with a fallback
    for col in CAT_COLS:
        le = LabelEncoder()
        le.fit(train_df[col].astype(str))
        encoders[col] = le

    def apply_encoders(df):
        df = df.copy()
        for col in CAT_COLS:
            le = encoders[col]
            vals = df[col].astype(str)
            # Map unseen categories to 0
            known = set(le.classes_)
            df[col] = vals.map(lambda v: le.transform([v])[0] if v in known else 0)
        return df

    train_enc = apply_encoders(train_df)
    test_enc  = apply_encoders(test_df)

    X_train = train_enc[FEATURE_COLS].values.astype(float)
    X_test  = test_enc[FEATURE_COLS].values.astype(float)

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    encoders['scaler'] = scaler
    return X_train, train_df['category'].values, X_test, test_df['category'].values, encoders


def non_iid_split(X, categories, ratios, target_n, rng, used_indices=None):
    """
    Sample `target_n` rows from X following `ratios` dict.
    `used_indices` — set of row indices already taken by another node (avoided).
    Returns (X_node, cat_node, chosen_indices).
    """
    if used_indices is None:
        used_indices = set()

    chosen_rows, chosen_cats, chosen_idx = [], [], []

    # Map categories to indices (excluding already-used)
    cat_pool = {}
    for cat in ratios:
        if cat == 'minority':
            mask = np.isin(categories, ['U2R', 'R2L'])
        else:
            mask = categories == cat
        pool = [i for i in np.where(mask)[0] if i not in used_indices]
        rng.shuffle(pool)
        cat_pool[cat] = pool

    for cat, ratio in ratios.items():
        n_needed = int(target_n * ratio)
        pool = cat_pool[cat]
        n_take = min(n_needed, len(pool))
        if n_take < n_needed:
            print(f'  [WARN] {cat}: needed {n_needed}, only {n_take} available')
        idx = pool[:n_take]
        chosen_rows.append(X[idx])
        chosen_cats.extend([cat] * n_take)
        chosen_idx.extend(idx)

    X_node = np.vstack(chosen_rows)
    cats   = np.array(chosen_cats)

    # Shuffle
    perm = rng.permutation(len(X_node))
    return X_node[perm], cats[perm], set(chosen_idx)


def save_csv(X, cats, path):
    """Save feature matrix + category label to CSV."""
    df = pd.DataFrame(X, columns=FEATURE_COLS)
    df['category'] = cats
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f'  Saved {len(df):,} rows → {path}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rng = np.random.default_rng(42)

    print('Loading raw training data ...')
    train_df = load_raw(TRAIN_RAW)
    print(f'  {len(train_df):,} rows loaded')
    print('  Category distribution:')
    for cat, cnt in train_df['category'].value_counts().items():
        print(f'    {cat:10s}: {cnt:6,}')

    print('\nLoading raw test data ...')
    test_df = load_raw(TEST_RAW)
    print(f'  {len(test_df):,} rows loaded')

    print('\nEncoding + scaling ...')
    X_train, y_train, X_test, y_test, encoders = encode_and_scale(train_df, test_df)
    print(f'  Train: {X_train.shape}   Test: {X_test.shape}')

    print('\nCreating non-IID node 1 split ...')
    print(f'  Target ratios: {NODE1_RATIOS}')
    X1, c1, used = non_iid_split(X_train, y_train, NODE1_RATIOS, TARGET_PER_NODE, rng)
    print(f'  Node 1: {len(X1):,} samples  |  dist: { {c: int((c1==c).sum()) for c in np.unique(c1)} }')

    print('\nCreating non-IID node 2 split ...')
    print(f'  Target ratios: {NODE2_RATIOS}')
    X2, c2, _ = non_iid_split(X_train, y_train, NODE2_RATIOS, TARGET_PER_NODE, rng, used_indices=used)
    print(f'  Node 2: {len(X2):,} samples  |  dist: { {c: int((c2==c).sum()) for c in np.unique(c2)} }')

    print('\nSaving node datasets ...')
    save_csv(X1, c1, OUT_NODE1)
    save_csv(X2, c2, OUT_NODE2)

    print('\nSaving shared test set ...')
    save_csv(X_test, y_test, OUT_TEST1)
    shutil.copy(OUT_TEST1, OUT_TEST2)
    print(f'  Copied test set to {OUT_TEST2}')

    print('\nSaving encoders + scaler ...')
    with open(OUT_ENC, 'wb') as f:
        pickle.dump(encoders, f)
    print(f'  Saved → {OUT_ENC}')

    print('\nDone. Summary:')
    print(f'  Node 1 train : {len(X1):,} rows')
    print(f'  Node 2 train : {len(X2):,} rows')
    print(f'  Shared test  : {len(X_test):,} rows')
    print(f'  Features     : {X_train.shape[1]}')


if __name__ == '__main__':
    main()
