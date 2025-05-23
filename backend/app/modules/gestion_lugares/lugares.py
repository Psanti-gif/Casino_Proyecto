from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

router = APIRouter(tags=["Gestion de Lugares"])

ARCHIVO = Path(__file__).parent / "lugares.json"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_id.txt"

# Modelo de entrada actualizado


class EntradaLugar(BaseModel):
    codigo: str
    nombre_casino: str
    ciudad: str
    direccion: str
    telefono: str
    persona_encargada: str

# Cargar lugares


def cargar_lugares():
    if ARCHIVO.exists() and ARCHIVO.stat().st_size > 0:
        with ARCHIVO.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Guardar lugares


def guardar_lugares(data):
    with ARCHIVO.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ID incremental


def obtener_siguiente_id():
    if ARCHIVO_CONTADOR.exists():
        ultimo_id = int(ARCHIVO_CONTADOR.read_text())
    else:
        ultimo_id = 0
    nuevo_id = ultimo_id + 1
    ARCHIVO_CONTADOR.write_text(str(nuevo_id))
    return nuevo_id

# Agregar lugar


@router.post("/agregar-lugar")
def agregar_lugar(entrada: EntradaLugar):
    lugares = cargar_lugares()

    for l in lugares.values():
        if l["codigo"] == entrada.codigo:
            raise HTTPException(
                status_code=400, detail="Ya existe un lugar con ese código")

    nuevo_id = obtener_siguiente_id()
    lugares[str(nuevo_id)] = {
        "codigo": entrada.codigo,
        "nombre_casino": entrada.nombre_casino,
        "ciudad": entrada.ciudad,
        "direccion": entrada.direccion,
        "telefono": entrada.telefono,
        "persona_encargada": entrada.persona_encargada,
        "estado": "Activo"
    }
    guardar_lugares(lugares)
    return {"mensaje": "Lugar registrado", "id": nuevo_id}

# Listar lugares


@router.get("/listar-lugares")
def listar_lugares():
    lugares = cargar_lugares()
    resultado = []
    for id_str, datos in lugares.items():
        datos["id"] = int(id_str)
        resultado.append(datos)
    return resultado

# Editar lugar


@router.put("/editar-lugar/{id}")
def editar_lugar(id: int, datos: EntradaLugar):
    lugares = cargar_lugares()
    id_str = str(id)
    if id_str not in lugares:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")

    lugares[id_str] = {
        **datos.dict(),
        "estado": lugares[id_str]["estado"]  # conservar estado actual
    }

    guardar_lugares(lugares)
    return {"mensaje": "Lugar actualizado correctamente"}

# Inactivar lugar


@router.put("/inactivar-lugar/{id}")
def inactivar_lugar(id: int):
    lugares = cargar_lugares()
    id_str = str(id)
    if id_str not in lugares:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    lugares[id_str]["estado"] = "Inactivo"
    guardar_lugares(lugares)
    return {"mensaje": "Lugar inactivado"}

# Activar lugar


@router.put("/activar-lugar/{id}")
def activar_lugar(id: int):
    lugares = cargar_lugares()
    id_str = str(id)
    if id_str not in lugares:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    lugares[id_str]["estado"] = "Activo"
    guardar_lugares(lugares)
    return {"mensaje": "Lugar activado"}
