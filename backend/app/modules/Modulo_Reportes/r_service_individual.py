import requests

class ReportesServiceIndividual:

    @staticmethod
    def generar_reporte_individual(fecha_inicio: str, fecha_fin: str, casino: str, maquina: str, denominacion: float):
        payload = {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "casino": casino,
            "maquina": maquina,
            "id": maquina,
            "denominacion": denominacion
        }

        try:
            response = requests.post("http://127.0.0.1:8000/cuadre_maquina", json=payload)
            if response.status_code != 200:
                return {"error": "No se pudo obtener la utilidad de la máquina"}

            data = response.json()
            return data.get("cuadres", [])

        except Exception as e:
            return {"error": f"Error al consultar cuadre_maquina: {str(e)}"}
