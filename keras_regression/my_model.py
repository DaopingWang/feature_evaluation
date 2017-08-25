from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import load_model
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import accuracy_score
from sklearn import tree

import csv
import pandas as pd
import numpy as np

TABLET_CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz',
                              'Bilddiagonale', 'Festplatte']
KOPIERPAPIER_CATEGORICAL_COLUMNS = ['brand', 'Format', 'Farbe', 'Verpackungseinheit', 'Papierstaerke']


def read_data(training_fn, evaluation_fn, type):
    train_end_label = 2800

    data_frame = pd.read_csv(training_fn, delimiter=',', header=0)
    eval_df = pd.read_csv(evaluation_fn, delimiter='\t', header=0)
    eval_df = eval_df[KOPIERPAPIER_CATEGORICAL_COLUMNS]
    Y = data_frame.ix[:, 1]
    test_df = data_frame.ix[train_end_label+1:, :]
    data_frame = data_frame[KOPIERPAPIER_CATEGORICAL_COLUMNS]

    training_index = data_frame.shape[0]
    conc_df = [data_frame, eval_df]
    conc_df = pd.concat(conc_df, ignore_index=True)

    if type is 'dtr':
        X = pd.get_dummies(conc_df, columns=KOPIERPAPIER_CATEGORICAL_COLUMNS)
        X_train = np.array(X.ix[0:train_end_label, :])
        X_test = np.array(X.ix[train_end_label+1:training_index-1, :])
        X_eval = np.array(X.ix[training_index:, :])
    elif type is 'linearNN':
        X = pd.get_dummies(conc_df, columns=KOPIERPAPIER_CATEGORICAL_COLUMNS)
        X_train = np.array(X.ix[0:train_end_label, :])
        X_test = np.array(X.ix[train_end_label+1:training_index-1, :])
        X_eval = np.array(X.ix[training_index:, :])
    else:
        raise ValueError('Wrong model type.')
    y_train = np.array(Y.ix[0:train_end_label])
    y_test = np.array(Y.ix[train_end_label+1:])
    onehot_dimension = X_train.shape[1]

    return X_train,y_train, X_test, y_test, X_eval, onehot_dimension, np.array(eval_df), np.array(test_df)


def sum_of_loss(y_true, y_pred):
    sol = 0
    for index in range(y_true.size):
        sol += abs(y_true[index] - y_pred[index])
    return sol


def build_linear_model(input_dim):
    model = Sequential()
    model.add(Dense(500, input_dim=input_dim, activation='relu'))
    # model.add(Dropout(0.15))
    model.add(Dense(400, activation='relu'))
    model.add(Dense(300, activation='relu'))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adagrad')
    return model


def build_decision_tree():
    return DecisionTreeRegressor(
        criterion='mse', splitter='best', max_depth=None, max_features=None
    )


def fit_decision_tree(X_train, y_train, adaboost=False, n_est=None):
    dtr = build_decision_tree()
    if adaboost is True:
        dtr = AdaBoostRegressor(dtr, n_estimators=n_est)
    dtr.fit(X_train, y_train)
    return dtr


def fit_linear_model(X_train, y_train, onehot_dimension, iteration, loadfile=None, savefile=None):
    if loadfile is None:
        model = build_linear_model(onehot_dimension)
    else:
        model = load_model(loadfile)
    model.fit(X_train, y_train, nb_epoch=iteration, verbose=1)
    if savefile is not None:
        model.save(savefile)
    return model


def write_eval_file(filename, model, X_eval, test_dat, y_true=None):
    print('Predicting...')
    predictions = model.predict(X_eval)
    predictions = predictions.astype(float)
    if y_true is not None:
        sol = sum_of_loss(y_true=y_true, y_pred=predictions)
        print(sol)
    results = np.concatenate((test_dat, np.reshape(predictions, (predictions.shape[0], 1))), axis=1)
    with open(filename, 'w', newline='') as f:
        csvwriter = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in results:
            csvwriter.writerow(row)
        csvwriter.writerow(sol)


def main():
    train_file = 'kopierpapier_enriched_training_data.csv'
    evaluation_file = 'Arjowiggins_evaluation_data.csv'

    # Linear model
    X_train, y_train, X_test, y_test, X_eval, onehot_dimension, eval_dat, test_dat = read_data(
        training_fn=train_file,
        evaluation_fn=evaluation_file,
        type='linearNN')

    model = fit_linear_model(X_train=X_train,
                             y_train=y_train,
                             onehot_dimension=onehot_dimension,
                             iteration=500000,
                             loadfile=None,
                             savefile='kp_500000_enriched_3200_model.h5')

    # write_eval_file('Staples_eval_1000_model.csv', model, X_eval, eval_dat)
    write_eval_file('kp_500000_enriched_3200_test.csv', model, X_test, test_dat, y_true=y_test)
    '''
    # Decision tree
    X_train, y_train, X_test, y_test, X_eval, onehot_dimension, eval_dat, test_dat = read_data(
        training_fn=train_file,
        evaluation_fn=evaluation_file,
        type='dtr')
    dtr = fit_decision_tree(X_train, y_train, adaboost=True, n_est=600)
    write_eval_file('kp_dt_adaboost_600_enriched.csv', dtr, X_test, test_dat, y_true=y_test)
    '''

if __name__ == "__main__":
    main()
