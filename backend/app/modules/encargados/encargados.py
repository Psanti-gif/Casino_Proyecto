from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json


class EncargadoEntrada(BaseModel):
    nombre: str
    correo: str
    telefono: str
    estado: str


class EncargadoEditable(BaseModel):
    nombre: str
    correo: str
    telefono: str
    estado: str


ARCHIVO = Path(__file__).parent / "encargados.json"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_id_encargado.txt"
router = APIRouter(tags=["Encargados"])


def obtener_siguiente_id():
    if ARCHIVO_CONTADOR.exists():
        ultimo_id = int(ARCHIVO_CONTADOR.read_text())
    else:
        ultimo_id = 0
    nuevo_id = ultimo_id + 1
    ARCHIVO_CONTADOR.write_text(str(nuevo_id))
    return nuevo_id


def cargar_encargados():
    if ARCHIVO.exists():
        with ARCHIVO.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_encargados(datos):
    with ARCHIVO.open("w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


@router.post("/agregar-encargado")
def agregar_encargado(encargado: EncargadoEntrada):
    encargados = cargar_encargados()

    # Validar si el correo ya existe
    for datos in encargados.values():
        if datos["correo"].lower() == encargado.correo.lower():
            raise HTTPException(
                status_code=400, detail="Ya existe un encargado con ese correo.")

    nuevo_id = obtener_siguiente_id()
    encargados[str(nuevo_id)] = encargado.dict()
    guardar_encargados(encargados)
    return {"mensaje": "Encargado guardado correctamente", "id_asignado": nuevo_id}


@router.get("/listar-encargados")
def listar_encargados():
    encargados = cargar_encargados()
    resultado = []
    for id_str, datos in encargados.items():
        datos["id"] = int(id_str)
        resultado.append(datos)
    return resultado


@router.get("/buscar-encargado-id/{id}")
def buscar_encargado_por_id(id: int):
    encargados = cargar_encargados()
    id_str = str(id)
    if id_str not in encargados:
        raise HTTPException(
            status_code=404, detail=f"No se encontró el encargado con ID {id}")
    datos = encargados[id_str]
    datos["id"] = id
    return datos


@router.put("/editar-encargado/{id}")
def editar_encargado(id: int, datos: EncargadoEditable):
    encargados = cargar_encargados()
    id_str = str(id)
    if id_str not in encargados:
        raise HTTPException(
            status_code=404, detail=f"No se encontró el encargado con ID {id}")

    # Validar si se intenta asignar un correo ya existente a otro encargado
    for otro_id, e in encargados.items():
        if otro_id != id_str and e["correo"].lower() == datos.correo.lower():
            raise HTTPException(
                status_code=400, detail="Ya existe otro encargado con ese correo.")

    encargados[id_str] = datos.dict()
    guardar_encargados(encargados)
    return {"mensaje": f"Encargado con ID {id} editado correctamente"}


@router.put("/inactivar-encargado/{id}")
def inactivar_encargado(id: int):
    encargados = cargar_encargados()
    id_str = str(id)
    if id_str not in encargados:
        raise HTTPException(
            status_code=404, detail=f"No se encontró el encargado con ID {id}")
    encargados[id_str]["estado"] = "Inactivo"
    guardar_encargados(encargados)
    return {"mensaje": f"Encargado con ID {id} inactivado correctamente"}


@router.put("/activar-encargado/{id}")
def activar_encargado(id: int):
    encargados = cargar_encargados()
    id_str = str(id)
    if id_str not in encargados:
        raise HTTPException(
            status_code=404, detail=f"No se encontró el encargado con ID {id}")
    encargados[id_str]["estado"] = "Activo"
    guardar_encargados(encargados)
    return {"mensaje": f"Encargado con ID {id} activado correctamente"}
