from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path

# Ruta de archivos
ARCHIVO = Path(__file__).parent / "maquinas.csv"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_maquinas.txt"

# Modelos


class MaquinaEntrada(BaseModel):
    nombre_maquina: str
    ubicacion: str
    tipo: str
    estado: str


class Maquina(BaseModel):
    id: int
    nombre_maquina: str
    ubicacion: str
    tipo: str
    estado: str


# Router de FastAPI
router = APIRouter(prefix="/maquinas", tags=["Maquinas"])

# Obtener siguiente ID


def obtener_siguiente_id():
    if ARCHIVO_CONTADOR.exists():
        with open(ARCHIVO_CONTADOR, "r") as f:
            ultimo_id = int(f.read())
    else:
        ultimo_id = 0

    nuevo_id = ultimo_id + 1

    with open(ARCHIVO_CONTADOR, "w") as f:
        f.write(str(nuevo_id))

    return nuevo_id

# Ruta para agregar maquina


@router.post("/agregar")
def agregar_maquina(maquina: MaquinaEntrada):
    nuevo_id = obtener_siguiente_id()
    escribir_cabecera = True

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            primera = f.readline().strip().lower()
            if primera == "id,nombre_maquina,ubicacion,tipo,estado":
                escribir_cabecera = False

    with open(ARCHIVO, "a", encoding="utf-8") as f:
        if escribir_cabecera:
            f.write("id,nombre_maquina,ubicacion,tipo,estado\n")

        linea = (
            str(nuevo_id) + "," +
            maquina.nombre_maquina + "," +
            maquina.ubicacion + "," +
            maquina.tipo + "," +
            maquina.estado + "\n"
        )

        f.write(linea)

    return {"mensaje": "Maquina guardada correctamente", "id_asignado": nuevo_id}

# Ruta para listar maquinas


@router.get("/listar")
def listar_maquinas():
    lista = []

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            for linea in lineas[1:]:
                partes = linea.strip().split(",")

                if len(partes) == 5:
                    maquina = {
                        "id": int(partes[0]),
                        "nombre_maquina": partes[1],
                        "ubicacion": partes[2],
                        "tipo": partes[3],
                        "estado": partes[4]
                    }
                    lista.append(maquina)

    return lista
