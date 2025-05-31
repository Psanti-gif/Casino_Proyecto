from fastapi import APIRouter, Query, Body
from modulo_reportes.r_service_lugares import ReportesServiceLugares
from modulo_reportes.r_service_maquinas import ReportesServiceMaquinas
from modulo_reportes.r_service_individual import ReportesServiceIndividual
from modulo_reportes.r_service_consolidado import ReportesServiceConsolidado
from modulo_reportes.r_service_grupo import ReportesServiceGrupo
from typing import List

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