from openpyxl import Workbook
from pathlib import Path

EXPORT_DIR = Path(__file__).parent.parent / "reportes"
EXPORT_DIR.mkdir(exist_ok=True)

def exportar_reporte_excel(data: dict, filename: str) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Consolidado"

    # Cabecera
    ws.append(["Casino", data.get("casino", "")])
    ws.append(["Rango de Fechas", f"{data.get('fecha_inicio', '')} a {data.get('fecha_fin', '')}"])
    ws.append([])
    ws.append(["IN", "OUT", "JACKPOT", "BILLETERO", "UTILIDAD"])

    # Totales
    totales = data.get("totales", {})
    utilidad = data.get("utilidad", 0)
    ws.append([
        totales.get("in", 0),
        totales.get("out", 0),
        totales.get("jackpot", 0),
        totales.get("billetero", 0),
        utilidad
    ])

    # Guardar el archivo
    path = EXPORT_DIR / f"{filename}.xlsx"
    wb.save(path)
    return str(path)
