from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

router = APIRouter(tags=["Gestion de Maquinas"])

ARCHIVO_MAQUINAS = Path(__file__).parent / "maquinas.json"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_id_maquina.txt"

# Modelo con porcentaje de participación incluido


class Maquina(BaseModel):
    codigo: str
    activo: int
    marca: str
    modelo: str
    numero_serie: str
    denominacion: float
    casino: str
    porcentaje_participacion: float

# Utilidades


def obtener_siguiente_id():
    if ARCHIVO_CONTADOR.exists():
        ultimo = int(ARCHIVO_CONTADOR.read_text())
    else:
        ultimo = 0
    nuevo = ultimo + 1
    ARCHIVO_CONTADOR.write_text(str(nuevo))
    return nuevo


def cargar_maquinas():
    if ARCHIVO_MAQUINAS.exists():
        with ARCHIVO_MAQUINAS.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_maquinas(maquinas):
    with ARCHIVO_MAQUINAS.open("w", encoding="utf-8") as f:
        json.dump(maquinas, f, indent=2, ensure_ascii=False)

# Rutas


@router.get("/maquinas")
def listar_maquinas():
    datos = cargar_maquinas()
    return [
        {"id": int(id_), **info}
        for id_, info in datos.items()
    ]


@router.post("/maquinas")
def crear_maquina(maquina: Maquina):
    maquinas = cargar_maquinas()

    for datos in maquinas.values():
        if datos["codigo"].strip().lower() == maquina.codigo.strip().lower():
            raise HTTPException(
                status_code=400, detail="Ya existe una máquina con ese código")

    nuevo_id = obtener_siguiente_id()
    maquinas[str(nuevo_id)] = maquina.dict()
    guardar_maquinas(maquinas)
    return {"mensaje": "Máquina registrada", "id": nuevo_id}


@router.put("/maquinas/{id}")
def editar_maquina(id: int, datos: Maquina):
    maquinas = cargar_maquinas()
    id_str = str(id)
    if id_str not in maquinas:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    maquinas[id_str] = datos.dict()
    guardar_maquinas(maquinas)
    return {"mensaje": "Máquina actualizada"}


@router.put("/maquinas/{id}/activar")
def activar_maquina(id: int):
    maquinas = cargar_maquinas()
    id_str = str(id)
    if id_str not in maquinas:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    maquinas[id_str]["activo"] = 1
    guardar_maquinas(maquinas)
    return {"mensaje": "Máquina activada correctamente"}


@router.put("/maquinas/{id}/inactivar")
def inactivar_maquina(id: int):
    maquinas = cargar_maquinas()
    id_str = str(id)
    if id_str not in maquinas:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    maquinas[id_str]["activo"] = 0
    guardar_maquinas(maquinas)
    return {"mensaje": "Máquina inactivada correctamente"}


@router.get("/maquina/{id}")
def obtener_maquina_por_id(id: int):
    maquinas = cargar_maquinas()
    id_str = str(id)
    if id_str not in maquinas:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return maquinas[id_str]
