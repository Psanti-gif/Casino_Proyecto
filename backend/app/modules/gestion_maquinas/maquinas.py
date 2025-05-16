from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path


# Modelos


class MaquinaEntrada(BaseModel):
    marca: str
    modelo: str
    serial: str
    asset: str
    casino: str
    denominacion: float  # no editable
    estado: str  # activa o inactiva


class Maquina(BaseModel):
    id: int
    marca: str
    modelo: str
    serial: str
    asset: str
    casino: str
    denominacion: float
    estado: str


# Ruta de archivos
ARCHIVO = Path(__file__).parent / "maquinas.csv"
CONTADOR = Path(__file__).parent / "contador_maquinas.txt"

# Router de FastAPI
router = APIRouter(tags=["Maquinas"])

# ID automatico


def obtener_siguiente_id():
    if CONTADOR.exists():
        with open(CONTADOR, "r") as f:
            ultimo_id = int(f.read())
    else:
        ultimo_id = 0

    nuevo_id = ultimo_id + 1

    with open(CONTADOR, "w") as f:
        f.write(str(nuevo_id))

    return nuevo_id

# Ruta para agregar maquina


@router.post("/agregar-maquina")
def agregar_maquina(maquina: MaquinaEntrada):
    nuevo_id = obtener_siguiente_id()
    escribir_cabecera = True

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            if f.readline().strip().lower() == "id,marca,modelo,serial,asset,casino,denominacion,estado":
                escribir_cabecera = False

    with open(ARCHIVO, "a", encoding="utf-8") as f:
        if escribir_cabecera:
            f.write("id,marca,modelo,serial,asset,casino,denominacion,estado\n")

        linea = (
            str(nuevo_id) + "," +
            maquina.marca + "," +
            maquina.modelo + "," +
            maquina.serial + "," +
            maquina.asset + "," +
            maquina.casino + "," +
            str(maquina.denominacion) + "," +
            maquina.estado + "\n"
        )

        f.write(linea)

    return {"mensaje": "Maquina registrada correctamente", "id": nuevo_id}

# Listar todas las maquinas


@router.get("/listar-maquinas")
def listar_maquinas():
    lista = []

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            lineas = f.readlines()[1:]  # saltar cabecera

            for linea in lineas:
                partes = linea.strip().split(",")
                if len(partes) == 8:
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
                    lista.append(maquina)

    return lista
