from keras.models import Sequential
import pandas as pd
import numpy as np

CATEGORICAL_COLUMNS = ['brand', 'Betriebssystem', 'Speicherkapazitaet', 'Arbeitsspeicher', 'CPU-Taktfrequenz', 'Bilddiagonale'
                       'Aufloesung', 'Festplatte', 'Akkukapazitaet', 'Aufloesung Hauptkamera', 'SSD-Speicherkapazitaet', 'Grafik-Controller-Serie']


def main():
    dataframe = pd.read_csv('')

