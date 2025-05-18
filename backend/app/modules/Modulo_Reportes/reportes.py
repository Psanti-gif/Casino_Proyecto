#Reportes Casino
from datetime import datetime
import pandas as pd
from Cargar_Datos import cargar_datos_actividad, cargar_datos_casino
df_actividad = cargar_datos_actividad()
df_maquinas = cargar_datos_casino()

def SeleccionarMaquina(casino_id = None, incluir_inactivos = False):
    df = df_maquinas[df_maquinas['casino_id'] == casino_id]
   
    if not incluir_inactivos:
        df = df[df['Estado'].str.lower() == 'activo']
        
    if df.empty:
        print("No hay maquinas disponibles.")
        return[]
    
    print("Maquinas disponibles:")
    for i, j in df.iterrows():
        print(f"{j['ID']}: {j['Nombre']} - {j['Tipo']} - {j['Estado']}")
        
    seleccion_id = input("Seleccione las maquinas a través de sus ID's (separelas con coma por favor): ")
    try:
        seleccion = [int(x.strip()) for x in seleccion_id.split(',')]
    except ValueError:
        print("Entrada invalida.")
        return []
    
    maquinas_seleccionadas = df[df['ID'].isin(seleccion)]
    if maquinas_seleccionadas.empty:
        print("No se selecciono maquina, entrada invalida")
        return []
    return maquinas_seleccionadas.to_dict('records')
    
def SeleccionarCasino(nombre=None, zona= None):
    df = df_maquinas[['casino_id', 'casino_nombre', 'zona']].drop_duplicates()
      
    if nombre:
        df = df[df['casino_nombre'].str.contains(nombre, case=False, na=False)]
    
    if zona:
        df = df[df['zona'].str.contains(zona, case=False, na=False)]
    
    if df.empty:
        print("No hay casinos que coincidan con los filtros")
        return None
    
    print("Casinos disponibles:")
    for i, j in df.iterrows():
        print(f"{j['casino_id']}: {j['casino_nombre']} - {j['zona']}")
    
    while True:
        choice = input("Seleccione el casino por su ID: ")
        try:
            if choice in df['casino_id'].values:
                casino_selec = df[df['casino_id'] == choice].iloc[0]
                return{
                    'ID': casino_selec['casino_id'],
                    'Nombre': casino_selec['casino_nombre'],
                    'Zona': casino_selec['zona']
                } 
            else:
                print("ID invalido, por favor intente nuevamente.")
        except ValueError:
            print("Por favor ingrese un numero valido.")
            
def SeleccionarRangoFechas():
    fechas_disponibles = df_actividad['fecha']
    fecha_min = fechas_disponibles.min().date()
    fecha_max = fechas_disponibles.max().date()
    
    print(f"\Rango de fechas disponibles en la base de datos: {fecha_min} hasta {fecha_max}")
    
    while True:
        try:
            entrada_in = input("Ingrese fecha de inicio (YYYY/MM/DD) o 'Exit' para salir").strip()
            if entrada_in.lower() == 'Exit':
                return None, None
            
            entrada_end = input("Ingrese la fecha fin (YYYY/MM/DD) o 'Exit' para salir").strip()
            if entrada_end.lower() == 'Exit':
                return None, None
            
            fecha_inicio = datetime.strptime(entrada_in,"%Y-%m-%d").date()
            fecha_fin = datetime.strptime(entrada_end, "%Y-%m-%d").date()
            
            if fecha_inicio > fecha_fin:
                print("La fecha de inicio no puede ser posterior a la fecha fin")
                continue
            
            if fecha_inicio < fecha_min or fecha_fin > fecha_max:
                print(f"Las fechas deben estar dentro del rango {fecha_min} a {fecha_max}")
                continue
            
            return fecha_inicio, fecha_fin
        except ValueError:
            print("Formato de fecha incorrecto. Use el sugerido.")

def FiltrosAvanazados(df_maquinas):
    print("\n<<< Filtros avanzados >>>")
    
    zonas_disponibles = df_maquinas['zona'].unique()
    print(f"Zonas disponibles: {', '.join(zonas_disponibles)}")
    zona = input("Filtrar por zona (presione ENTER para omitir): ")
    if zona:
        df_maquinas = df_maquinas[df_maquinas['zona'] == zona]
    
    casinos_disponibles = df_maquinas['casino_nombre'].unique()
    print(f"Casinos disponibles: {', '.join(casinos_disponibles)}")
    casino = input("Filtrar por casino (presione ENTER para omitir): ")
    if casino:
        df_maquinas = df_maquinas[df_maquinas['casino_nombre'] == casino]
        
    tipos_disponibles = df_maquinas['Tipo'].unique()
    print(f"Tipos de máquinas disponibles: {', '.join(tipos_disponibles)}")
    tipo = input("Filtrar por tipo de maquina (presione ENTER para omitir): ")
    if tipo:
        df_maquinas = df_maquinas[df_maquinas['Tipo'] == tipo]
        
    marcas_disponibles = df_maquinas['Marca'].unique()
    print(f"Marcas disponibles: {', '.join(marcas_disponibles)}")
    marca = input("Filtrar por marca (presione ENTER para omitir): ")
    if marca:
        df_maquinas = df_maquinas[df_maquinas['Marca'] == marca]
    
    modelos_disponibles = df_maquinas['Modelo'].unique()
    print(f"Modelos disponibles: {', '.join(modelos_disponibles)}")   
    modelo = input("Filtrar por modelo (presione ENTER para omitir): ")
    if modelo:
        df_maquinas = df_maquinas[df_maquinas['Modelo'] == modelo]
        
    if df_maquinas.empty:
        print("No se encontraron resultados.")
        return []
    
    maquinas_selec = df_maquinas.to_dict('records')
    print(f"Se seleccionaron {len(maquinas_selec)} maquinas con los filtros seleccionados.")
    return maquinas_selec
            
