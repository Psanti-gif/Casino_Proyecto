#ReportesLogic
from datetime import datetime, date
from Cargar_Datos import cargar_datos_actividad, cargar_datos_casino
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import schedule
import threading
import time
import os

######
from fastapi import APIRouter, Query
from typing import Optional, List
import pandas as pd
import tempfile
from fastapi.responses import FileResponse

router =  APIRouter(prefix="/reportes", tags=["Reportes"])

df_actividad = cargar_datos_actividad()
df_maquinas = cargar_datos_casino()

@router.get("/maquinas")
def SeleccionarMaquina(
    casino_id: Optional[int] = Query(None),
    incluir_inactivos: bool = Query(False),
    ids_seleccionados: Optional[List[int]] = Query(None)
):
    df = df_maquinas.copy()
    if casino_id is not None:
        df = df[df['casino_id'] == casino_id]
    if not incluir_inactivos:
        df = df[df['Estado'].str.lower() ==  'activo']
    if ids_seleccionados:
        df = df[df['ID'].isin(ids_seleccionados)]
        
    return df.to_dict('records')

@router.get('/casinos')
def SeleccionarCasino(
    nombre: Optional[str] = Query(None),
    zona: Optional[str] = Query(None)
):
    df = df_maquinas[['casino_id', 'casino_nombre', 'zona']].drop_duplicates()
    
    if nombre:
        df = df[df['casino_nombre'].str.contains(nombre, case=False, na=False)]
    if zona:
        df = df[df['zona'].str.contains(zona, case=False, na=False)]
    return df.to_dict('records')
    
@router.get('/fechas_disponibles')            
def SeleccionarRangoFechas():
    fechas = pd.to_datetime(df_actividad['fecha'])
    return{
        'fecha_min': fechas.min().date(),
        'fecha_max': fechas.max().date()
    }
    
@router.get('/maquinas/filtros-avanzados')
def FiltrosAvanazados(
    zona: Optional[str] = Query(None),
    casino: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None)
):
    df = df_maquinas.copy()
    
    if zona:
        df = df[df['zona'] == zona]
    if casino:
        df = df[df['casino_nombre'] == casino]
    if tipo:
        df = df[df['Tipo'] == tipo]
    if marca:
        df = df[df['Marca'] == marca]
    if modelo:
        df = df[df['Modelo'] == modelo]
    return df.to_dict('records')

router.get('/individual')    
def ReporteIndividual(
    maquina_ids: List[int] = Query(...),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...)
):
    resultados = []
    for id_maquina in maquina_ids:
        maquina = df_maquinas[df_maquinas['ID'] == id_maquina]
        if maquina.empty:
            continue
        nombre = maquina.iloc[0]['Nombre']
        tipo = maquina.iloc[0]['Tipo']
        
        df_filtrada = df_actividad[
            (df_actividad['maquina_id'] == id_maquina) &
            (df_actividad['fecha'] >= fecha_inicio) &
            (df_actividad['fecha'] <= fecha_fin)
        ]
        
        if df_filtrada.empty:
            resultados.append({
                'id': id_maquina,
                'nombre': nombre,
                'tipo': tipo,
                'mensaje': 'Sin actividad en el rango de fechas'
            }) 
            continue
        
        total_in = df_filtrada['IN'].sum()
        total_out = df_filtrada['OUT'].sum()
        total_jackpot = df_filtrada['JACKPOT'].sum()
        total_billetero = df_filtrada['BILLETERO'].sum()
        utilidad = total_in - total_out - total_jackpot - total_billetero
        
        resultados.append({
            'id': id_maquina,
            'nombre': nombre,
            'tipo': tipo,
            'in': total_in,
            'out': total_out,
            'jackpot': total_jackpot,
            'billetero': total_billetero,
            'utilidad': utilidad
        })
    return resultados
        
router.get('/grupal')
def ReporteGrupal(
    maquina_ids: List[int] = Query(...),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...)
):
    df_maquinas_filtradas = df_maquinas[df_maquinas['ID'].isin(maquina_ids)]
    
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(maquina_ids)) &
        (df_actividad['fecha'] >= fecha_inicio) &
        (df_actividad['fecha'] <=fecha_fin)
    ]
    
    if df_filtrada.empty:
        return {"mensaje": "No hay actividad en el rango de fechas."}
    
    df_merged = df_filtrada.merge(df_maquinas_filtradas, left_on = 'maquina_id', right_on = 'ID')
    resumen = df_merged.groupby('Tipo').agg({
        'IN': 'sum',
        'OUT': 'sum',
        'JACKPOT': 'sum',
        'BILLETERO': 'sum'
    }).reset_index()
    
    resumen['UTILIDAD'] = resumen['IN'] - resumen['OUT'] - resumen['JACKPOT'] - resumen['BILLETERO']
    return resumen.to_dict(orient='records')

