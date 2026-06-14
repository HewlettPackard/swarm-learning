"""
Deep K-Means for Network Intrusion Detection — NSL-KDD
HPE Swarm Learning example.

Two-phase training using Functional API models (required for SwarmCallback
compatibility — subclassed models cause weight-count assertion errors in TF2.7):

  Phase 1  (LOCAL, no Swarm): Autoencoder pretraining on MSE loss.
  Phase 2  (FEDERATED):       Combined model (encoder + clustering + decoder)
             trained with MSE + λ·KLD.  SwarmCallback syncs all weights
             (encoder, decoder, centroids) across nodes every syncFrequency batches.

Fixed categorical lists ensure every node produces the same feature shape,
which is required for federated weight averaging to be valid.

Environment variables (set by SWOP in Swarm mode):
  DATA_DIR        path containing KDDTrain+.txt   (default /platform/data)
  SCRATCH_DIR     output directory                 (default /platform/scratch)
  MAX_EPOCHS      Phase 2 joint-training epochs    (default 30)
  MIN_PEERS       minimum swarm peers              (default 2)
  PRETRAIN_EPOCHS Phase 1 autoencoder epochs       (default 15)
  LAMBDA_COEFF    clustering loss weight λ         (default 0.1)
  N_CLUSTERS      K                                (default 5)
  LATENT_DIM      encoder output size              (default 10)
  TRAIN_FILE      filename inside DATA_DIR         (default KDDTrain+.txt)
"""

import sys
import os

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from sklearn.cluster import KMeans

try:
    from swarmlearning.tf import SwarmCallback
except ImportError:
    try:
        from swarmlearning import SwarmCallback
    except ImportError:
        SwarmCallback = None  # running locally without Swarm infrastructure

# ---------------------------------------------------------------------------
# NSL-KDD schema
# ---------------------------------------------------------------------------
_COL_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
    'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
    'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
    'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate',
    'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
    'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
    'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
    'dst_host_srv_rerror_rate', 'label', 'difficulty'
]

_ATTACK_MAP = {
    'normal': 'normal',
    'back': 'dos', 'land': 'dos', 'neptune': 'dos', 'pod': 'dos',
    'smurf': 'dos', 'teardrop': 'dos', 'mailbomb': 'dos',
    'apache2': 'dos', 'processtable': 'dos', 'udpstorm': 'dos',
    'ipsweep': 'probe', 'nmap': 'probe', 'portsweep': 'probe',
    'satan': 'probe', 'mscan': 'probe', 'saint': 'probe',
    'ftp_write': 'r2l', 'guess_passwd': 'r2l', 'imap': 'r2l',
    'multihop': 'r2l', 'phf': 'r2l', 'spy': 'r2l', 'warezclient': 'r2l',
    'warezmaster': 'r2l', 'sendmail': 'r2l', 'named': 'r2l',
    'snmpgetattack': 'r2l', 'snmpguess': 'r2l', 'xlock': 'r2l',
    'xsnoop': 'r2l', 'httptunnel': 'r2l',
    'buffer_overflow': 'u2r', 'loadmodule': 'u2r', 'perl': 'u2r',
    'rootkit': 'u2r', 'ps': 'u2r', 'sqlattack': 'u2r', 'xterm': 'u2r'
}

# Fixed categories — all nodes must use these exact lists so feature shapes match
_PROTOCOL_CATS = ['icmp', 'tcp', 'udp']
_SERVICE_CATS = [
    'IRC', 'X11', 'Z39_50', 'aol', 'auth', 'bgp', 'courier', 'csnet_ns',
    'ctf', 'daytime', 'discard', 'domain', 'domain_u', 'echo', 'eco_i',
    'ecr_i', 'efs', 'exec', 'finger', 'ftp', 'ftp_data', 'gopher',
    'harvest', 'hostnames', 'http', 'http_2784', 'http_443', 'http_8001',
    'imap4', 'iso_tsap', 'klogin', 'kshell', 'ldap', 'link', 'login',
    'mtp', 'name', 'netbios_dgm', 'netbios_ns', 'netbios_ssn', 'netstat',
    'nnsp', 'nntp', 'ntp_u', 'other', 'pm_dump', 'pop_2', 'pop_3',
    'printer', 'private', 'red_i', 'remote_job', 'rje', 'shell', 'smtp',
    'sql_net', 'ssh', 'sunrpc', 'supdup', 'systat', 'telnet', 'tftp_u',
    'tim_i', 'time', 'urh_i', 'urp_i', 'uucp', 'uucp_path', 'vmnet', 'whois'
]
_FLAG_CATS = ['OTH', 'REJ', 'RSTO', 'RSTOS0', 'RSTR', 'S0', 'S1', 'S2', 'S3', 'SF', 'SH']

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_MAX_EPOCHS      = 30
DEFAULT_PRETRAIN_EPOCHS = 15
DEFAULT_MIN_PEERS       = 2
DEFAULT_LAMBDA          = 0.1
DEFAULT_N_CLUSTERS      = 5
DEFAULT_LATENT_DIM      = 10
DEFAULT_TRAIN_FILE      = 'KDDTrain+.txt'
BATCH_SIZE              = 256


