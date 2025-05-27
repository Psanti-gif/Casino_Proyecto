from fastapi import APIRouter, Query
from modulo_reportes.r_service_lugares import ReportesServiceLugares
from modulo_reportes.r_service_maquinas import ReportesServiceMaquinas

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
    
    