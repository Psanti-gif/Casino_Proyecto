import requests

class ReportesServiceParticipacion:

    @staticmethod
    def generar_reporte_participacion(maquinas: list, fecha_inicio: str, fecha_fin: str, denominaciones: dict, casino: str, porcentaje: float):
        resultados = []

        for codigo in maquinas:
            payload = {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "casino": casino,
                "maquina": codigo,
                "id": codigo,
                "denominacion": denominaciones.get(codigo, 1.0)
            }

            try:
                resp = requests.post("http://127.0.0.1:8000/cuadre_maquina", json=payload)
                if resp.status_code == 200:
                    resultados.extend(resp.json().get("cuadres", []))
            except:
                continue

        utilidad_total = sum(r["utilidad"] for r in resultados)
        valor_participacion = utilidad_total * (porcentaje / 100)

        return {
            "casino": casino,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "porcentaje_aplicado": porcentaje,
            "utilidad_total": utilidad_total,
            "valor_participacion": valor_participacion,
            "detalle_maquinas": resultados
        }