def GenerarReporte():
    print("<<< Módulo de Reportes de Casino >>>")
    
    maquinas_filtradas = FiltrosAvanazados()
    
    if not maquinas_filtradas:
        print("Cancelando operacion... No se seleccionó un casino.")
        return

    Fecha_Inicio, Fecha_Fin = SeleccionarRangoFechas()
    
    print("\nTipos de reportes disponibles:")
    print("1. Individual")
    print("2. Grupal")
    print("3. Consolidado")
    TipoReporte = input("Seleccione una opcion: ")
    
    if TipoReporte == '1':
        ReporteIndividual(maquinas_filtradas.to_dict(orient='records'), Fecha_Inicio, Fecha_Fin)
    elif TipoReporte == '2':
        ReporteGrupal(maquinas_filtradas.to_dict(orient='records'), Fecha_Inicio, Fecha_Fin)
    elif TipoReporte == '3':
        ReporteConsolidado(maquinas_filtradas.to_dict(orient='records'), Fecha_Inicio, Fecha_Fin)
    else:
        print("Opcion invalida.")
        return
    
def ReporteIndividual(maquinas, fecha_inicio, fecha_fin):
    print("\n<<< Reporte individual >>>")
    for maquina in maquinas:
        id_maquina = maquina['ID']
        nombre = maquina['Nombre']
        tipo = maquina['Tipo']
        
        df_filtrada = df_actividad[
            (df_actividad['maquina_id'] == id_maquina) &
            (df_actividad['fecha'] >= fecha_inicio) &
            (df_actividad['fecha'] <= fecha_fin)
        ]
        
        if df_filtrada.empty:
            print(f"\nMaquina ID: {id_maquina} ({nombre}): No hay actividad en el rango de fechas.")
            continue
        
        total_in = df_filtrada['IN'].sum()
        total_out = df_filtrada['OUT'].sum()
        total_jackpot = df_filtrada['JACKPOT'].sum()
        total_billetero = df_filtrada['BILLETERO'].sum()
        utilidad = total_in - total_out - total_jackpot - total_billetero
        
        print(f"\nMaquina ID {id_maquina}: {nombre} ({tipo})")
        print(f"IN: {total_in}")
        print(f"OUT: {total_out}")
        print(f"JACKPOT: {total_jackpot}")
        print(f"BILLETERO: {total_billetero}")
        print(f"UTILIDAD: {utilidad}")
        

def ReporteGrupal(maquinas, fecha_inicio, fecha_fin):
    print("<<< Reporte grupal por maquina >>>")
    
    df_maquinas_filtradas = pd.DataFrame(maquinas)
    
    ids_maquinas = df_maquinas_filtradas['ID'].tolist()
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(ids_maquinas)) &
        (df_actividad['fecha'] >= fecha_inicio) &
        (df_actividad['fecha'] <=fecha_fin)
    ]
    
    if df_filtrada.empty:
        print("No hay actividad en el rango de fechas para las maquinas seleccionadas")
        return
    
    df_merged = df_filtrada.merge(df_maquinas_filtradas, left_on = 'maquina_id', right_on = 'ID')
    resumen = df_merged.groupby('Tipo').agg({
        'IN': 'sum',
        'OUT': 'sum',
        'JACKPOT': 'sum',
        'BILLETERO': 'sum'
    }).reset_index()
    
    resumen['UTILIDAD'] = resumen['IN'] - resumen['OUT'] - resumen['JACKPOT'] - resumen['BILLETERO']
    
    for _, fila in resumen.iterrows():
        print(f"\nTipo: {fila['Tipo']}")
        print(f"IN: {fila['IN']}")
        print(f"OUT: {fila['OUT']}")
        print(f"JACKPOT: {fila['JACKPOT']}")
        print(f"BILLETERO: {fila['BILLETERO']}")
        print(f"UTILIDAD: {fila['UTILIDAD']}")
    
def ReporteConsolidado(maquinas, fecha_inicio, fecha_fin):
    print("<<< Reporte consolidado >>>")
    
    ids_maquinas = [i['ID'] for i in maquinas]
    
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(ids_maquinas)) &
        (df_actividad['fecha'] >= fecha_inicio) &
        (df_actividad['fecha'] <= fecha_fin)
    ]
    
    if df_filtrada.empty:
        print("No hay datos de actividad en el rango de fechas seleccionado")
        return
    
    total_in = df_filtrada['IN'].sum()
    total_out = df_filtrada['OUT'].sum()
    total_jackpot = df_actividad['JACKPOT'].sum()
    total_billetero = df_actividad['BILLETERO'].sum()
    utilidad = total_in - total_out - total_jackpot - total_billetero
    
    print(f"\nRango de fechas: {fecha_inicio.date()} a {fecha_fin.date()}")
    print(f"Maquinas incluidas: {len(ids_maquinas)}")
    print(f"IN total: {total_in}")
    print(f"OUT total: {total_out}")
    print(f"JACPOT total: {total_jackpot}")
    print(f"BILLETERO total: {total_billetero}")
    print(f"UTILIDAD total: {utilidad}")
    

