import pandas as pd
import os

# Definir rutas absolutas o relativas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_actividad_path = os.path.join(BASE_DIR, 'datos_actividad.csv')
csv_casino_path = os.path.join(BASE_DIR, 'datos_casino.csv')

# Leer actividad
try:
    df_actividad = pd.read_csv(csv_actividad_path, parse_dates=['fecha'], encoding='utf-8')
except UnicodeDecodeError:
    df_actividad = pd.read_csv(csv_actividad_path, parse_dates=['fecha'], encoding='latin1')

# Leer casino
try:
    df_casino = pd.read_csv(csv_casino_path, encoding='utf-8')
except UnicodeDecodeError:
    df_casino = pd.read_csv(csv_casino_path, encoding='latin1')

# Imprimir los dataframes
print("\n--- DATOS ACTIVIDAD ---")
print(df_actividad)

print("\n--- DATOS CASINO ---")
print(df_casino)
