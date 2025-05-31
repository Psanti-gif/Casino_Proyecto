from fpdf import FPDF
import pandas as pd

class ExportadorReportes:

    @staticmethod
    def exportar_a_excel(data: dict, nombre_archivo: str):
        df = pd.json_normalize(data["detalle_maquinas"])
        totales = pd.DataFrame([data.get("totales_grupo") or data.get("totales") or {}])
        ruta = f"exports/{nombre_archivo}.xlsx"

        with pd.ExcelWriter(ruta) as writer:
            df.to_excel(writer, sheet_name="Detalle", index=False)
            totales.to_excel(writer, sheet_name="Totales", index=False)

        return ruta

    @staticmethod
    def exportar_a_pdf(data: dict, nombre_archivo: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="REPORTE DE MAQUINAS", ln=True, align='C')

        for clave, valor in data.get("totales_grupo") or data.get("totales") or {}.items():
            pdf.cell(200, 10, txt=f"{clave}: {valor}", ln=True)

        ruta = f"exports/{nombre_archivo}.pdf"
        pdf.output(ruta)
        return ruta

