import tensorflow as tf
import pandas as pd
import categorical_keys as keys
import tempfile

CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Bilddiagonale', 'Aufloesung', 'Akkukapazitaet',
                      'Grafik-Controller-Serie']
CONTINUOUS_COLUMNS = ['Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz', 'Aufloesung_Hauptkamera']
TARGET_COLUMN = ['avg_price']


def build_estimator(model_dir):
    # Categorical feature columns
    betriebssystem = tf.contrib.layers.sparse_column_with_keys(column_name='Betriebssystem', keys=keys.BETRIEBSSYSTEM_KEYS)
    brand = tf.contrib.layers.sparse_column_with_keys(column_name='brand', keys=keys.BRAND_KEYS)
    bilddiagonale = tf.contrib.layers.sparse_column_with_keys(column_name='Bilddiagonale', keys=keys.BILDDIAGONALE_KEYS)
    aufloesung = tf.contrib.layers.sparse_column_with_keys(column_name='Aufloesung', keys=keys.AUFLOESUNG_KEYS)
    akkukapazitaet = tf.contrib.layers.sparse_column_with_keys(column_name='Akkukapazitaet', keys=keys.AKKUKAPAZITAET_KEYS)
    gpu = tf.contrib.layers.sparse_column_with_keys(column_name='Grafik-Controller-Serie', keys=keys.GPU_KEYS)

    # Continuous feature columns
    arbeitsspeicher = tf.contrib.layers.real_valued_column('Arbeitsspeicher')
    speicherkapazitaet = tf.contrib.layers.real_valued_column('Speicherkapazitaet')
    cpufrequenz = tf.contrib.layers.real_valued_column('CPU-Taktfrequenz')
    kameraaufloesung = tf.contrib.layers.real_valued_column('Aufloesung_Hauptkamera')

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

    model = tf.contrib.learn.DNNLinearCombinedRegressor(
        model_dir=model_dir,
        linear_feature_columns=wide_cols,
        dnn_feature_columns=deep_cols,
        dnn_hidden_units=[100, 50],
        fix_global_step_increment_bug=True)

    return model


def preprocess_data(train, test):
    train['Arbeitsspeicher'] = train['Arbeitsspeicher'].fillna(train['Arbeitsspeicher'].median()).astype(float)
    train['Speicherkapazitaet'] = train['Speicherkapazitaet'].fillna(train['Speicherkapazitaet'].median()).astype(
        float)
    train['CPU-Taktfrequenz'] = train['CPU-Taktfrequenz'].fillna(train['CPU-Taktfrequenz'].median()).astype(
        float)
    train['Aufloesung_Hauptkamera'] = train['Aufloesung_Hauptkamera'].fillna(
        train['Aufloesung_Hauptkamera'].median()).astype(float)

    test['Arbeitsspeicher'] = test['Arbeitsspeicher'].fillna(test['Arbeitsspeicher'].median()).astype(float)
    test['Speicherkapazitaet'] = test['Speicherkapazitaet'].fillna(test['Speicherkapazitaet'].median()).astype(
        float)
    test['CPU-Taktfrequenz'] = test['CPU-Taktfrequenz'].fillna(test['CPU-Taktfrequenz'].median()).astype(float)
    test['Aufloesung_Hauptkamera'] = test['Aufloesung_Hauptkamera'].fillna(
        test['Aufloesung_Hauptkamera'].median()).astype(float)

    return train, test


def input_fn(df):
    continuous_cols = {k: tf.constant(df[k].values)
                       for k in CONTINUOUS_COLUMNS}
    categorical_cols = {k: tf.SparseTensor(
        indices=[[i, 0] for i in range(df[k].size)],
        values=df[k].values,
        dense_shape=[df[k].size, 1])
                        for k in CATEGORICAL_COLUMNS}
    continuous_cols.update(categorical_cols)
    feature_cols = continuous_cols
    target = tf.constant(df['avg_price'].values)
    return feature_cols, target


def main():
    df_train = pd.read_csv('tablets_training.csv')
    df_test = pd.read_csv('tablets_testing.csv')

    train_steps = 5000
    model_dir = tempfile.mkdtemp()

    df_train, df_test = preprocess_data(df_train, df_test)
    estimator = build_estimator(model_dir)
    estimator.fit(input_fn=lambda: input_fn(df_train), steps=train_steps)

    print(estimator.evaluate(input_fn=lambda: input_fn(df_test), steps=1))

if __name__ == "__main__":
    main()
