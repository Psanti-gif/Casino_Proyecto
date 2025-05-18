import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_actividad_path = os.path.join(BASE_DIR, 'datos_actividad.csv')
csv_casino_path = os.path.join(BASE_DIR, 'datos_casino.csv')

def cargar_datos_actividad():
    try:
        return pd.read_csv(csv_actividad_path, parse_dates=['fecha'], encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(csv_actividad_path, parse_dates=['fecha'], encoding='latin1')

def cargar_datos_casino():
    try:
        return pd.read_csv(csv_casino_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(csv_casino_path, encoding='latin1')

