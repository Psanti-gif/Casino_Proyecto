#Reportes Casino
from datetime import datetime
import pandas as pd
from Cargar_Datos import cargar_datos_actividad, cargar_datos_casino
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import schedule
import threading
import time
import mimetypes
import os

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
    total_jackpot = df_filtrada['JACKPOT'].sum()
    total_billetero = df_filtrada['BILLETERO'].sum()
    utilidad = total_in - total_out - total_jackpot - total_billetero
    
    print(f"\nRango de fechas: {fecha_inicio.date()} a {fecha_fin.date()}")
    print(f"Maquinas incluidas: {len(ids_maquinas)}")
    print(f"IN total: {total_in}")
    print(f"OUT total: {total_out}")
    print(f"JACPOT total: {total_jackpot}")
    print(f"BILLETERO total: {total_billetero}")
    print(f"UTILIDAD total: {utilidad}")
    
def ExportToPDF(name, maquinas, fecha_in, fecha_fin, tipo_reporte, df_actividad):
    tipo_reporte = tipo_reporte.lower()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size= 12)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(200, 10, txt='REPORTE DE ACTIVIDAD DE MAQUINAS', ln=True, align='C')
    
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, txt=f"Tipo de reporte: {tipo_reporte.upper()}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Fecha: {fecha_in.date()} a {fecha_fin.date()}", ln=True, align='C')
    pdf.ln(10)
    
    ids_maquinas = [i['ID'] for i in maquinas]
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(ids_maquinas)) &
        (df_actividad['fecha'] >= fecha_in) &
        (df_actividad['fecha'] <= fecha_fin)
    ]
    
    if df_filtrada.empty:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 10, txt='No hay datos de actividad en este rango de fechas', ln=True)
        pdf.output(name)
        print(f"PDF generado sin datos: {name}")
        return
    pdf.set_text_color(0,0,0)
    
    if tipo_reporte == 'consolidado':
        total_in = df_filtrada['IN'].sum()
        total_out = df_filtrada['OUT'].sum()
        total_jackpot = df_filtrada['JACKPOT'].sum()
        total_billetero = df_filtrada['BILLETERO'].sum()
        utilidad = total_in - total_out - total_jackpot - total_billetero
        
        pdf.set_text_color(0,0,0)
        pdf.cell(200, 10, txt=f'Maquinas incluidas: {len(ids_maquinas)}', ln=True)
        pdf.cell(200, 10, txt=f'IN total: {total_in}', ln=True)
        pdf.cell(200, 10, txt=f'OUT total: {total_out}', ln=True)
        pdf.cell(200, 10, txt=f'JACKPOT total: {total_jackpot}', ln=True)
        pdf.cell(200, 10, txt=f'BILLETERO total: {total_billetero}', ln=True)
        pdf.cell(200, 10, txt=f'UTILIDAD total: {utilidad}', ln=True)
    
    elif tipo_reporte == 'individual':
        for i in maquinas:
            mid = i['ID']
            datos = df_filtrada[df_filtrada['maquina_id'] == mid]
            if datos.empty:
                continue
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(200, 10, txt=f'Maquina ID: {mid}', ln=True)
            pdf.set_font('Arial', 'B', size=12)
            pdf.cell(200, 10, txt=f'Marca: {i['marca']}, Modelo: {i['modelo']}', ln=True)
            pdf.cell(200, 10, txt=f'IN: {datos['IN'].sum()}, OUT: {datos['OUT'].sum()}, JACKPOT: {datos['JACKPOT'].sum()}, BILLETERO: {datos['BILLETERO'].sum()}', ln=True)
            utilidad = datos['IN'].sum() - datos['OUT'].sum() - datos['JACKPOT'].sum() - datos['BILLETERO'].sum()
            pdf.cell(200, 10, txt=f'UTILIDAD: {utilidad}', ln=True)
            pdf.ln(5)
    
    elif tipo_reporte == 'grupal':
        group = df_filtrada.groupby('maquina_id').sum(numeric_only=True)
        for i in group.index:
            maquina = next((m for m in maquinas if m['ID'] == i), None)
            if not maquina:
                continue
            row = group.loc[i]
            utilidad = row['IN'] - row['OUT'] - row['JACKPOT'] - row['BILLETERO']
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(200, 10, txt=f'Maquina ID: {i}', ln=True)
            pdf.set_font('Arial', 'B', size=12)
            pdf.cell(200, 10, txt=f'Marca: {maquina['marca']}, Modelo: {maquina['Modelo']}', ln=True)
            pdf.cell(200, 10, txt=f"IN: {row['IN']}, OUT: {row['OUT']}, JACKPOT: {row['JACKPOT']}, BILLETERO: {row['BILLETERO']}", ln=True)
            pdf.cell(200, 10, txt=f'UTILIDAD: {utilidad}', ln=True)
            pdf.ln(5)
    else:
        pdf.cell(200, 10, txt='Tipo de reporte no soportado', ln=True)
            
    pdf.output(name)
    print(f"PDF generado exitosamente!: {name}")
    
