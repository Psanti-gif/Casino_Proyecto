#Reportes Casino
from datetime import datetime

#1. ENTRADA DE PARAMETROS


def SeleccionarMaquina(casino_id = None, estado = False):
    Maquinas_Disponibles = [{'ID': 1, 'Nombre': 'Ruleta 200', 'Tipo': 'Ruleta', 'Estado': 'Activo', 'casino_id': 1},
                            {'ID': 2, 'Nombre': 'Blackjack', 'Tipo': 'Juego de mesa', 'Estado': 'Activo', 'casino_id': 1},
                            {'ID': 3, 'Nombre': 'Zeus', 'Tipo': 'Tragamoneda', 'Estado': 'Inactivo', 'casino_id': 2}]
    
    if casino_id is not None:
        Maquinas_Disponibles = [i for i in Maquinas_Disponibles if i['casino_id'] == casino_id]
        
    if not estado:
        Maquinas_Disponibles = [i for i in Maquinas_Disponibles if i['Estado'] == 'Activo']
        
    #Salida
    print("Maquinas disponibles:")
    for m in Maquinas_Disponibles:
        print(f"{m['ID']}, {m['Nombre']}, {m['Tipo'], {m['Estado']}}")
        
    seleccion_id = input("Seleccione las maquinas a través de sus ID's (separelas con coma por favor): ")
    seleccion_id = [int(i.strip()) for i in seleccion_id.split(",")]
    
    Maquinas_seleccionada = [i for i in Maquinas_Disponibles if i['ID'] in seleccion_id]
    return Maquinas_seleccionada
    
def SeleccionarCasino(nombre=None, zona= None):
    Casinos_Disponibles = [
        {'ID': 1, 'Nombre': 'Casino Boston', 'Zona': 'Norte', 'Estado': 'Activo'},
        {'ID': 2, 'Nombre': 'Casino Robledo', 'Zona': 'Sur', 'Estado': 'Activo'},
    ]
      
    if nombre:
        Casinos_Disponibles = [i for i in Casinos_Disponibles if nombre.lower() in i['Nombre'].lower()]
        return
    
    if zona:
        Casinos_Disponibles = [i for i in Casinos_Disponibles if zona.lower() in i['Zona'].lower()]
    
    Casinos_Activos = [i for i in Casinos_Disponibles if i['Estado'] == 'Activo']
    if not Casinos_Activos:
        print("No hay casinos que coincidan con los filtros.")
        return None
    
    print("Casinos disponibles:")
    for c in Casinos_Activos:
        print(f"{c['ID']}: {c['Nombre']} - {c['Zona']}")
    
    Seleciona_ID = input("Selecciona el casino por su ID: ")
    try:
        Seleciona_ID = int(Seleciona_ID.strip())
    except ValueError:
        print("ID invalido")
        return None
    
    Casino_Seleccionado = [i for i in Casinos_Disponibles if i['ID'] == Seleciona_ID]
    if not Casino_Seleccionado:
        print("El ID ingresado no corresponde a un casino existente.")
        return None
    
    return Casino_Seleccionado[0]

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
    #Seleccionamos el casino
    Casino = SeleccionarCasino()
    if not Casino:
        print("Cancelando operacion... No se seleccionó un casino.")
        return
    #Seleccionamos maquina segun el casino
    Maquina = SeleccionarMaquina(casino_id=Casino['ID'])
    if not Maquina:
        print("No se seleccionaron maquinas validas.")
        return
    #Seleccionamos rango de fechas
    Fecha_Inicio, Fecha_Fin = SeleccionarRangoFechas()
    
    print("\nTipos de reportes disponibles:")
    print("1. Individual")
    print("2. Grupal")
    print("3. Consolidado")
    TipoReporte = input("Seleccione una opcion: ")
    
    if TipoReporte == '1':
        ReporteIndividual()
    elif TipoReporte == '2':
        ReporteGrupal()
    elif TipoReporte == '3':
        ReporteConsolidado()
    else:
        print("Opcion invalida.")
        return
    
def ReporteIndividual(maquinas, fecha_inicio, fecha_fin):
    pass

def ReporteGrupal(maquinas, fecha_inicio, fecha_fin):
    pass

def ReporteConsolidado(maquinas, fecha_inicio, fecha_fin):
    pass
    
    
        