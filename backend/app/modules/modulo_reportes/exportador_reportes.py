import os
import uuid
import pandas as pd
from fpdf import FPDF
from fastapi.responses import FileResponse

class ExportadorReportes:

    @staticmethod
    def exportar_a_pdf(data: dict, nombre_archivo: str) -> str:
        os.makedirs("exports", exist_ok=True)
        ruta = f"exports/{nombre_archivo}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="REPORTE DE UTILIDAD", ln=True, align='C')
        pdf.ln(10)

        for maquina in data.get("detalle_maquinas", []):
            pdf.cell(200, 10, txt=f"Máquina: {maquina['maquina']}", ln=True)
            pdf.cell(200, 10, txt=f"Casino: {maquina['casino']}", ln=True)
            pdf.cell(200, 10, txt=f"Utilidad: {maquina['utilidad']}", ln=True)
            pdf.ln(5)

        pdf.ln(5)
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt="Totales:", ln=True)
        pdf.set_font("Arial", size=12)

        for clave, valor in (data.get("totales_grupo") or data.get("totales") or {}).items():
            pdf.cell(200, 10, txt=f"{clave}: {valor}", ln=True)

        pdf.output(ruta)
        return ruta

    @staticmethod
    def exportar_a_excel(data: dict, nombre_archivo: str) -> str:
        os.makedirs("exports", exist_ok=True)
        ruta = f"exports/{nombre_archivo}.xlsx"

        df = pd.json_normalize(data.get("detalle_maquinas", []))
        df_totales = pd.DataFrame([data.get("totales_grupo") or data.get("totales") or {}])

        with pd.ExcelWriter(ruta) as writer:
            df.to_excel(writer, sheet_name="Detalle", index=False)
            df_totales.to_excel(writer, sheet_name="Totales", index=False)

        return ruta

    @staticmethod
    def generar_nombre_archivo() -> str:
        return f"reporte_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def devolver_archivo(ruta: str) -> FileResponse:
        return FileResponse(path=ruta, filename=os.path.basename(ruta), media_type="application/octet-stream")

