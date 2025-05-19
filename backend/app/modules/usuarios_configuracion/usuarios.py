import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

router = APIRouter()
ARCHIVO = Path(__file__).parent / "usuarios.json"


class LoginRequest(BaseModel):
    nombre_usuario: str
    contrasena: str


@router.post("/login")
def login(datos: LoginRequest):
    if not os.path.exists(ARCHIVO):
        raise HTTPException(
            status_code=500, detail="No se encuentra el archivo de usuarios")

    with open(ARCHIVO, "r") as archivo:
        usuarios = json.load(archivo)

    for usuario in usuarios.values():
        if usuario["nombre_usuario"] == datos.nombre_usuario:
            if usuario["contrasena"] != datos.contrasena:
                raise HTTPException(
                    status_code=401, detail="Contrasena incorrecta")
            if usuario["estado"] != "Activo":
                raise HTTPException(status_code=403, detail="Usuario inactivo")
            return {
                "mensaje": "Login exitoso",
                "nombre_completo": usuario["nombre_completo"],
                "rol": usuario["rol"]
            }

    raise HTTPException(status_code=404, detail="Usuario no encontrado")
