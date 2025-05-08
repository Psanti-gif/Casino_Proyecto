from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

# Modelo que se usa al crear un usuario (sin ID)


class UsuarioEntrada(BaseModel):
    nombre: str
    correo: str
    rol: str
    estado: str

# Modelo que se usa al listar (con ID)


class Usuario(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    estado: str


# Rutas de archivos
ARCHIVO = Path(__file__).parent / "usuarios.csv"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_id.txt"

# ruta de usuarios
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

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


@router.post("/")
def agregar_usuario(usuario: UsuarioEntrada):
    nuevo_id = obtener_siguiente_id()

    # Comprobamos si el archivo existe y si tiene cabecera
    escribir_cabecera = True
    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            primera_linea = f.readline().strip().lower()  # strip quitar espacios
            if primera_linea == "id,nombre,correo,rol,estado":
                escribir_cabecera = False  # Ya existe la cabecera

    with open(ARCHIVO, mode="a", encoding="utf-8") as f:
        if escribir_cabecera:
            f.write("id,nombre,correo,rol,estado\n")

        linea = f"{nuevo_id},{usuario.nombre},{usuario.correo},{usuario.rol},{usuario.estado}\n"
        f.write(linea)

    return {"mensaje": "Usuario guardado correctamente", "id_asignado": nuevo_id}


# Ruta para listar usuarios


@router.get("/")
def listar_usuarios():
    lista = []

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            lineas = f.readlines()

            for linea in lineas[1:]:  # sato la cabecera
                datos = linea.strip().split(",")  # Separa los campos por coma

                if len(datos) == 5:
                    usuario = {
                        "id": int(datos[0]),
                        "nombre": datos[1],
                        "correo": datos[2],
                        "rol": datos[3],
                        "estado": datos[4]
                    }
                    lista.append(usuario)

    return lista


"""
csv.DictReader(f) crea un lector de filas del archivo CSV (f), y convierte cada fila en un diccionario de Python.
Toma la primera línea del archivo (la que tiene los encabezados: id,nombre,correo,rol,estado)
Luego, cada fila del archivo se convierte en un diccionario con esos nombres como claves.
"""

"""
# [a, append], [newline="", quitar lineas en blanco]
"""

"""
listar usuarios http://127.0.0.1:8000/usuarios/
"""
