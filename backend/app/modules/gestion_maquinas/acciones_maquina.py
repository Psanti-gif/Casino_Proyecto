from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path


class Maquina(BaseModel):
    id: int
    marca: str
    modelo: str
    serial: str
    asset: str
    casino: str
    denominacion: float
    estado: str


class MaquinaEditable(BaseModel):
    marca: str
    modelo: str
    serial: str
    asset: str
    casino: str
    estado: str  # NO se modifica denominacion


# Ruta de archivos
ARCHIVO = Path(__file__).parent / "maquinas.csv"
CONTADOR = Path(__file__).parent / "contador_maquinas.txt"

# rutas
router = APIRouter(tags=["Acciones Maquina"])


# buscar maquina
@router.get("/buscar-maquina/{serial}")
def buscar_maquina(serial: str):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay maquinas registradas"}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

        for linea in lineas[1:]:  # saltar cabecera
            partes = linea.strip().split(",")

            if len(partes) != 8:
                continue

            if partes[3].lower() == serial.lower():  # index 3 = serial
                maquina = {
                    "id": int(partes[0]),
                    "marca": partes[1],
                    "modelo": partes[2],
                    "serial": partes[3],
                    "asset": partes[4],
                    "casino": partes[5],
                    "denominacion": float(partes[6]),
                    "estado": partes[7]
                }
                return maquina

    return {"mensaje": f"No se encontro una maquina con serial: {serial}"}


# editar maquina
@router.put("/editar-maquina/{id}")
def editar_maquina(id: int, datos: MaquinaEditable):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay maquinas registradas"}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    encontrada = False

    for linea in lineas:
        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")
        if int(partes[0]) == id:
            nueva = (
                partes[0] + "," +
                datos.marca + "," +
                datos.modelo + "," +
                datos.serial + "," +
                datos.asset + "," +
                datos.casino + "," +
                partes[6] + "," +  # denominacion no se cambia
                datos.estado + "\n"
            )
            nuevas_lineas.append(nueva)
            encontrada = True
        else:
            nuevas_lineas.append(linea)

    if not encontrada:
        return {"mensaje": f"No se encontro la maquina con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Maquina con ID {id} actualizada correctamente"}


# Inactivar maquina
@router.put("/inactivar-maquina/{id}")
def inactivar_maquina(id: int):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay maquinas registradas"}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    inactivada = False

    for linea in lineas:
        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")
        if int(partes[0]) == id:
            partes[7] = "inactiva"
            nueva = ",".join(partes) + "\n"
            nuevas_lineas.append(nueva)
            inactivada = True
        else:
            nuevas_lineas.append(linea)

    if not inactivada:
        return {"mensaje": f"No se encontro la maquina con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Maquina con ID {id} marcada como inactiva"}

# inactivar maquina


@router.put("/activar-maquina/{id}")
def activar_maquina(id: int):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay maquinas registradas"}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    activada = False

    for linea in lineas:
        if linea.strip() == "":
            continue

        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")

        if len(partes) != 8:
            nuevas_lineas.append(linea)
            continue

        id_actual = int(partes[0])

        if id_actual == id:
            partes[7] = "activa"  # cambia el estado

            nueva_linea = (
                partes[0] + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "," +
                partes[5] + "," +
                partes[6] + "," +
                partes[7] + "\n"
            )

            nuevas_lineas.append(nueva_linea)
            activada = True
        else:
            nueva_linea = (
                partes[0] + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "," +
                partes[5] + "," +
                partes[6] + "," +
                partes[7] + "\n"
            )

            nuevas_lineas.append(nueva_linea)

    if not activada:
        return {"mensaje": f"No se encontro la maquina con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Maquina con ID {id} activada correctamente"}