# ---------------------------------------------------------------------------
# NSL-KDD data loading and preprocessing
# ---------------------------------------------------------------------------
def load_and_preprocess(data_dir, train_file):
    import pandas as pd
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer

    file_path = os.path.join(data_dir, train_file)
    print(f'Loading data: {file_path}')

    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
    has_header = first_line.startswith('duration')

    if has_header:
        df = pd.read_csv(file_path, low_memory=False)
        labels = df['label'].values
        df = df.drop(['label'], axis=1)
        if 'difficulty' in df.columns:
            df = df.drop(['difficulty'], axis=1)
    else:
        df = pd.read_csv(file_path, names=_COL_NAMES, low_memory=False)
        df['label'] = df['label'].map(_ATTACK_MAP).fillna('unknown')
        labels = df['label'].values
        df = df.drop(['label', 'difficulty'], axis=1)

    categorical_cols = ['protocol_type', 'service', 'flag']
    numeric_cols = [c for c in df.columns if c not in categorical_cols]

    preprocessor = ColumnTransformer(transformers=[
        ('cat', OneHotEncoder(
            categories=[_PROTOCOL_CATS, _SERVICE_CATS, _FLAG_CATS],
            sparse_output=False,
            handle_unknown='ignore'
        ), categorical_cols),
        ('num', StandardScaler(), numeric_cols)
    ])

    X = preprocessor.fit_transform(df).astype(np.float32)
    unique, counts = np.unique(labels, return_counts=True)
    dist = ', '.join(f'{u}:{c}' for u, c in zip(unique, counts))
    print(f'  {len(X):,} samples, {X.shape[1]} features | {dist}')
    return X, labels


# ---------------------------------------------------------------------------
# ClusteringLayer — Functional API compatible
# ---------------------------------------------------------------------------
class ClusteringLayer(layers.Layer):
    """Soft cluster assignment via Student-t distribution."""
    def __init__(self, n_clusters, embedding_dim, **kwargs):
        super().__init__(**kwargs)
        self.n_clusters    = n_clusters
        self.embedding_dim = embedding_dim

    def build(self, input_shape):
        self.clusters = self.add_weight(
            name='clusters',
            shape=(self.n_clusters, self.embedding_dim),
            initializer='glorot_uniform',
            trainable=True,
        )
        super().build(input_shape)

    def call(self, inputs):
        z   = tf.expand_dims(inputs, axis=1)
        mu  = tf.expand_dims(self.clusters, axis=0)
        dist = tf.reduce_sum(tf.square(z - mu), axis=2)
        q   = 1.0 / (1.0 + dist)
        q   = q / tf.reduce_sum(q, axis=1, keepdims=True)
        return q

    def get_config(self):
        cfg = super().get_config()
        cfg.update({'n_clusters': self.n_clusters, 'embedding_dim': self.embedding_dim})
        return cfg


