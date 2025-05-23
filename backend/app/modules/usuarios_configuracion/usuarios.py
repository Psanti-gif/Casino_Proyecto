import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import smtplib
import random
from email.message import EmailMessage

router = APIRouter()
ARCHIVO = Path(__file__).parent / "usuarios.json"
ARCHIVO_CODIGOS = Path(__file__).parent / "codigos_recuperacion.json"

# Configuracion del correo, recuperar contraseña
SMTP_SERVIDOR = "smtp.gmail.com"
SMTP_PUERTO = 587
SMTP_CORREO = "mosqueramurilloyair@gmail.com"
SMTP_CLAVE = "yfdicglayyfmkdfe"

router = APIRouter(tags=["Grupo de sesion"])


class SolicitudRecuperacion(BaseModel):
    nombre_usuario: str


class ValidacionCodigo(BaseModel):
    nombre_usuario: str
    codigo: str
    nueva_contrasena: str


class LoginRequest(BaseModel):
    nombre_usuario: str
    contrasena: str


class CambioContrasenaRequest(BaseModel):
    id: int
    actual: str
    nueva: str


@router.post("/login")
def login(datos: LoginRequest):
    if not os.path.exists(ARCHIVO):
        raise HTTPException(
            status_code=500, detail="No se encuentra el archivo de usuarios")

    with open(ARCHIVO, "r") as archivo:
        usuarios = json.load(archivo)

    for id_str, usuario in usuarios.items():
        if usuario["nombre_usuario"] == datos.nombre_usuario:
            if usuario["contrasena"] != datos.contrasena:
                raise HTTPException(
                    status_code=401, detail="Contrasena incorrecta")
            if usuario["estado"] != "Activo":
                raise HTTPException(status_code=403, detail="Usuario inactivo")
            return {
                "mensaje": "Login exitoso",
                "id": int(id_str),
                "nombre_usuario": usuario["nombre_usuario"],
                "nombre_completo": usuario["nombre_completo"],
                "rol": usuario["rol"]
            }

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# combio contraseña

def cargar_usuarios():
    if ARCHIVO.exists():
        with ARCHIVO.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_usuarios(data):
    with ARCHIVO.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@router.put("/cambiar-contrasena")
def cambiar_contrasena(datos: CambioContrasenaRequest):
    usuarios = cargar_usuarios()
    id_str = str(datos.id)

    if id_str not in usuarios:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario = usuarios[id_str]

    if usuario["contrasena"] != datos.actual:
        raise HTTPException(
            status_code=401, detail="Contraseña actual incorrecta")

    usuario["contrasena"] = datos.nueva
    guardar_usuarios(usuarios)
    return {"mensaje": "Contraseña actualizada correctamente"}

# Recuperar contraseña


def cargar_codigos():
    if ARCHIVO_CODIGOS.exists():
        with ARCHIVO_CODIGOS.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_codigos(codigos):
    with ARCHIVO_CODIGOS.open("w", encoding="utf-8") as f:
        json.dump(codigos, f, indent=2)


@router.post("/recuperar-contrasena")
def recuperar_contrasena(solicitud: SolicitudRecuperacion):
    usuarios = cargar_usuarios()
    codigos = cargar_codigos()

    for id_str, usuario in usuarios.items():
        if usuario["nombre_usuario"].lower() == solicitud.nombre_usuario.lower():
            correo_destino = usuario.get("correo")
            if not correo_destino:
                raise HTTPException(
                    status_code=400, detail="Este usuario no tiene un correo registrado")

            # Generar código
            codigo = str(random.randint(100000, 999999))
            codigos[usuario["nombre_usuario"]] = codigo
            guardar_codigos(codigos)

            # Enviar correo
            try:
                mensaje = EmailMessage()
                mensaje["Subject"] = "Código de recuperación - CUADRE CASINO"
                mensaje["From"] = SMTP_CORREO
                mensaje["To"] = correo_destino
                mensaje.set_content(f"""
Hola {usuario["nombre_completo"]},

Tu código de recuperación de contraseña es: {codigo}

Si no solicitaste este cambio, ignora este mensaje.

CUADRE CASINO
""")
                with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO) as servidor:
                    servidor.starttls()
                    servidor.login(SMTP_CORREO, SMTP_CLAVE)
                    servidor.send_message(mensaje)

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"No se pudo enviar el correo: {str(e)}")

            return {"mensaje": "Código enviado al correo registrado"}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.put("/recuperar-contrasena-validar")
def validar_codigo_y_cambiar(validacion: ValidacionCodigo):
    usuarios = cargar_usuarios()
    codigos = cargar_codigos()

    usuario = next(
        (u for u in usuarios.items() if u[1]["nombre_usuario"].lower(
        ) == validacion.nombre_usuario.lower()),
        None
    )

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nombre_usuario = usuario[1]["nombre_usuario"]

    if nombre_usuario not in codigos:
        raise HTTPException(
            status_code=400, detail="No se solicito recuperacion para este usuario")

    if codigos[nombre_usuario] != validacion.codigo:
        raise HTTPException(status_code=401, detail="Codigo incorrecto")

    # Actualizar contraseña
    for id_str, datos in usuarios.items():
        if datos["nombre_usuario"] == nombre_usuario:
            datos["contrasena"] = validacion.nueva_contrasena
            break

    guardar_usuarios(usuarios)

    # Eliminar codigo usado
    codigos.pop(nombre_usuario)
    guardar_codigos(codigos)

    return {"mensaje": "Contraseña actualizada correctamente"}
