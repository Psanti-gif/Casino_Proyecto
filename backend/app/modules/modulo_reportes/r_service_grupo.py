import requests
from fastapi import HTTPException

class ReportesServiceGrupo:

    @staticmethod
    def generar_reporte_grupo(fecha_inicio: str, fecha_fin: str, casino: str, maquinas: list, denominacion: float):
        resultados = []

        for codigo in maquinas:
            payload = {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "casino": casino,
                "maquina": codigo,
                "id": codigo,
                "denominacion": denominacion
            }

            try:
                resp = requests.post("http://127.0.0.1:8000/cuadre_maquina", json=payload)
                if resp.status_code == 200:
                    cuadre = resp.json().get("cuadres", [])
                    resultados.extend(cuadre)
                else:
                    raise HTTPException(status_code=500, detail=f"Error al consultar máquina {codigo}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Excepción al procesar máquina {codigo}: {str(e)}")

        return {"registros": resultados}
