from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from datetime import date
import os
import pandas as pd
from fpdf import FPDF
import uuid
from app.modules.cuadre_casino.cuadre_casino import cuadre_casino, CuadreCasinoRequest
from app.modules.cuadre_maquina.cuadre_maquina import calcular_balance, BalanceRequest
from app.modules.gestion_lugares.lugares import cargar_lugares

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def obtener_datos_reporte(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    casino: Optional[str] = None,
    marca: Optional[str] = None,
    modelo: Optional[str] = None,
    maquinas: Optional[List[str]] = None,
):
    registros = []
    fecha_inicio_str = fecha_inicio.isoformat() if fecha_inicio else None
    fecha_fin_str = fecha_fin.isoformat() if fecha_fin else None

    if modelo and modelo.lower() in ["todos", "todas"]:
        modelo = None
    if marca and marca.lower() in ["todos", "todas"]:
        marca = None
    if maquinas and any(m.lower() in ["todos", "todas"] for m in maquinas):
        maquinas = None

    from pathlib import Path
    import json
    ruta_maquinas = Path(__file__).parent.parent / \
        "gestion_maquinas" / "maquinas.json"
    maquinas_data = {}
    if ruta_maquinas.exists():
        with open(ruta_maquinas, "r", encoding="utf-8") as f:
            maquinas_data = json.load(f)

    if modelo or marca:
        codigos_filtrados = []
        for m in maquinas_data.values():
            cumple_modelo = not modelo or m.get(
                "modelo", "").lower() == modelo.lower()
            cumple_marca = not marca or m.get(
                "marca", "").lower() == marca.lower()
            cumple_casino = not casino or m.get("casino", "").lower() == (
                casino or "").lower() or casino == "Todos"
            if cumple_modelo and cumple_marca and cumple_casino:
                codigos_filtrados.append(m["codigo"])
        if maquinas:
            maquinas = list(set(maquinas) & set(codigos_filtrados))
        else:
            maquinas = codigos_filtrados

    if (casino is None or casino == "Todos") and (not maquinas or len(maquinas) == 0):
        lugares = cargar_lugares()
        for datos in lugares.values():
            casino_nombre = datos["nombre_casino"]
            try:
                req = CuadreCasinoRequest(
                    casino=casino_nombre, fecha_inicio=fecha_inicio_str, fecha_fin=fecha_fin_str
                )
                resultado = cuadre_casino(req)
                for m in resultado["detalle_maquinas"]:
                    codigo_maquina = m["maquina"]
                    porcentaje = 0.0
                    for datos in maquinas_data.values():
                        if datos.get("codigo", "").strip().lower() == codigo_maquina.strip().lower():
                            porcentaje = float(
                                datos.get("porcentaje_participacion", 0))
                            break

                    total_in = m["total_in"]
                    total_out = m["total_out"]
                    total_jackpot = m["total_jackpot"]
                    total_billetero = m["total_billetero"]
                    utilidad = total_in + total_billetero - \
                        (total_out + total_jackpot)
                    utilidad_participante = round(
                        utilidad * (porcentaje / 100), 2)
                    utilidad_operador = round(
                        utilidad - utilidad_participante, 2)

                    registros.append({
                        "fecha_inicio": m["fecha_inicio"],
                        "fecha_fin": m["fecha_fin"],
                        "casino": casino_nombre,
                        "maquina": codigo_maquina,
                        "in": total_in,
                        "out": total_out,
                        "jackpot": total_jackpot,
                        "billetero": total_billetero,
                        "utilidad": utilidad,
                        "porcentaje_participacion": porcentaje,
                        "utilidad_participante": utilidad_participante,
                        "utilidad_operador": utilidad_operador,
                        "denominacion": m["denominacion"],
                        "contador_inicial": m["contador_inicial"],
                        "contador_final": m["contador_final"],
                    })
            except Exception as e:
                print(
                    f"Error al obtener cuadre del casino '{casino_nombre}': {e}")
                continue

    elif casino and (not maquinas or len(maquinas) == 0):
        req = CuadreCasinoRequest(
            casino=casino, fecha_inicio=fecha_inicio_str, fecha_fin=fecha_fin_str
        )
        resultado = cuadre_casino(req)
        for m in resultado["detalle_maquinas"]:
            codigo_maquina = m["maquina"]
            porcentaje = 0.0
            for datos in maquinas_data.values():
                if datos.get("codigo", "").strip().lower() == codigo_maquina.strip().lower():
                    porcentaje = float(
                        datos.get("porcentaje_participacion", 0))
                    break

            total_in = m["total_in"]
            total_out = m["total_out"]
            total_jackpot = m["total_jackpot"]
            total_billetero = m["total_billetero"]
            utilidad = total_in + total_billetero - (total_out + total_jackpot)
            utilidad_participante = round(utilidad * (porcentaje / 100), 2)
            utilidad_operador = round(utilidad - utilidad_participante, 2)

            registros.append({
                "fecha_inicio": m["fecha_inicio"],
                "fecha_fin": m["fecha_fin"],
                "casino": casino,
                "maquina": codigo_maquina,
                "in": total_in,
                "out": total_out,
                "jackpot": total_jackpot,
                "billetero": total_billetero,
                "utilidad": utilidad,
                "porcentaje_participacion": porcentaje,
                "utilidad_participante": utilidad_participante,
                "utilidad_operador": utilidad_operador,
                "denominacion": m["denominacion"],
                "contador_inicial": m["contador_inicial"],
                "contador_final": m["contador_final"],
            })

    elif maquinas:
        for maquina in maquinas:
            req = BalanceRequest(
                fecha_inicio=fecha_inicio_str,
                fecha_fin=fecha_fin_str,
                casino=casino or "",
                maquina=maquina,
                id=maquina,
                denominacion=1.0
            )
            resultado = calcular_balance(req)
            for r in resultado["cuadres"]:
                porcentaje = 0.0
                for datos in maquinas_data.values():
                    if datos.get("codigo", "").strip().lower() == maquina.strip().lower():
                        porcentaje = float(
                            datos.get("porcentaje_participacion", 0))
                        break
                utilidad = r["utilidad"]
                utilidad_participante = round(utilidad * (porcentaje / 100), 2)
                utilidad_operador = round(utilidad - utilidad_participante, 2)

                registros.append({
                    "fecha_inicio": r["fecha_inicio"],
                    "fecha_fin": r["fecha_fin"],
                    "casino": r["casino"],
                    "maquina": r["maquina"],
                    "in": r["total_in"],
                    "out": r["total_out"],
                    "jackpot": r["total_jackpot"],
                    "billetero": r["total_billetero"],
                    "utilidad": utilidad,
                    "porcentaje_participacion": porcentaje,
                    "utilidad_participante": utilidad_participante,
                    "utilidad_operador": utilidad_operador,
                    "contador_inicial": r["contador_inicial"],
                    "contador_final": r["contador_final"],
                })
    return registros


@router.get("/generar-reporte")
def generar_reporte(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    casino: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None),
    maquinas: Optional[List[str]] = Query(None),
):
    try:
        registros = obtener_datos_reporte(
            fecha_inicio, fecha_fin, casino, marca, modelo, maquinas)
        if not registros:
            return JSONResponse(status_code=404, content={"error": "No se encontraron registros"})
        return {"registros": registros}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error interno del servidor: {str(e)}"})
