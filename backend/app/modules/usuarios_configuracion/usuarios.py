from .acciones import router as acciones_router
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel


# Modelo que se usa al crear un usuario (sin ID)


class UsuarioEntrada(BaseModel):
    nombre_usuario: str
    nombre_completo: str
    correo: str
    rol: str
    estado: str
    contrasena: str

# Modelo que se usa para listar (con ID)


class Usuario(BaseModel):
    id: int
    nombre_usuario: str
    nombre_completo: str
    correo: str
    rol: str
    estado: str
    contrasena: str


# Rutas de archivos
ARCHIVO = Path(__file__).parent / "usuarios.csv"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_id.txt"

# ruta de usuarios
router = APIRouter(tags=["Usuarios"])

# para generar ID autoincremental


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

# Ruta para agregar usuario


@router.post("/agregar-usuario")
def agregar_usuario(usuario: UsuarioEntrada):
    nuevo_id = obtener_siguiente_id()
    escribir_cabecera = True


@router.post("/agregar-usuario")
def agregar_usuario(usuario: UsuarioEntrada):
    nuevo_id = obtener_siguiente_id()
    escribir_cabecera = True

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            primera_linea = f.readline().strip().lower()
            if primera_linea == "id,nombre_usuario,nombre_completo,correo,rol,estado,contrasena":
                escribir_cabecera = False

    with open(ARCHIVO, "a", encoding="utf-8") as f:
        if escribir_cabecera:
            f.write(
                "id,nombre_usuario,nombre_completo,correo,rol,estado,contrasena\n")

        linea = (
            str(nuevo_id) + "," +
            usuario.nombre_usuario + "," +
            usuario.nombre_completo + "," +
            usuario.correo + "," +
            usuario.rol + "," +
            usuario.estado + "," +
            usuario.contrasena + "\n"
        )

        f.write(linea)

    return {"mensaje": "Usuario guardado correctamente", "id_asignado": nuevo_id}


# Ruta para listar usuarios


@router.get("/listar-usuarios")
def listar_usuarios():
    lista = []

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            lineas = f.readlines()

            for linea in lineas[1:]:
                datos = linea.strip().split(",")

                if len(datos) == 7:
                    usuario = {
                        "id": int(datos[0]),
                        "nombre_usuario": datos[1],
                        "nombre_completo": datos[2],
                        "correo": datos[3],
                        "rol": datos[4],
                        "estado": datos[5],
                        "contrasena": datos[6]
                    }
                    lista.append(usuario)

    return lista


"""
# [a, append], [newline="", quitar lineas en blanco]
"""

"""
listar usuarios http://127.0.0.1:8000/usuarios/
"""
