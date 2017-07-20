from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import load_model
import h5py
import csv
import pandas as pd
import numpy as np

TABLET_CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz',
                              'Bilddiagonale', 'Festplatte']
KOPIERPAPIER_CATEGORICAL_COLUMNS = ['brand', 'Format', 'Farbe', 'Verpackungseinheit', 'Papierstaerke']


def read_data(filename):
    data_frame = pd.read_csv(filename, delimiter=',', header=0)
    Y = data_frame.ix[:, 1]
    data_frame = data_frame[KOPIERPAPIER_CATEGORICAL_COLUMNS]
    X = pd.get_dummies(data_frame, columns=KOPIERPAPIER_CATEGORICAL_COLUMNS)

    X_train = np.array(X.ix[0:2500, :])
    X_test = np.array(X.ix[2501:, :])
    Y_train = np.array(Y.ix[0:2500])
    Y_test = np.array(Y.ix[2501:])
    onehot_dimension = X_train.shape[1]

    print('Test data starting at ' + str(data_frame.ix[2501, 0]))
    return X_train,Y_train, X_test, Y_test, onehot_dimension, np.array(data_frame.ix[2501:, :])


def build_model(input_dim):
    model = Sequential()
    model.add(Dense(500, input_dim=input_dim, activation='relu'))
    # model.add(Dropout(0.15))
    model.add(Dense(300, activation='relu'))
    model.add(Dense(300, activation='relu'))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adagrad')
    return model


def main():
    # train_file = 'tablets_training_data.csv'
    train_file = 'kopierpapier_training_data.csv'
    X_train, Y_train, X_test, Y_test, onehot_dimension, test_dat = read_data(filename=train_file)
    '''
    model = build_model(onehot_dimension)
    model.fit(X_train, Y_train, nb_epoch=1000, verbose=1)
    model.save('/model/kopierpapier_2_model.h5')

    '''
    model = load_model('/model/kopierpapier_2_model.h5')

    predictions = model.predict(X_test, verbose=1)
    predictions = predictions.astype(float)
    results = np.concatenate((np.reshape(Y_test, (Y_test.shape[0], 1)), predictions), axis=1)
    print(results)

    results = np.concatenate((test_dat, np.reshape(Y_test.astype(float), (Y_test.shape[0], 1))), axis=1)
    results = np.concatenate((results, predictions), axis=1)
    with open('/results/kopierpapier_2_model.csv', 'w', newline='') as f:
        csvwriter = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in results:
            csvwriter.writerow(row)


if __name__ == "__main__":
    main()
