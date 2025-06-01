from fastapi import APIRouter, Query, Body
from app.modules.modulo_reportes.r_service_lugares import ReportesServiceLugares
from app.modules.modulo_reportes.r_service_maquinas import ReportesServiceMaquinas
from app.modules.modulo_reportes.r_service_individual import ReportesServiceIndividual
from app.modules.modulo_reportes.r_service_consolidado import ReportesServiceConsolidado
from app.modules.modulo_reportes.r_service_grupo import ReportesServiceGrupo
from app.modules.modulo_reportes.r_service_participacion import ReportesServiceParticipacion
from app.modules.modulo_reportes.exportador_reportes import ExportadorReportes
from typing import List
from fastapi.responses import FileResponse
import os
import uuid

router = APIRouter(tags=["Modulo de Reportes"])

#Reporte de casinos por ciudad
@router.get("/reportes/casinos")
def obtener_casinos(ciudad: str = Query(None)):
    return ReportesServiceLugares.obtener_casinos(ciudad=ciudad)

#Reporte de maquina por filtros avanzados
@router.get("/reportes/maquinas")
def filtrar_maquinas(
    marca: str = Query(None),
    modelo: str = Query(None),
    casino: str = Query(None),
    ciudad: str = Query(None)
):
    return ReportesServiceMaquinas.filtrar_maquinas(
        marca=marca,
        modelo=modelo,
        casino=casino,
        ciudad=ciudad
    )
    
@router.get("/reportes/individual")
def obtener_reporte_individual(
    fecha_inicio: str = Query(...),
    fecha_fin: str = Query(...),
    casino: str = Query(...),
    maquina: str = Query(...),
    denominacion: float = Query(...)
):
    return ReportesServiceIndividual.generar_reporte_individual(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        casino=casino,
        maquina=maquina,
        denominacion=denominacion
    )
    

@router.get("/reportes/consolidado")
def obtener_reporte_consolidado(
    casino: str = Query(...),
    fecha_inicio: str = Query(...),
    fecha_fin: str = Query(...)
):
    return ReportesServiceConsolidado.generar_reporte_consolidado(
        casino=casino,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


@router.post("/reportes/grupo")
def obtener_reporte_por_grupo(
    maquinas: List[str] = Body(...),
    fecha_inicio: str = Query(...),
    fecha_fin: str = Query(...),
    casino: str = Query(...),
    denominaciones: dict = Body(...)
):
    return ReportesServiceGrupo.generar_reporte_grupal(
        maquinas=maquinas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        denominaciones=denominaciones,
        casino=casino
    )
    
@router.post("/reportes/participacion")
def obtener_reporte_participacion(
    maquinas: List[str] = Body(...),
    fecha_inicio: str = Query(...),
    fecha_fin: str = Query(...),
    casino: str = Query(...),
    denominaciones: dict = Body(...),
    porcentaje: float = Query(...)
):
    return ReportesServiceParticipacion.generar_reporte_participacion(
        maquinas=maquinas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        denominaciones=denominaciones,
        casino=casino,
        porcentaje = porcentaje
    )
    

@router.post("/reportes/exportar")
def exportar_reporte(
    data: dict = Body(...),
    formato: str = Query(..., description="pdf o excel")
):
    nombre_archivo = f"reporte_{uuid.uuid4().hex[:8]}"

    if formato.lower() == "pdf":
        ruta = ExportadorReportes.exportar_a_pdf(data, nombre_archivo)
    elif formato.lower() == "excel":
        ruta = ExportadorReportes.exportar_a_excel(data, nombre_archivo)
    else:
        return {"error": "Formato no soportado. Usa 'pdf' o 'excel'."}

    return FileResponse(path=ruta, filename=os.path.basename(ruta), media_type="application/octet-stream")


import smtplib
from email.message import EmailMessage

def enviar_email_con_adjunto(destinatario, archivo_adjunto, formato):
    remitente = "samuxbass200424@gmail.com"
    password = "uogv ekis tyie kwjg"
    nombre_remitente = "Sistema Casino"

    asunto = f"Reporte del Sistema Casino ({formato.upper()})"
    cuerpo = "Hola,\n\nAdjunto encontrarás el reporte solicitado desde el sistema Casino.\n\nSaludos."

    mensaje = EmailMessage()
    mensaje["From"] = f"{nombre_remitente} <{remitente}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)

    with open(archivo_adjunto, "rb") as f:
        contenido = f.read()
        nombre = os.path.basename(archivo_adjunto)
        tipo_mime = "application/pdf" if formato == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        mensaje.add_attachment(contenido, maintype="application", subtype=tipo_mime.split("/")[-1], filename=nombre)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remitente, password)
        smtp.send_message(mensaje)

from app.modules.modulo_reportes.exportador_reportes import ExportadorReportes
@router.post("/reportes/enviar-email")
def enviar_reporte_por_email(
    data: dict = Body(...),
    formato: str = Query(..., description="pdf o excel"),
    destinatario: str = Query(...)
):
    nombre_archivo = f"reporte_{uuid.uuid4().hex[:8]}"
    ruta = ExportadorReportes.exportar_a_pdf(data, nombre_archivo) if formato == "pdf" else ExportadorReportes.exportar_a_excel(data, nombre_archivo)

    try:
        enviar_email_con_adjunto(destinatario, ruta, formato)
        return {"mensaje": f"Reporte enviado exitosamente a {destinatario}"}
    except Exception as e:
        return {"error": str(e)}


from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Usa el mismo scheduler global que en main.py
scheduler = BackgroundScheduler()
scheduler.start()

def tarea_programada_enviar_reporte(destinatario, formato, data):
    nombre_archivo = f"reporte_{uuid.uuid4().hex[:8]}"
    ruta = ExportadorReportes.exportar_a_pdf(data, nombre_archivo) if formato == "pdf" else ExportadorReportes.exportar_a_excel(data, nombre_archivo)
    enviar_email_con_adjunto(destinatario, ruta, formato)

@router.post("/reportes/programar-envio")
def programar_envio_reporte(
    data: dict = Body(...),
    formato: str = Query(...),
    destinatario: str = Query(...),
    fecha: str = Query(..., description="Formato: YYYY-MM-DD HH:MM")
):
    try:
        fecha_programada = datetime.strptime(fecha, "%Y-%m-%d %H:%M")

        scheduler.add_job(
            tarea_programada_enviar_reporte,
            trigger='date',
            run_date=fecha_programada,
            args=[destinatario, formato, data]
        )

        return {"mensaje": f"Envío programado para {fecha_programada} a {destinatario}"}

    except Exception as e:
        return {"error": str(e)}
