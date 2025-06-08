from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from datetime import date
from pathlib import Path
import uuid
import json
import pandas as pd
from fpdf import FPDF

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

    # Cargar máquinas
    ruta_maquinas = Path(__file__).parent.parent / \
        "gestion_maquinas" / "maquinas.json"
    maquinas_data = {}
    if ruta_maquinas.exists():
        with open(ruta_maquinas, "r", encoding="utf-8") as f:
            maquinas_data = json.load(f)

    # Filtrar por marca y modelo si se especifica
    if modelo or marca:
        codigos_filtrados = []
        for m in maquinas_data.values():
            if (
                (not modelo or m.get("modelo", "").lower() == modelo.lower()) and
                (not marca or m.get("marca", "").lower() == marca.lower()) and
                (not casino or m.get("casino", "").lower()
                 == casino.lower() or casino == "Todos")
            ):
                codigos_filtrados.append(m["codigo"])
        if maquinas:
            maquinas = list(set(maquinas) & set(codigos_filtrados))
        else:
            maquinas = codigos_filtrados

    def calcular_utilidades(m, casino_nombre):
        codigo_maquina = m["maquina"]
        total_in = m["total_in"]
        total_out = m["total_out"]
        total_jackpot = m["total_jackpot"]
        total_billetero = m["total_billetero"]
        utilidad = total_in + total_billetero - (total_out + total_jackpot)

        porcentaje = float(next(
            (datos.get("porcentaje_participacion", 0)
             for datos in maquinas_data.values()
             if datos.get("codigo", "").strip().lower() == codigo_maquina.strip().lower()),
            0.0
        ))

        utilidad_participante = round(utilidad * (porcentaje / 100), 2)
        utilidad_operador = round(utilidad - utilidad_participante, 2)

        return {
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
            "denominacion": m.get("denominacion"),
            "contador_inicial": m.get("contador_inicial"),
            "contador_final": m.get("contador_final"),
        }

    # Lógica de generación de reportes
    if (casino is None or casino == "Todos") and not maquinas:
        for datos in cargar_lugares().values():
            nombre = datos["nombre_casino"]
            try:
                res = cuadre_casino(CuadreCasinoRequest(
                    casino=nombre, fecha_inicio=fecha_inicio_str, fecha_fin=fecha_fin_str))
                for m in res["detalle_maquinas"]:
                    registros.append(calcular_utilidades(m, nombre))
            except:
                continue

    elif casino and not maquinas:
        res = cuadre_casino(CuadreCasinoRequest(
            casino=casino, fecha_inicio=fecha_inicio_str, fecha_fin=fecha_fin_str))
        for m in res["detalle_maquinas"]:
            registros.append(calcular_utilidades(m, casino))

    elif maquinas:
        for maquina in maquinas:
            res = calcular_balance(BalanceRequest(
                fecha_inicio=fecha_inicio_str,
                fecha_fin=fecha_fin_str,
                casino=casino or "",
                maquina=maquina,
                id=maquina,
                denominacion=1.0
            ))
            for r in res["cuadres"]:
                registros.append(calcular_utilidades(r, r["casino"]))

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
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/exportar-reporte")
def exportar_reporte(
    formato: str = Query("pdf"),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    casino: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None),
    maquinas: Optional[List[str]] = Query(None),
):
    from pathlib import Path
    registros = obtener_datos_reporte(
        fecha_inicio, fecha_fin, casino, marca, modelo, maquinas
    )

    if not registros:
        return JSONResponse(status_code=404, content={"error": "No hay datos para exportar"})

    directorio = Path(__file__).parent / "exports"
    directorio.mkdir(exist_ok=True)
    nombre_base = f"reporte_cuadre_casino_fpdf"

    if formato == "pdf":
        from fpdf import FPDF
        archivo = directorio / f"{nombre_base}.pdf"
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "REPORTE DE CONTADORES - CUADRE CASINO",
                 ln=True, align="C")

        pdf.set_font("Arial", "", 9)
        filtros = f"Fechas: {fecha_inicio} a {fecha_fin}  |  Casino: {casino or 'Todos'}"
        pdf.cell(0, 8, filtros, ln=True, align="L")

        # Tabla
        headers = [
            "Fecha Inicio", "Fecha Fin", "Casino", "Máquina", "IN", "OUT",
            "JACKPOT", "BILLETERO", "%PARTICIP.", "UTILIDAD", "PARTICIPANTE", "OPERADOR"
        ]
        campos = [
            "fecha_inicio", "fecha_fin", "casino", "maquina", "in", "out",
            "jackpot", "billetero", "porcentaje_participacion", "utilidad",
            "utilidad_participante", "utilidad_operador"
        ]
        col_widths = [24, 24, 30, 25, 20, 20, 20, 20, 22, 22, 25, 25]

        pdf.set_font("Arial", "B", 8)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 7, h, border=1, align="C")
        pdf.ln()

        # Contadores de totales
        total_utilidad = 0
        total_participante = 0
        total_operador = 0

        pdf.set_font("Arial", "", 7)
        for r in registros:
            for i, campo in enumerate(campos):
                valor = r.get(campo, "-")
                if isinstance(valor, float):
                    if "porcentaje" in campo:
                        valor = f"{valor:.2f}%"
                    else:
                        valor = f"{valor:,.0f}"
                pdf.cell(col_widths[i], 6, str(valor), border=1, align="C")
            pdf.ln()

            # Sumar totales
            total_utilidad += r.get("utilidad", 0)
            total_participante += r.get("utilidad_participante", 0)
            total_operador += r.get("utilidad_operador", 0)

        # Fila de totales
        pdf.set_font("Arial", "B", 8)
        for i in range(9):
            if i == 8:
                pdf.cell(col_widths[i], 6, "TOTALES:", border=1, align="R")
            else:
                pdf.cell(col_widths[i], 6, "", border=1)
        pdf.cell(col_widths[9], 6,
                 f"{total_utilidad:,.0f}", border=1, align="C")
        pdf.cell(col_widths[10], 6,
                 f"{total_participante:,.0f}", border=1, align="C")
        pdf.cell(col_widths[11], 6,
                 f"{total_operador:,.0f}", border=1, align="C")

        pdf.output(str(archivo))
        return FileResponse(archivo, filename=archivo.name)

    elif formato == "excel":
        import pandas as pd
        archivo = directorio / f"{nombre_base}.xlsx"
        df = pd.DataFrame(registros)
        df.to_excel(archivo, index=False)
        return FileResponse(archivo, filename=archivo.name)

    return JSONResponse(status_code=400, content={"error": "Formato no soportado"})
