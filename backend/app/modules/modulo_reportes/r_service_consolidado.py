import requests

class ReportesServiceConsolidado:

    @staticmethod
    def generar_reporte_consolidado(casino: str, fecha_inicio: str, fecha_fin: str):
        payload = {
            "casino": casino,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

        print(f"📤 Enviando POST a /cuadre_casino con payload:", payload)

        try:
            response = requests.post("http://127.0.0.1:8000/cuadre_casino", json=payload)

            print(f"📥 Respuesta de /cuadre_casino: {response.status_code}")

            # Si no hay registros, generar uno con ceros
            if response.status_code == 404:
                print(f"⚠️ Sin registros para {casino}")
                return [{
                    "fecha": fecha_inicio,
                    "casino": casino,
                    "maquina": "Sin datos",
                    "in": 0,
                    "out": 0,
                    "jackpot": 0,
                    "billetero": 0,
                    "utilidad": 0
                }]

            if response.status_code != 200:
                print("⛔️ Error inesperado:", response.text)
                return {"error": "No se pudo obtener el cuadre consolidado del casino"}

            data = response.json()
            print(f"✅ JSON recibido: {data}")

            # Si ya es lista, devolver tal cual
            if isinstance(data, list):
                return data

            if "totales" not in data:
                return [{
                    "fecha": fecha_inicio,
                    "casino": casino,
                    "maquina": "Sin datos",
                    "in": 0,
                    "out": 0,
                    "jackpot": 0,
                    "billetero": 0,
                    "utilidad": 0
                }]

            # Generar estructura compatible con la tabla del frontend
            registro = {
                "fecha": fecha_inicio,
                "casino": casino,
                "maquina": "Total por Casino",
                "in": data["totales"].get("total_in", 0),
                "out": data["totales"].get("total_out", 0),
                "jackpot": data["totales"].get("total_jackpot", 0),
                "billetero": data["totales"].get("total_billetero", 0),
                "utilidad": data["totales"].get("utilidad_total", 0)
            }

            return [registro]

        except Exception as e:
            print("💥 Excepción:", str(e))
            return {"error": f"Error al consultar cuadre-casino: {str(e)}"}
