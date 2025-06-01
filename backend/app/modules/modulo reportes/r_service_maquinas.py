from app.modules.gestion_maquinas.gestion_maquinas import cargar_maquinas
from app.modules.gestion_lugares.lugares import cargar_lugares

class ReportesServiceMaquinas:

    @staticmethod
    def filtrar_maquinas(
        marca: str = None,
        modelo: str = None,
        casino: str = None,
        ciudad: str = None
    ) -> list:
        maquinas = cargar_maquinas()
        lugares = cargar_lugares()
        resultado = []

        for maquina in maquinas.values():
            if marca and maquina["marca"].lower() != marca.lower():
                continue
            if modelo and maquina["modelo"].lower() != modelo.lower():
                continue
            if casino and maquina["casino"].lower() != casino.lower():
                continue

            lugar = next(
                (l for l in lugares.values()
                 if l["nombre_casino"].lower() == maquina["casino"].lower()),
                None
            )
            ciudad_maquina = lugar["ciudad"] if lugar else "Desconocida"

            if ciudad and ciudad_maquina.lower() != ciudad.lower():
                continue

            resultado.append({
                "codigo": maquina["codigo"],
                "marca": maquina["marca"],
                "modelo": maquina["modelo"],
                "casino": maquina["casino"],
                "ciudad": ciudad_maquina,
                "denominacion": maquina["denominacion"],
                "estado": "Activo" if maquina["activo"] == 1 else "Inactiva"
            })

        return resultado
