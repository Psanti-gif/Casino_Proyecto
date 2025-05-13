from pathlib import Path
from fastapi import APIRouter

ARCHIVO = Path(__file__).parent / "usuarios.csv"

router = APIRouter(tags=["Acciones"])


@router.put("/inactivar-usuario/{id}")
def inactivar_usuario(id: int):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay usuarios registrados."}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    encontrado = False

    for linea in lineas:
        if linea.strip() == "":
            continue

        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")

        id_actual = int(partes[0])

        if id_actual == id:
            partes[4] = "inactivo"
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)
            encontrado = True
        else:
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)

    if not encontrado:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Usuario con ID {id} inactivado correctamente"}


@router.put("/activar-usuario/{id}")
def activar_usuario(id: int):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay usuarios registrados."}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    encontrado = False

    for linea in lineas:
        if linea.strip() == "":
            continue

        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")

        id_actual = int(partes[0])

        if id_actual == id:
            partes[4] = "activo"
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)
            encontrado = True
        else:
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)

    if not encontrado:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Usuario con ID {id} activado correctamente"}
