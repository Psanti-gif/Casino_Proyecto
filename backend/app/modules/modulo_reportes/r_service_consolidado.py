import requests

class ReportesServiceConsolidado:

    @staticmethod
    def generar_reporte_consolidado(casino: str, fecha_inicio: str, fecha_fin: str):
        payload = {
            "casino": casino,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

        try:
            response = requests.post("http://127.0.0.1:8000/cuadre-casino", json=payload)
            if response.status_code != 200:
                return {"error": "No se pudo obtener el cuadre consolidado del casino"}

            return response.json()

        except Exception as e:
            return {"error": f"Error al consultar cuadre-casino: {str(e)}"}