def ExportToExcel(name, maquinas, fecha_in, fecha_fin, tipo_reporte, df_actividad):
    tipo_reporte = tipo_reporte.lower()
    
    ids_maquinas = [i['ID'] for i in maquinas]
    
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(ids_maquinas)) &
        (df_actividad['fecha'] >= fecha_in) &
        (df_actividad['fecha'] <= fecha_fin)
    ]
    
    if df_filtrada.empty:
        print("No hay datos de actividad en este rango de fechas")
        return
    
    if tipo_reporte == 'consolidado':
        total_in = df_filtrada['IN'].sum()
        total_out = df_filtrada['OUT'].sum()
        total_jackpot = df_filtrada['JACKPOT'].sum()
        total_billetero = df_filtrada['BILLETERO'].sum()
        utilidad = total_in - total_out - total_jackpot - total_billetero
        
        df_resumen = pd.DataFrame([{
            'Maquinas incluidas': len(ids_maquinas),
            'IN total': total_in,
            'OUT total': total_out,
            'JACKPOT total': total_jackpot,
            'BILLETERO total': total_billetero,
            'UTILIDAD total': utilidad
        }])
        df_resumen.to_excel(name, index=False)
        print("Excel generado exitosamente:", name)
        return
    
    elif tipo_reporte == 'individual':
        filas = []
        for i in maquinas:
            mid = i['ID']
            datos = df_filtrada[df_filtrada['maquina_id'] == mid]
            if datos.empty:
                continue
            in_total = datos['IN'].sum()
            out_total = datos['OUT'].sum()
            jackpot_total = datos['JACKPOT'].sum()
            billetero_total = datos['BILLETERO'].sum()
            utilidad = in_total - out_total - jackpot_total - billetero_total
            
            filas.append({
                'ID': mid,
                'Marca': i['Marca'],
                'Modelo': i['Modelo'],
                'IN': in_total,
                'OUT': out_total,
                'JACKPOT': jackpot_total,
                'BILLETERO': billetero_total,
                'UTILIDAD' : utilidad
            })
        df_resultado = pd.DataFrame(filas)
        df_resultado.to_excel(name, index= False)
        print("Excel generado exitosamente: ", name)
        return
    elif tipo_reporte == 'grupal':
        group = df_filtrada.groupby('maquina_id').sum(numeric_only = True)
        filas = []
        for i in group.index:
            maquina = next((m for m in maquinas if m['ID'] == i), None)
            if not maquina:
                continue
            row = group.loc[i]
            utilidad = row['IN'] - row['OUT'] - row['JACKPOT'] - row['BILLETERO']
            
            filas.append({
                'ID': i,
                'Marca': maquina['Marca'],
                'Modelo': maquina['Modelo'],
                'IN': row['IN'],
                'OUT': row['OUT'],
                'JACKPOT': row['JACKPOT'],
                'BILLETERO': row['BILLETERO'],
                'UTILIDAD': utilidad
            })
        df_resultado = pd.DataFrame(filas)
        df_resultado.to_excel(name, index=False)
        print("Excel generado con exito:", name)
        return
    else:
        print("Tipo de reporte no soportado")

