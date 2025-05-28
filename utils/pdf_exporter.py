from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

def exportar_reporte_pdf(reporte: dict, filename: str) -> str:
    output_path = Path(__file__).parent.parent / "reportes" / f"{filename}.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Reporte General - {reporte['casino']}")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Rango de fechas: {reporte['rango_fechas']['desde']} a {reporte['rango_fechas']['hasta']}")
    y -= 30

    for key, value in reporte["totales"].items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Utilidad: {reporte['utilidad']}")

    c.save()
    return str(output_path)