@router.get('/consolidado')    
def ReporteConsolidad(
    maquina_ids: List[int] = Query(...),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...)
):
    
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(maquina_ids)) &
        (df_actividad['fecha'] >= fecha_inicio) &
        (df_actividad['fecha'] <= fecha_fin)
    ]
    
    if df_filtrada.empty:
        return {"mensaje": "No hay datos de actividad en el rango de fechas."}
    
    total_in = df_filtrada['IN'].sum()
    total_out = df_filtrada['OUT'].sum()
    total_jackpot = df_filtrada['JACKPOT'].sum()
    total_billetero = df_filtrada['BILLETERO'].sum()
    utilidad = total_in - total_out - total_jackpot - total_billetero
    
    return {
        'rango_fechas':{
            'inicio': fecha_inicio,
            'fin': fecha_fin
        },
        'maquinas_incluidas': len(maquina_ids),
        'in_total': total_in,
        'out_total': total_out,
        'jackpot_total': total_jackpot,
        'billetero_total': total_billetero,
        'utilidad_total': utilidad
    }
    
@router.get('/exportar/pdf')
def ExportToPDF(
    maquina_ids: List[int] = Query(...),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    tipo_reporte: str = Query(...)
):
    
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(maquina_ids)) &
        (df_actividad['fecha'] >= fecha_inicio) &
        (df_actividad['fecha'] <= fecha_fin)
    ]
    
    if df_filtrada.empty:
        return {"mensaje": "No hay datos de actividad en el rango de fechas"}
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(200, 10, txt='REPORTE DE ACTIVIDAD DE MAQUINAS', ln=True, align='C')
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, txt=f"Tipo de reporte: {tipo_reporte.upper()}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Rango de fechas: {fecha_inicio.date()} a {fecha_fin.date()}", ln=True, align='C')
    pdf.ln(10)
    
    if tipo_reporte == 'consolidado':
        total_in = df_filtrada['IN'].sum()
        total_out = df_filtrada['OUT'].sum()
        total_jackpot = df_filtrada['JACKPOT'].sum()
        total_billetero = df_filtrada['BILLETERO'].sum()
        utilidad = total_in - total_out - total_jackpot - total_billetero
        
        pdf.cell(200, 10, txt=f'IN total: {total_in}', ln=True)
        pdf.cell(200, 10, txt=f'OUT total: {total_out}', ln=True)
        pdf.cell(200, 10, txt=f'JACKPOT total: {total_jackpot}', ln=True)
        pdf.cell(200, 10, txt=f'BILLETERO total: {total_billetero}', ln=True)
        pdf.cell(200, 10, txt=f'UTILIDAD total: {utilidad}', ln=True)
    
    elif tipo_reporte == 'individual':
        for mid in maquina_ids:
            datos = df_filtrada[df_filtrada['maquina_id'] == mid]
            if datos.empty:
                continue
            
            maquina = df_maquinas[df_maquinas['ID'] == mid].iloc[0]
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(200, 10, txt=f'Máquina ID: {mid} - {maquina["Nombre"]}', ln=True)
            pdf.set_font('Arial', 'B', size=12)
            pdf.cell(200, 10, txt=f'Marca: {maquina["Marca"]}, Modelo: {maquina["Modelo"]}', ln=True)
            pdf.cell(200, 10, txt=f'IN: {datos['IN'].sum()}, OUT: {datos['OUT'].sum()}, JACKPOT: {datos['JACKPOT'].sum()}, BILLETERO: {datos['BILLETERO'].sum()}', ln=True)
            utilidad = datos['IN'].sum() - datos['OUT'].sum() - datos['JACKPOT'].sum() - datos['BILLETERO'].sum()
            pdf.cell(200, 10, txt=f'UTILIDAD: {utilidad}', ln=True)
            pdf.ln(5)
    
    elif tipo_reporte == 'grupal':
        df_maquinas_filtradas = df_maquinas[df_maquinas['ID'].isin(maquina_ids)]
        df_merged = df_filtrada.merge(df_maquinas_filtradas, left_on='maquina_id', right_on='ID')
        resumen = df_merged.groupby('Tipo').agg({
            'IN': 'sum',
            'OUT': 'sum',
            'JACKPOT': 'sum',
            'BILLETERO': 'sum'
        }).reset_index()
        resumen =['UTILIDAD'] = resumen['IN'] - resumen['OUT'] - resumen['JACKPOT'] - resumen['BILLETERO']
        
        for _, fila in resumen.iterrows():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(200, 10, txt=f"Tipo: {fila['Tipo']}", ln=True)
            pdf.set_font('Arial', '', 12)
            pdf.cell(200, 10, txt=f"IN: {fila['IN']}, OUT: {fila['OUT']}, JACKPOT: {fila['JACKPOT']}, BILLETERO: {fila['BILLETERO']}", ln=True)
            pdf.cell(200, 10, txt=f"UTILIDAD: {fila['UTILIDAD']}", ln=True)
            pdf.ln(5)
    else:
        return {"mensaje": "Tipo de reporte no soportado. Usa Individual, Grupal o Consolidado"}
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        path = tmp.name
        pdf.output(path)
    
    return FileResponse(path, media_type='application/pdf', filename='reporte.pdf')

