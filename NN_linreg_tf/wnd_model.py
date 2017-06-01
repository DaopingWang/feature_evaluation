import tensorflow as tf
import pandas as pd
import categorical_keys as keys
import tempfile

CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Bilddiagonale', 'Auflösung', 'Akkukapazität',
                      'Grafik-Controller-Serie']
CONTINUOUS_COLUMNS = ['Speicherkapazität', 'Arbeitsspeicher', 'CPU-Taktfrequenz', 'Auflösung Hauptkamera']
TARGET_COLUMN = ['avg_price']


def build_estimator(model_dir):
    # Categorical feature columns
    betriebssystem = tf.contrib.layers.sparse_column_with_keys(column_name='Betriebssystem', keys=keys.BETRIEBSSYSTEM_KEYS)
    brand = tf.contrib.layers.sparse_column_with_keys(column_name='brand', keys=keys.BRAND_KEYS)
    bilddiagonale = tf.contrib.layers.sparse_column_with_keys(column_name='Bilddiagonale', keys=keys.BILDDIAGONALE_KEYS)
    aufloesung = tf.contrib.layers.sparse_column_with_keys(column_name='Auflösung', keys=keys.AUFLOESUNG_KEYS)
    akkukapazitaet = tf.contrib.layers.sparse_column_with_keys(column_name='Akkukapazität', keys=keys.AKKUKAPAZITAET_KEYS)
    gpu = tf.contrib.layers.sparse_column_with_keys(column_name='Grafik-Controller-Serie', keys=keys.GPU_KEYS)

    # Continuous feature columns
    arbeitsspeicher = tf.contrib.layers.real_valued_column('Arbeitsspeicher')
    speicherkapazitaet = tf.contrib.layers.real_valued_column('Speicherkapazität')
    cpufrequenz = tf.contrib.layers.real_valued_column('CPU-Taktfrequenz')
    kameraaufloesung = tf.contrib.layers.real_valued_column('Auflösung Hauptkamera')

    # Crossed feature columns
    brand_x_bilddiagonale = tf.contrib.layers.crossed_column([brand, bilddiagonale], hash_bucket_size=int(1e4))
    bilddiagonale_x_aufloesung = tf.contrib.layers.crossed_column([bilddiagonale, aufloesung], hash_bucket_size=int(1e4))

    # Wide and deep columns
    wide_cols = [betriebssystem, brand, bilddiagonale, aufloesung, akkukapazitaet,
                 brand_x_bilddiagonale, bilddiagonale_x_aufloesung]
    deep_cols = [tf.contrib.layers.embedding_column(betriebssystem, dimension=6),
                 tf.contrib.layers.embedding_column(brand, dimension=6),
                 tf.contrib.layers.embedding_column(bilddiagonale, dimension=6),
                 tf.contrib.layers.embedding_column(aufloesung, dimension=6),
                 tf.contrib.layers.embedding_column(akkukapazitaet, dimension=6),
                 tf.contrib.layers.embedding_column(gpu, dimension=6),
                 arbeitsspeicher, speicherkapazitaet, cpufrequenz, kameraaufloesung]

    model = tf.contrib.learn.DNNLinearCombinedClassifier(
        model_dir=model_dir,
        linear_feature_columns=wide_cols,
        dnn_feature_columns=deep_cols,
        dnn_hidden_units=[100, 50])

    return model


def train_and_eval(model_dir, train_steps, train_data, test_data):
    df_train = pd.read_csv(train_data)
    df_test = pd.read_csv(test_data)




def input_fn(df):
    continuous_cols = {k: tf.constant(df[k].values)
                       for k in CONTINUOUS_COLUMNS}
    categorical_cols = {k: tf.SparseTensor(
        indices=[[i, 0] for i in range(df[k].size)],
        values=df[k].values,
        dense_shape=[df[k].size, 1])
                        for k in CATEGORICAL_COLUMNS}
    feature_cols = dict(continuous_cols.items() + categorical_cols.items())
    target = tf.constant(df['avg_price'].values)
    return feature_cols, target


def train_input_fn():
    return input_fn(df_train)


def test_input_fn():
    return input_fn(df_test)