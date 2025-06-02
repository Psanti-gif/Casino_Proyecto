import requests
from fastapi import HTTPException

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
                raise HTTPException(status_code=500, detail="No se pudo obtener la utilidad de la máquina")

            data = response.json()

            if "cuadres" not in data or not isinstance(data["cuadres"], list):
                raise HTTPException(status_code=400, detail="Respuesta de cuadre_maquina inválida")

            return {"registros": data["cuadres"]}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al consultar cuadre_maquina: {str(e)}")
