import requests

class ReportesServiceGrupo:
    @staticmethod
    def generar_reporte_grupal(maquinas: list, fecha_inicio: str, fecha_fin: str, denominaciones: dict, casino: str):
        resultados = []
        errores = []

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
                else:
                    errores.append({"maquina": codigo, "error": resp.json()})
            except Exception as e:
                errores.append({"maquina": codigo, "error": str(e)})

        total_in = sum(r["total_in"] for r in resultados)
        total_out = sum(r["total_out"] for r in resultados)
        total_jackpot = sum(r["total_jackpot"] for r in resultados)
        total_billetero = sum(r["total_billetero"] for r in resultados)
        utilidad_total = sum(r["utilidad"] for r in resultados)

        return {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "casino": casino,
            "detalle_maquinas": resultados,
            "totales_grupo": {
                "total_in": total_in,
                "total_out": total_out,
                "total_jackpot": total_jackpot,
                "total_billetero": total_billetero,
                "utilidad_total": utilidad_total
            },
            "errores": errores
        }