@router.post("/exportar/excel")
def ExportToExcel(
    maquina_ids: List[int] = Query(...),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    tipo_reporte: str = Query(...)
):
    
    df_filtrada = df_actividad[
        (df_actividad['maquina_id'].isin(maquina_ids)) &
        (df_actividad['fecha'] >= fecha_inicio) &
        (df_actividad['fecha'] <= fecha_fin)
    ]
    
    if df_filtrada.empty:
        return{'mensaje': 'No hay datos de actividad en el rango de fechas'}
    
    if tipo_reporte.lower() == 'consolidado':
        total_in = df_filtrada['IN'].sum()
        total_out = df_filtrada['OUT'].sum()
        total_jackpot = df_filtrada['JACKPOT'].sum()
        total_billetero = df_filtrada['BILLETERO'].sum()
        utilidad = total_in - total_out - total_jackpot - total_billetero
        
        df_resumen = pd.DataFrame([{
            'Maquinas incluidas': len(maquina_ids),
            'IN total': total_in,
            'OUT total': total_out,
            'JACKPOT total': total_jackpot,
            'BILLETERO total': total_billetero,
            'UTILIDAD total': utilidad
        }])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            path = tmp.name
            df_resumen.to_excel(path, index=False)
            
        return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="reporte.xlsx")
            
    elif tipo_reporte.lower() == 'individual':
        filas = []
        for mid in maquina_ids:
            datos = df_filtrada[df_filtrada['maquina_id'] == mid]
            if datos.empty:
                continue
            maquina = df_maquinas[df_maquinas['ID'] == mid].iloc[0]
            filas.append({
                'ID': mid,
                'Nombre': maquina['Nombre'],
                'Marca': maquina['Marca'],
                'Modelo': maquina['Modelo'],
                'IN': datos['IN'].sum(),
                'OUT':datos['OUT'].sum(),
                'JACKPOT': datos['JACKPOT'].sum(),
                'BILLETERO': datos['BILLETERO'].sum(),
                'UTILIDAD': datos['IN'].sum() - datos['OUT'].sum() - datos['JACKPOT'].sum() - datos['BILLETERO'].sum()
            })
            
        df_resultado = pd.DataFrame(filas)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            path = tmp.name
            df_resultado.to_excel(path, index=False)
        return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="reporte.xlsx")
    
    elif tipo_reporte.lower() == 'grupal':
        df_maquinas_filtradas = df_maquinas[df_maquinas['ID'].isin(maquina_ids)]
        df_merged = df_filtrada.merge(df_maquinas_filtradas, left_on='maquina_id', right_on='ID')
        resumen = df_merged.groupby('Tipo').agg({
            'IN': 'sum',
            'OUT': 'sum',
            'JACKPOT': 'sum',
            'BILLETERO': 'sum'
        }).reset_index()
        resumen['UTILIDAD'] = resumen['IN'] - resumen['OUT'] - resumen['JACKPOT'] - resumen['BILLETERO']
       
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
           path = tmp.name()
           resumen.to_excel(path, index=False)
        return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="reporte.xlsx")
    else:
        return {"mensaje": "Tipo de reporte no soportado. Usa Individual, Grupal o Consolidado"}
       
  
       
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