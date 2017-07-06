from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
import pandas as pd
import numpy as np

CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz', 'Bilddiagonale',
                       'Aufloesung', 'Festplatte', 'Akkukapazitaet', 'Aufloesung Hauptkamera', 'SSD-Speicherkapazitaet', 'Grafik-Controller-Serie']


def read_data(filename):
    data_frame = pd.read_csv(filename, delimiter=',', header=0)
    X = pd.get_dummies(data_frame.ix[:, 2:], columns=CATEGORICAL_COLUMNS)
    Y = data_frame.ix[:, 1]
    return X, Y


def build_model():
    model = Sequential()
    model.add(Dense(12, input_dim=283, activation='relu'))
    model.add(Dense(12, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adagrad')
    return model


def main():
    train_file = 'train.csv'
    test_file = 'test.csv'
    X_train, Y_train = read_data(filename=train_file)
    X_test, Y_test = read_data(filename=test_file)
    model = build_model()

    model.fit(X_train, Y_train, nb_epoch=100, verbose=1)
    predictions = model.predict(X_test, verbose=1)

    print(predictions)

if __name__ == "__main__":
    main()
