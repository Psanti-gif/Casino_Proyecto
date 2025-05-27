from gestion_lugares.lugares import cargar_lugares

class ReportesServiceLugares:

    @staticmethod
    def obtener_casinos(ciudad: str = None) -> list:
        lugares = cargar_lugares()
        resultado = []

        for lugar in lugares.values():
            # Filtro por ciudad si se especifica
            if ciudad and lugar["ciudad"].lower() != ciudad.lower():
                continue

            resultado.append({
                "nombre": lugar["nombre_casino"],
                "ciudad": lugar["ciudad"],
                "direccion": lugar["direccion"],
                "telefono": lugar["telefono"],
                "encargado": lugar["persona_encargada"],
                "estado": lugar["estado"]
            })

        return resultado
