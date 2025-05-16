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
    while True:
        try:
            Fecha_Inicio = input("Ingrese la fecha de inicio (Formato YYYY/MM/DD): ")
            Fecha_Inicio = datetime.strptime(Fecha_Inicio, "%Y-%m-%d")
            
            Fecha_Fin = input("Ingrese la fecha de fin (Formato YYYY/MM/DD): ")
            Fecha_Fin = datetime.strptime(Fecha_Fin, "%Y-%m-%d")
            
                
            if Fecha_Inicio > Fecha_Fin:
                print("La fecha de inicio no puede ser posterior a la fecha de fin.")
                continue
            
            return Fecha_Inicio, Fecha_Fin
        except ValueError:
            print("Hubo un error con el ingreso de fecha. Intente nuevamente.")

def GenerarReporte():
    print("<<< Módulo de Reportes de Casino >>>")
  
    Casino = SeleccionarCasino()
    if not Casino:
        print("Cancelando operacion... No se seleccionó un casino.")
        return
   
    Maquina = SeleccionarMaquina(casino_id=Casino['ID'])
    if not Maquina:
        print("No se seleccionaron maquinas validas.")
        return

    Fecha_Inicio, Fecha_Fin = SeleccionarRangoFechas()
    
    print("\nTipos de reportes disponibles:")
    print("1. Individual")
    print("2. Grupal")
    print("3. Consolidado")
    TipoReporte = input("Seleccione una opcion: ")
    
    if TipoReporte == '1':
        ReporteIndividual(Maquina, Fecha_Inicio, Fecha_Fin)
    elif TipoReporte == '2':
        ReporteGrupal(Maquina, Fecha_Inicio, Fecha_Fin)
    elif TipoReporte == '3':
        ReporteConsolidado(Maquina, Fecha_Inicio, Fecha_Fin)
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
    pass

def ReporteConsolidado(maquinas, fecha_inicio, fecha_fin):
    pass


