from fastapi import APIRouter, Form, HTTPException
from pathlib import Path
import json

router = APIRouter(tags=["Marcas y Modelos"])

ARCHIVO = Path(__file__).parent / "marcas_modelos.json"


# Cargar datos


def cargar_datos():
    if ARCHIVO.exists():
        with ARCHIVO.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Guardar datos


def guardar_datos(data):
    with ARCHIVO.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Obtener todas las marcas y modelos


@router.get("/marcas-modelos")
def listar_marcas_modelos():
    return cargar_datos()

# Agregar una nueva marca y modelo


@router.post("/agregar-marca-modelo")
def agregar_marca_modelo(
    marca: str = Form(...),
    modelo: str = Form(...)
):
    data = cargar_datos()
    if marca in data:
        if modelo in data[marca]:
            raise HTTPException(
                status_code=400, detail="El modelo ya existe para esta marca")
        data[marca].append(modelo)
    else:
        data[marca] = [modelo]
    guardar_datos(data)
    return {"mensaje": "Marca y modelo agregados correctamente"}
