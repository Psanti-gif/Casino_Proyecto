#Reportes Casino


#1. ENTRADA DE PARAMETROS

def SeleccionarMaquina(casino_id = None, estado = False):
    Maquinas_Disponibles = [{'ID': 1, 'Nombre': 'Ruleta 200', 'Tipo': 'Ruleta', 'Estado': 'Activo'},
                            {'ID': 2, 'Nombre': 'Blackjack', 'Tipo': 'Juego de mesa', 'Estado': 'Activo'},
                            {'ID': 3, 'Nombre': 'Zeus', 'Tipo': 'Tragamoneda', 'Estado': 'Inactivo'}]
    
    #Filtros
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
    
def SeleccionarCasino():
    pass
    

        
    
    