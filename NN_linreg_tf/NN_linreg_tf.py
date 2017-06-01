import tensorflow as tf
import numpy as np
import pandas as pd
import tensorflow.contrib.learn as learn
import tensorflow.contrib.layers as layers

import categorical_keys as keys

TABLETS_TRAINING_DATA = "tablets_training.csv"
TABLETS_TESTING_DATA = "tablets_testing.csv"

df_train = pd.read_csv(TABLETS_TRAINING_DATA)
df_test = pd.read_csv(TABLETS_TESTING_DATA)

CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Bilddiagonale', 'Auflösung', 'Akkukapazität',
                      'Grafik-Controller-Serie']
CONTINUOUS_COLUMNS = ['Speicherkapazität', 'Arbeitsspeicher', 'CPU-Taktfrequenz', 'Auflösung Hauptkamera']


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


def preprocess_data(raw_data, write=False):
    if not isinstance(raw_data, pd.DataFrame):
        raise Exception('raw_data must be type DataFrame')
    else:
        categorical_dummies = pd.get_dummies(raw_data, columns=CATEGORICAL_COLUMNS)
        parsed_data = categorical_dummies.drop(['article_id'], axis=1)
        if write:
            parsed_data.to_csv('dummies.csv', encoding='UTF-8')


def build_model(data_dir):
    betriebssystem = layers.sparse_column_with_keys(column_name='Betriebssystem', keys=keys.BETRIEBSSYSTEM_KEYS)
    brand = layers.sparse_column_with_keys(column_name='brand', keys=keys.BRAND_KEYS)
    bilddiagonale = layers.sparse_column_with_keys(column_name='Bilddiagonale', keys=keys.BILDDIAGONALE_KEYS)
    aufloesung = layers.sparse_column_with_keys(column_name='Auflösung', keys=keys.AUFLOESUNG_KEYS)
    akkukapazitaet = layers.sparse_column_with_keys(column_name='Akkukapazität', keys=keys.AKKUKAPAZITAET_KEYS)
    gpu = layers.sparse_column_with_keys(column_name='Grafik-Controller-Serie', keys=keys.GPU_KEYS)

    arbeitsspeicher = layers.real_valued_column('Arbeitsspeicher')
    speicherkapazitaet = layers.real_valued_column('Speicherkapazität')
    cpufrequenz = layers.real_valued_column('CPU-Taktfrequenz')
    kameraaufloesung = layers.real_valued_column('Auflösung Hauptkamera')


def main():
    training_set = learn.datasets.base.load_csv_with_header(
        TABLETS_TRAINING_DATA,
        target_dtype=np.float32,
        features_dtype=np.float32,
        target_column=5
    )
    testing_set = learn.datasets.base.load_csv_with_header(
        TABLETS_TESTING_DATA,
        target_dtype=np.float32,
        features_dtype=np.float32,
        target_column=5
    )



if __name__ == "__main__":
    main()