from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import load_model
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn import tree
from sklearn.metrics import mean_squared_error

import csv
import pandas as pd
import numpy as np
import Policy

TABLET_CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz',
                              'Bilddiagonale', 'Festplatte']
KOPIERPAPIER_CATEGORICAL_COLUMNS = ['brand', 'Format', 'Farbe', 'Verpackungseinheit', 'Papierstaerke']

HAAS_SMARTPHONE_CATEGORICAL_COLUMNS = ['Hersteller', 'Betriebssystem', 'Prozessor', 'Sim Kartenformat']
HAAS_SMARTPHONE_CONTINUOUS_COLUMNS = ['Taktfrequenz', 'Speicherkapazitat', 'Arbeitsspeicher', 'Displaydiagonale', 'ppi',
                                      'Kameraauflosung', 'Kameraauflosung', 'Gewicht', 'Breite', 'Hohe', 'Tiefe', 'Akkukapazitat']
HAAS_SMARTPHONE_CATEGORICAL_KA_COLUMNS = ['Speicherkartensteckplatz', 'Fingerabdrucksensor', 'Naherungssensor',
                                          'Lichtsensor', 'Beschleunigungs-/Bewegungssensor', 'Blende', 'Autofokus',
                                          'Integrierter Blitz', 'Besondere Kamerafunktionen', 'Videoauflosung',
                                          'Geo Tagging', 'Integriertes Gps Modul', '3 G', 'Hsdpa', 'Spritzwasserschutz']


def read_data(training_fn, evaluation_fn, type):
    data_frame = pd.read_csv(training_fn, delimiter=',', header=0)
    # data_frame = Policy.remove_invalid_entries(data_frame)
    # data_frame.to_csv('kopierpapier_enriched_cleaned_training_data.csv', sep=',', index=False, encoding='utf-8')
    total_entries = data_frame.shape[0]
    train_end_label = total_entries - 21
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


def read_haas_data(haas_file, option='all'):
    test_start_index = 125
    data_frame = pd.read_csv(haas_file, delimiter=';', header=0)
    y = data_frame['Preis']
    ppi = calc_ppi(
        np.array(data_frame['Zeilenpixel']),
        np.array(data_frame['Spaltenpixel']),
        np.array(data_frame['Displaydiagonale']))
    data_frame['ppi'] = pd.Series(ppi, index=data_frame.index)
    data_frame['soll'] = y
    if option is 'all':
        categorical_headers = HAAS_SMARTPHONE_CATEGORICAL_COLUMNS + HAAS_SMARTPHONE_CATEGORICAL_KA_COLUMNS
        headers = categorical_headers + HAAS_SMARTPHONE_CONTINUOUS_COLUMNS
    elif option is 'drop_ka':
        categorical_headers = HAAS_SMARTPHONE_CATEGORICAL_COLUMNS
        headers = categorical_headers + HAAS_SMARTPHONE_CONTINUOUS_COLUMNS
    else:
        raise ValueError('Wrong option.')
    X = data_frame[headers]
    X = pd.get_dummies(X, columns=categorical_headers)
    X_train = np.array(X.ix[0:test_start_index, :])
    X_test = np.array(X.ix[test_start_index+1:, :])
    y_train = np.array(y.ix[0:test_start_index])
    y_test = np.array(y.ix[test_start_index+1:])
    dimension = X_train.shape[1]

    headers.append('Preis')
    data_frame = data_frame[headers]
    test_df = np.array(data_frame.ix[test_start_index+1:, :])
    return X_train, X_test, y_train, y_test, dimension, test_df, headers


def calc_ppi(wp, hp, dcm):
    di = np.multiply(dcm.astype(float), 0.3937)
    dp = np.add(np.power(wp.astype(float), 2), np.power(hp.astype(float), 2))
    dp = np.sqrt(dp)
    return np.divide(dp, di)


def sum_of_loss(y_true, y_pred):
    sol = 0
    for index in range(y_true.size):
        sol += abs(y_true[index] - y_pred[index])
    return sol


def build_linear_model(input_dim):
    model = Sequential()
    model.add(Dense(300, input_dim=input_dim, activation='relu'))
    # model.add(Dropout(0.25))
    model.add(Dense(300, activation='relu'))
    model.add(Dense(200, activation='relu'))
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
    if iteration == 0:
        return load_model(loadfile)
    if loadfile is None:
        model = build_linear_model(onehot_dimension)
    else:
        model = load_model(loadfile)
    model.fit(X_train, y_train, nb_epoch=iteration, verbose=1)
    if savefile is not None:
        model.save(savefile)
    return model


def write_eval_file(filename, model, X_eval, test_dat, y_true=None, headers=None):
    print('Predicting...')
    predictions = model.predict(X_eval)
    predictions = predictions.astype(float)

    mean = np.mean(predictions)
    stddev = np.std(predictions)

    results = np.concatenate((test_dat, np.reshape(predictions, (predictions.shape[0], 1))), axis=1)
    with open(filename, 'w', newline='') as f:
        csvwriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if headers is not None:
            csvwriter.writerow(headers)
        for row in results:
            csvwriter.writerow(row)
        csvwriter.writerow([mean, stddev])
        if y_true is not None:
            y_true = np.reshape(y_true, (y_true.shape[0], 1))
            mse = mean_squared_error(y_true=y_true, y_pred=predictions)
            csvwriter.writerow([mse])


def main():
    train_file = 'kopierpapier_enriched_cleaned_training_data.csv'
    evaluation_file = 'papierstaerke_eval.csv'
    haas_file = 'Produktdetails_Media_Markt_Smartphones_reordered.csv'

    # Linear model
    '''
    X_train_haas, X_test_haas, y_train_haas, y_test_haas, dimension_haas, test_df_haas, headers = read_haas_data(
        haas_file=haas_file,
        option='all'
    )

    model = fit_linear_model(X_train=X_train_haas,
                             y_train=y_train_haas,
                             onehot_dimension=dimension_haas,
                             iteration=300000,
                             loadfile=None,
                             savefile=None)
    write_eval_file('haas_300000_all_test.csv', model, X_test_haas, test_df_haas, y_true=y_test_haas, headers=headers)
    '''

    X_train, y_train, X_test, y_test, X_eval, dimension, eval_dat, test_dat = read_data(
        training_fn=train_file,
        evaluation_fn=evaluation_file,
        type='linearNN')

    model = fit_linear_model(X_train=X_train,
                             y_train=y_train,
                             onehot_dimension=dimension,
                             iteration=1000,
                             loadfile=None,
                             savefile='kp_1000_enriched_cleaned_ps_model.h5')
    # write_eval_file('kp_10000_enriched_cleaned_reordered_test.csv', model, X_test, test_dat, y_true=y_test)
    write_eval_file('kp_papierstaerke_enriched_cleaned_eval.csv', model, X_eval, eval_dat)

    '''
    # Decision tree
    X_train, y_train, X_test, y_test, X_eval, onehot_dimension, eval_dat, test_dat = read_data(
        training_fn=train_file,
        evaluation_fn=evaluation_file,
        type='dtr')
    
    dtr = fit_decision_tree(X_train_haas, y_train_haas, adaboost=True, n_est=6000)
    write_eval_file('haas_adaboost6000_dropka_test.csv', dtr, X_test_haas, test_df_haas, y_true=y_test_haas, headers=headers)
    '''

if __name__ == "__main__":
    main()