def SendEmail(
    remitente_correo,
    remitente_nombre,
    contraseña_app,
    destinarios,
    asunto,
    cuerpo,
    archivo_adjunto,
    nombre_mostrado = None,
    servidor = 'smtp.gmail.com',
    puerto = 587
):
    if not os.path.exists(archivo_adjunto):
        print(f"El archivo '{archivo_adjunto}' no existe")
        return
    
    msg = EmailMessage()
    msg['From'] = formataddr((remitente_nombre or remitente_correo, remitente_correo))
    msg['To'] = ', '.join(destinarios)
    msg['Subject'] = asunto
    msg.set_content(cuerpo)
    
    with open(archivo_adjunto, 'rb') as f:
        nombre_archivo = nombre_mostrado or os.path.basename(archivo_adjunto)
        msg.add_attachment(f.read(), maintype = 'application', subtype = 'octet-stream', filename = nombre_archivo)
    try:
        with smtplib.SMTP(servidor, puerto) as smtp:
            smtp.starttls()
            smtp.login(remitente_correo, contraseña_app)
            smtp.send_message(msg)
            print(f"Correo enviado a {', '.join(destinarios)}.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        
def ProgramarEnvioAutomatico(name, tipo, maquinas, fecha_in, fecha_fin, df_actividad, correo_destino, frecuencia= 'diario', hora= '08:00'):
    def tarea():
        print(f"Ejecutando envio automatico {tipo.upper()} a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if tipo == 'pdf':
            ExportToPDF(name, maquinas, fecha_in, fecha_fin, 'consolidado', df_actividad)
        elif tipo == 'excel':
            ExportToExcel(name, maquinas, fecha_in, fecha_fin, 'consolidado', df_actividad)
        else:
            print("Tipo de reporte invalido")
            return
        
        SendEmail(
            remitente_correo="tucorreo@gmail.com",
            remitente_nombre="CasinoApp",
            contraseña_app="tupassword_o_clave_app",
            destinatarios=correo_destino,
            asunto=f"Reporte automático ({tipo.upper()})",
            cuerpo=f"Este es un reporte automático generado por CasinoApp.",
            archivo_adjunto=name
        )
    
    if frecuencia == 'diario':
        schedule.every().day.at(hora).do(tarea)
    elif frecuencia == 'semanal':
        schedule.every().friday.at(hora).do(tarea)
    elif frecuencia == 'mensual':
        schedule.every().day.at(hora).do(lambda: tarea() if datetime.now().day == 1 else None)
    else:
        print("Frencuencia no soportada")
        return
    
    def programador():
        print("Envio automatico programado...")
        while True:
            schedule.run_pending()
            time.sleep(60)
    threading.Thread(target=programador, daemon=True).start()
    
def GenerarReporteParticipacion(
    df_maquinas,
    df_actividad,
    maquinas_seleccionadas,
    porcentaje_participacion,
    fecha_inicio,
    fecha_fin
):
    if not maquinas_seleccionadas:
        print("Debes seleccionar alguna maquina")
        return
    
    df_actividad['fecha'] = pd.to_datetime(df_actividad['fecha'])
    df_filtrado = df_actividad[
        (df_actividad['maquina_id'].isin(maquinas_seleccionadas)) &
        (df_actividad['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (df_actividad['fecha'] <= pd.to_datetime(fecha_fin))
    ].copy()
    
    if df_filtrado.empty:
        print("No se encontraron registros")
        return
    
    df_filtrado['UTILIDAD'] = df_filtrado['IN'] - (df_filtrado['OUT'] + df_filtrado['JACKPOT'] + df_filtrado['BILLETERO'])
    
    Utilidad_total = df_filtrado['UTILIDAD'].sum()
    valor_participacion = Utilidad_total * porcentaje_participacion
    
    detalle_maquina = df_maquinas[df_maquinas['ID'].isin(maquinas_seleccionadas)].copy()
    
    reporte = {
        'maquinas_incluidas': detalle_maquina,
        'utilidad_total': Utilidad_total,
        'porcentaje_participacion': porcentaje_participacion,
        'valor_participacion': valor_participacion,
        'detalle_contadores': df_filtrado
    }
    print("Reporte de participacion generado correctamente")
    return reporte
        
        
        
