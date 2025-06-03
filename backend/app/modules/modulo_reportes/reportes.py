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

# Función para obtener datos reales de reportes
# Si se filtra por casino y no por máquina, usa cuadre_casino; si se filtra por máquina, usa cuadre_maquina

def obtener_datos_reporte(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    casino: Optional[str] = None,
    marca: Optional[str] = None,
    modelo: Optional[str] = None,
    ciudad: Optional[str] = None,
    maquinas: Optional[List[str]] = None,
):
    registros = []
    fecha_inicio_str = fecha_inicio.isoformat() if fecha_inicio else None
    fecha_fin_str = fecha_fin.isoformat() if fecha_fin else None

    # Si casino es 'Todos' o None, obtener todos los casinos
    if (casino is None or casino == "Todos") and (not maquinas or len(maquinas) == 0):
        lugares = cargar_lugares()
        for datos in lugares.values():
            casino_nombre = datos["nombre_casino"]
            req = CuadreCasinoRequest(casino=casino_nombre, fecha_inicio=fecha_inicio_str, fecha_fin=fecha_fin_str)
            resultado = cuadre_casino(req)
            for m in resultado["detalle_maquinas"]:
                registros.append({
                    "fecha_inicio": m["fecha_inicio"],
                    "fecha_fin": m["fecha_fin"],
                    "casino": casino_nombre,
                    "maquina": m["maquina"],
                    "in": m["total_in"],
                    "out": m["total_out"],
                    "jackpot": m["total_jackpot"],
                    "billetero": m["total_billetero"],
                    "utilidad": m["utilidad"],
                    "denominacion": m["denominacion"],
                    "contador_inicial": m["contador_inicial"],
                    "contador_final": m["contador_final"],
                })
    # Reporte por casino (consolidado)
    elif casino and (not maquinas or len(maquinas) == 0):
        req = CuadreCasinoRequest(casino=casino, fecha_inicio=fecha_inicio_str, fecha_fin=fecha_fin_str)
        resultado = cuadre_casino(req)
        for m in resultado["detalle_maquinas"]:
            registros.append({
                "fecha_inicio": m["fecha_inicio"],
                "fecha_fin": m["fecha_fin"],
                "casino": casino,
                "maquina": m["maquina"],
                "in": m["total_in"],
                "out": m["total_out"],
                "jackpot": m["total_jackpot"],
                "billetero": m["total_billetero"],
                "utilidad": m["utilidad"],
                "denominacion": m["denominacion"],
                "contador_inicial": m["contador_inicial"],
                "contador_final": m["contador_final"],
            })
    # Reporte por máquina(s)
    elif maquinas:
        for maquina in maquinas:
            # Se requiere denominación, casino y máquina para el cuadre de máquina
            # Aquí se asume denominación=1.0, pero se puede mejorar leyendo la real si es necesario
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
                registros.append({
                    "fecha_inicio": r["fecha_inicio"],
                    "fecha_fin": r["fecha_fin"],
                    "casino": r["casino"],
                    "maquina": r["maquina"],
                    "in": r["total_in"],
                    "out": r["total_out"],
                    "jackpot": r["total_jackpot"],
                    "billetero": r["total_billetero"],
                    "utilidad": r["utilidad"],
                    "contador_inicial": r["contador_inicial"],
                    "contador_final": r["contador_final"],
                })
    # Si no hay filtro, retorna vacío
    return registros

@router.get("/generar-reporte")
def generar_reporte(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    casino: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None),
    ciudad: Optional[str] = Query(None),
    maquinas: Optional[List[str]] = Query(None),
):
    try:
        print(f"Parametros recibidos: fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, casino={casino}, marca={marca}, modelo={modelo}, ciudad={ciudad}, maquinas={maquinas}")
        registros = obtener_datos_reporte(fecha_inicio, fecha_fin, casino, marca, modelo, ciudad, maquinas)
        print(f"Registros obtenidos: {registros}")
        return {"registros": registros}
    except Exception as e:
        print(f"Error en generar_reporte: {e}")  # Log del error
        return JSONResponse(status_code=500, content={"error": f"Error interno del servidor: {str(e)}"})

