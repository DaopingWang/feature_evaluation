import tensorflow as tf
import numpy as np
import pandas as pd

import tensorflow.contrib.learn as learn

TABLETS_TRAINING_DATA = "tablets_training.csv"
TABLETS_TESTING_DATA = "tablets_testing.csv"

CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Bilddiagonale', 'Auflösung', 'Akkukapazität',
                      'Grafik-Controller-Serie']
CONTINUOUS_COLUMNS = ['Speicherkapazität', 'Arbeitsspeicher', 'CPU-Taktfrequenz', 'Auflösung Hauptkamera']


def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def preprocess_data(raw_data, write=False):
    if not isinstance(raw_data, pd.DataFrame):
        raise Exception('raw_data must be type DataFrame')
    else:
        categorical_dummies = pd.get_dummies(raw_data, columns=CATEGORICAL_COLUMNS)
        parsed_data = categorical_dummies.drop(['article_id'], axis=1)
        if write:
            parsed_data.to_csv('dummies.csv', encoding='UTF-8')


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

    feature_columns = [tf.contrib.layers.real_valued_column("", dimension=)]

    classifier = learn.DNNClassifier(

    )


if __name__ == "__main__":
    main()