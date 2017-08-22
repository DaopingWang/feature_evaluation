from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import load_model
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import accuracy_score
from sklearn import tree

import csv
import pandas as pd
import numpy as np

TABLET_CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz',
                              'Bilddiagonale', 'Festplatte']
KOPIERPAPIER_CATEGORICAL_COLUMNS = ['brand', 'Format', 'Farbe', 'Verpackungseinheit', 'Papierstaerke']


def read_data(training_fn, evaluation_fn, type):
    data_frame = pd.read_csv(training_fn, delimiter=',', header=0)
    eval_df = pd.read_csv(evaluation_fn, delimiter='\t', header=0)
    eval_df = eval_df[KOPIERPAPIER_CATEGORICAL_COLUMNS]
    Y = data_frame.ix[:, 1]
    data_frame = data_frame[KOPIERPAPIER_CATEGORICAL_COLUMNS]

    training_index = data_frame.shape[0]
    conc_df = [data_frame, eval_df]
    conc_df = pd.concat(conc_df, ignore_index=True)

    if type is 'dtr':
        X_train = np.array(conc_df.ix[0:2800, :])
        X_test = np.array(conc_df.ix[2801:training_index-1, :])
        X_eval = np.array(conc_df.ix[training_index:, :])
    elif type is 'linearNN':
        X = pd.get_dummies(conc_df, columns=KOPIERPAPIER_CATEGORICAL_COLUMNS)
        X_train = np.array(X.ix[0:2800, :])
        X_test = np.array(X.ix[2801:training_index-1, :])
        X_eval = np.array(X.ix[training_index:, :])
    else:
        raise ValueError('Lol wrong model type.')
    y_train = np.array(Y.ix[0:2800])
    y_test = np.array(Y.ix[2801:])
    onehot_dimension = X_train.shape[1]

    return X_train,y_train, X_test, y_test, X_eval, onehot_dimension, np.array(eval_df)


def build_linear_model(input_dim):
    model = Sequential()
    model.add(Dense(500, input_dim=input_dim, activation='relu'))
    # model.add(Dropout(0.15))
    model.add(Dense(300, activation='relu'))
    model.add(Dense(300, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adagrad')
    return model


def build_decision_tree():
    return DecisionTreeRegressor(
        criterion='mse', splitter='best', max_depth=None, max_features=None
    )


def fit_decision_tree(dtr, X_train, y_train):
    dtr.fit(X_train, y_train)


def fit_linear_model(X_train, y_train, onehot_dimension, iteration, loadfile=None, savefile=None):
    if loadfile is None:
        model = build_linear_model(onehot_dimension)
        model.fit(X_train, y_train, nb_epoch=iteration, verbose=1)
        if savefile is not None:
            model.save(savefile)
    else:
        model = load_model(loadfile)
    return model


def write_eval_file(filename, model, X_eval, test_dat):
    predictions = model.predict(X_eval, verbose=1)
    predictions = predictions.astype(float)
    results = np.concatenate((test_dat, predictions), axis=1)
    with open(filename, 'w', newline='') as f:
        csvwriter = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in results:
            csvwriter.writerow(row)


def main():
    # train_file = 'tablets_training_data.csv'
    train_file = 'kopierpapier_training_data.csv'
    evaluation_file = 'Staples_evaluation_data.csv'
    X_train, y_train, X_test, y_test, X_eval, onehot_dimension, test_dat = read_data(
        training_fn=train_file, evaluation_fn=evaluation_file, type='linearNN'
    )

    model = fit_linear_model(
        X_train, y_train, onehot_dimension, iteration=100000, loadfile='kopierpapier_505000_model.h5'
    )
    write_eval_file('Staples_eval_100000_model.csv', model, X_eval, test_dat)


if __name__ == "__main__":
    main()