@router.get("/exportar-reporte")
def exportar_reporte(
    formato: str = Query("pdf"),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    casino: Optional[str] = Query(None),
    marca: Optional[str] = Query(None),
    modelo: Optional[str] = Query(None),
    ciudad: Optional[str] = Query(None),
    maquinas: Optional[List[str]] = Query(None),
):
    registros = obtener_datos_reporte(fecha_inicio, fecha_fin, casino, marca, modelo, ciudad, maquinas)
    if not registros:
        return JSONResponse(status_code=404, content={"error": "No hay datos para exportar"})
    export_dir = os.path.join(os.path.dirname(__file__), "../../../exports")
    os.makedirs(export_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:8]
    # Remove 'contador_inicial' and 'contador_final' from the DataFrame for Excel
    if formato == "excel" or formato == "xlsx":
        df = pd.DataFrame(registros).drop(columns=["contador_inicial", "contador_final"], errors="ignore")
        nombre_archivo = f"reporte_{unique_id}.xlsx"
        ruta_archivo = os.path.join(export_dir, nombre_archivo)
        with pd.ExcelWriter(ruta_archivo, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Reporte")
            worksheet = writer.sheets["Reporte"]
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in column_cells if cell.value is not None)
                column_letter = column_cells[0].column_letter
                worksheet.column_dimensions[column_letter].width = max_length + 2
    elif formato == "pdf":
        nombre_archivo = f"reporte_{unique_id}.pdf"
        ruta_archivo = os.path.join(export_dir, nombre_archivo)
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Reporte de Contadores", ln=True, align="C")
        pdf.set_font("Arial", size=9)
        headers = ["fecha_inicio", "fecha_fin", "casino", "maquina", "in", "out", "jackpot", "billetero", "utilidad"]
        # Calculate max width for each column (header or value)
        col_widths = []
        for h in headers:
            max_content = max([len(str(r.get(h, ""))) for r in registros] + [len(h)])
            # Use string width in mm for best fit
            max_val = max([pdf.get_string_width(str(r.get(h, ""))) for r in registros] + [pdf.get_string_width(h)])
            col_widths.append(max(max_val + 4, 20))  # min width 20mm, add padding
        # Draw headers
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h.upper(), border=1, align="C")
        pdf.ln()
        # Draw rows
        for r in registros:
            for i, h in enumerate(headers):
                val = str(r.get(h, ""))
                # If value is too wide, use MultiCell
                if pdf.get_string_width(val) > col_widths[i] - 2:
                    x = pdf.get_x()
                    y = pdf.get_y()
                    pdf.multi_cell(col_widths[i], 8, val, border=1, align="C")
                    pdf.set_xy(x + col_widths[i], y)
                else:
                    pdf.cell(col_widths[i], 8, val, border=1, align="C")
            pdf.ln()
        pdf.output(ruta_archivo)
    else:
        return JSONResponse(status_code=400, content={"error": "Formato no soportado"})
    return FileResponse(ruta_archivo, filename=nombre_archivo)

@router.get("/reporte-participacion")
def reporte_participacion(
    porcentaje: float = Query(..., gt=0, lt=100),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    casino: Optional[str] = Query(None),
    maquinas: Optional[List[str]] = Query(None),
):
    registros = obtener_datos_reporte(fecha_inicio, fecha_fin, casino, None, None, None, maquinas)
    utilidad_total = sum(r["utilidad"] for r in registros)
    valor_participacion = utilidad_total * (porcentaje / 100)
    return {
        "utilidad_total": utilidad_total,
        "valor_participacion": valor_participacion,
        "registros": registros,
    }