# ---------------------------------------------------------------------------
# Target distribution for DEC
# ---------------------------------------------------------------------------
def target_distribution(q):
    weight = q ** 2 / q.sum(axis=0)
    return (weight.T / weight.sum(axis=1)).T


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    model_name      = 'deep-kmeans'
    data_dir        = os.getenv('DATA_DIR',        '/platform/data')
    scratch_dir     = os.getenv('SCRATCH_DIR',     '/platform/scratch')
    max_epochs      = int(os.getenv('MAX_EPOCHS',      str(DEFAULT_MAX_EPOCHS)))
    pretrain_epochs = int(os.getenv('PRETRAIN_EPOCHS', str(DEFAULT_PRETRAIN_EPOCHS)))
    min_peers       = int(os.getenv('MIN_PEERS',       str(DEFAULT_MIN_PEERS)))
    lambda_coeff    = float(os.getenv('LAMBDA_COEFF',  str(DEFAULT_LAMBDA)))
    n_clusters      = int(os.getenv('N_CLUSTERS',      str(DEFAULT_N_CLUSTERS)))
    latent_dim      = int(os.getenv('LATENT_DIM',      str(DEFAULT_LATENT_DIM)))
    train_file      = os.getenv('TRAIN_FILE',      DEFAULT_TRAIN_FILE)

    os.makedirs(scratch_dir, exist_ok=True)
    print(f'***** Starting model = {model_name}')
    print(f'      pretrain={pretrain_epochs} (local)  joint={max_epochs} (federated)  '
          f'K={n_clusters}  latent={latent_dim}  λ={lambda_coeff}')

    # ── Load and preprocess NSL-KDD data ────────────────────────────────────
    X, _ = load_and_preprocess(data_dir, train_file)
    input_dim = X.shape[1]

    # ── Build models (Functional API — required for SwarmCallback) ───────────
    # Encoder
    enc_input = keras.Input(shape=(input_dim,), name='enc_input')
    e         = layers.Dense(64,        activation='relu',   name='enc_1')(enc_input)
    e         = layers.Dense(32,        activation='relu',   name='enc_2')(e)
    embedding = layers.Dense(latent_dim, activation='linear', name='embedding')(e)
    encoder   = Model(inputs=enc_input, outputs=embedding, name='encoder')

    # Autoencoder (encoder + decoder, used for Phase 1 only)
    d        = layers.Dense(32,        activation='relu',   name='dec_1')(embedding)
    d        = layers.Dense(64,        activation='relu',   name='dec_2')(d)
    recon    = layers.Dense(input_dim, activation='linear', name='recon_out')(d)
    autoencoder = Model(inputs=enc_input, outputs=recon, name='autoencoder')

    # Combined model for Phase 2: two outputs — cluster assignments + reconstruction
    combined_in  = keras.Input(shape=(input_dim,), name='combined_input')
    emb          = encoder(combined_in)
    cluster_out  = ClusteringLayer(n_clusters, latent_dim, name='clustering')(emb)
    d2           = layers.Dense(32,        activation='relu',   name='cdec_1')(emb)
    d2           = layers.Dense(64,        activation='relu',   name='cdec_2')(d2)
    recon_out    = layers.Dense(input_dim, activation='linear', name='crecon')(d2)
    combined_model = Model(
        inputs=combined_in,
        outputs=[cluster_out, recon_out],
        name='combined_model'
    )

    print(f'\nEncoder params   : {encoder.count_params():,}')
    print(f'Autoencoder params: {autoencoder.count_params():,}')
    print(f'Combined params  : {combined_model.count_params():,}')
    print(f'Clustering       : {n_clusters} centroids × {latent_dim} dims')

    # ── Phase 1: LOCAL autoencoder pretraining (no SwarmCallback) ───────────
    print(f'\n{"─"*60}')
    print(f'Phase 1: local autoencoder pretraining ({pretrain_epochs} epochs)')
    print(f'{"─"*60}')

    autoencoder.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss='mse', metrics=['mae']
    )
    autoencoder.fit(
        X, X,
        epochs=pretrain_epochs,
        batch_size=BATCH_SIZE,
        validation_split=0.1,
        verbose=1,
        shuffle=True,
    )

    # Transfer encoder weights into combined model's encoder sub-model
    combined_model.get_layer('encoder').set_weights(encoder.get_weights())
    print('Encoder weights transferred to combined model.')

    # K-means initialisation of cluster centroids
    print('\nGenerating embeddings for K-means initialisation...')
    embeddings = encoder.predict(X, verbose=0)
    km = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    km.fit(embeddings)
    combined_model.get_layer('clustering').set_weights([km.cluster_centers_])
    print(f'K-means inertia: {km.inertia_:.4f}  |  '
          + '  '.join(f'C{c}:{n}' for c, n in
                      zip(*np.unique(km.labels_, return_counts=True))))

    # ── Phase 2: FEDERATED joint Deep K-Means training ──────────────────────
    print(f'\n{"─"*60}')
    print(f'Phase 2: federated joint training ({max_epochs} epochs, minPeers={min_peers})')
    print(f'{"─"*60}')

    combined_model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss=['kld', 'mse'],
        loss_weights=[lambda_coeff, 1.0],
    )

    # SwarmCallback requires a single fit() call for all epochs — it fires
    # on_train_end once, which signals the SL that training is complete.
    # Calling fit() in a loop causes the SL to shut down after the first call.
    #
    # We update the target distribution P every P_UPDATE_INTERVAL epochs via
    # a Keras Sequence that regenerates batches from the latest P on each epoch.
    P_UPDATE_INTERVAL = 2  # recompute P every N epochs

    class DKMSequence(keras.utils.Sequence):
        """Yields (X_batch, [P_batch, X_batch]) and refreshes P every N epochs."""
        def __init__(self, X, model, update_interval, batch_size):
            self.X = X
            self.model = model
            self.update_interval = update_interval
            self.batch_size = batch_size
            self.epoch = 0
            self._refresh_p()

        def _refresh_p(self):
            q, _ = self.model.predict(self.X, verbose=0)
            self.p = target_distribution(q)
            assignments = np.argmax(q, axis=1)
            u, c = np.unique(assignments, return_counts=True)
            print('\n  [epoch {:3d}] cluster dist: {}'.format(
                self.epoch, '  '.join(f'C{ci}:{ni}' for ci, ni in zip(u, c))), flush=True)

        def __len__(self):
            return int(np.ceil(len(self.X) / self.batch_size))

        def __getitem__(self, idx):
            s = idx * self.batch_size
            e = s + self.batch_size
            xb = self.X[s:e]
            pb = self.p[s:e]
            return xb, [pb, xb]

        def on_epoch_end(self):
            self.epoch += 1
            if self.epoch % self.update_interval == 0:
                self._refresh_p()

    seq = DKMSequence(X, combined_model, P_UPDATE_INTERVAL, BATCH_SIZE)

    # syncFrequency must be < batches_per_epoch so at least one sync happens
    # per epoch. With ~69 batches/epoch, half that gives ~2 syncs/epoch.
    batches_per_epoch = int(np.ceil(len(X) / BATCH_SIZE))
    sync_freq = max(10, batches_per_epoch // 2)
    print(f'syncFrequency={sync_freq}  (batches/epoch={batches_per_epoch})', flush=True)

    callbacks = []
    if SwarmCallback is not None:
        swarm_cb = SwarmCallback(
            syncFrequency=sync_freq,
            minPeers=min_peers,
            useAdaptiveSync=False,
            mergeMethod='mean',
            totalEpochs=max_epochs,
        )
        callbacks.append(swarm_cb)
    else:
        print('Running without SwarmCallback (local mode).', flush=True)

    try:
        combined_model.fit(
            seq,
            epochs=max_epochs,
            verbose=1,
            callbacks=callbacks,
        )
        print('\nPhase 2 training done!')
    except Exception as exc:
        import traceback
        err_msg = traceback.format_exc()
        print(f'\nPhase 2 interrupted ({type(exc).__name__}: {exc}); saving current state.')
        with open(os.path.join(scratch_dir, 'training_error.log'), 'w') as _f:
            _f.write(err_msg)

    # ── Save ─────────────────────────────────────────────────────────────────
    model_path = os.path.join(scratch_dir, model_name)
    try:
        encoder.save(model_path + '_encoder.keras')
        np.save(model_path + '_centroids.npy',
                combined_model.get_layer('clustering').get_weights()[0])
    except Exception:
        encoder.save(model_path + '_encoder.h5')
        np.save(model_path + '_centroids.npy',
                combined_model.get_layer('clustering').get_weights()[0])

    print(f'\nSaved encoder and centroids to {scratch_dir}/')


if __name__ == '__main__':
    # Redirect stdout/stderr to a persistent log file so container output is
    # captured even when the container uses auto_remove=True.
    _STARTUP_LOG = '/tmp/test/startup.log'
    try:
        _logf = open(_STARTUP_LOG, 'w', buffering=1)
        sys.stdout = _logf
        sys.stderr = _logf
        print(f'--- autoencoder.py starting ---', flush=True)
        print(f'Python {sys.version}', flush=True)
        print(f'CWD: {os.getcwd()}', flush=True)
        print(f'numpy {np.__version__}  tf {tf.__version__}', flush=True)
        print(f'SwarmCallback: {SwarmCallback}', flush=True)
    except Exception:
        pass  # fall back to default stdout/stderr

    try:
        main()
    except Exception as _main_exc:
        import traceback
        _tb = traceback.format_exc()
        print(f'\nFATAL error in main():\n{_tb}', flush=True)
        _sd = os.getenv('SCRATCH_DIR', 'scratch')
        try:
            os.makedirs(_sd, exist_ok=True)
            with open(os.path.join(_sd, 'training_error.log'), 'w') as _ef:
                _ef.write(_tb)
        except Exception:
            pass
        sys.exit(1)
