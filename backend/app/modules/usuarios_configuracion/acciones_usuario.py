from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
import json

# Modelos


class UsuarioEditable(BaseModel):
    nombre_completo: str
    correo: str
    rol: str
    estado: str
    contrasena: str


class Usuario(BaseModel):
    id: int
    nombre_usuario: str
    nombre_completo: str
    correo: str
    rol: str
    estado: str
    contrasena: str


class UsuarioEntrada(BaseModel):
    nombre_usuario: str
    nombre_completo: str
    correo: str
    rol: str
    estado: str
    contrasena: str


ARCHIVO = Path(__file__).parent / "usuarios.json"
ARCHIVO_CONTADOR = Path(__file__).parent / "contador_id.txt"
router = APIRouter(tags=["Acciones Usuario"])

# ID incremental


def obtener_siguiente_id():
    if ARCHIVO_CONTADOR.exists():
        ultimo_id = int(ARCHIVO_CONTADOR.read_text())
    else:
        ultimo_id = 0
    nuevo_id = ultimo_id + 1
    ARCHIVO_CONTADOR.write_text(str(nuevo_id))
    return nuevo_id

# Leer archivo JSON


def cargar_usuarios():
    if ARCHIVO.exists():
        with ARCHIVO.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Guardar archivo JSON


def guardar_usuarios(datos):
    with ARCHIVO.open("w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

# Agregar usuario


@router.post("/agregar-usuario")
def agregar_usuario(usuario: UsuarioEntrada):
    # Validar campos vacíos o con solo comillas vacías
    for campo, valor in usuario.dict().items():
        limpio = valor.strip().replace('"', '').strip()
        if not limpio:
            return {"mensaje": f"El campo '{campo}' no puede estar vacio o contener solo comillas."}

    usuarios = cargar_usuarios()
    for u in usuarios.values():
        if u["nombre_usuario"].lower() == usuario.nombre_usuario.lower():
            return {"mensaje": "El nombre de usuario ya existe"}

    nuevo_id = obtener_siguiente_id()
    usuarios[str(nuevo_id)] = usuario.dict()
    guardar_usuarios(usuarios)
    return {"mensaje": "Usuario guardado correctamente", "id_asignado": nuevo_id}


# Listar usuarios


@router.get("/listar-usuarios")
def listar_usuarios():
    usuarios = cargar_usuarios()
    resultado = []
    for id_str, datos in usuarios.items():
        datos["id"] = int(id_str)
        resultado.append(datos)
    return resultado

# Buscar usuario por nombre


@router.get("/buscar-usuario/{nombre_usuario}")
def buscar_usuario(nombre_usuario: str):
    usuarios = cargar_usuarios()
    for id_str, datos in usuarios.items():
        if datos["nombre_usuario"].lower() == nombre_usuario.lower():
            datos["id"] = int(id_str)
            return datos
    return {"mensaje": f"No se encontro el usuario: {nombre_usuario}"}

# Buscar usuario por id


@router.get("/buscar-usuario-id/{id}")
def buscar_usuario_por_id(id: int):
    usuarios = cargar_usuarios()
    id_str = str(id)
    if id_str not in usuarios:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}
    datos = usuarios[id_str]
    datos["id"] = id
    return datos

# Editar usuario por ID


@router.put("/editar-usuario/{id}")
def editar_usuario(id: int, datos: UsuarioEditable):
    usuarios = cargar_usuarios()
    id_str = str(id)
    if id_str not in usuarios:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    usuario = usuarios[id_str]
    usuario["nombre_completo"] = datos.nombre_completo
    usuario["correo"] = datos.correo
    usuario["rol"] = datos.rol
    usuario["estado"] = datos.estado
    usuario["contrasena"] = datos.contrasena

    guardar_usuarios(usuarios)
    return {"mensaje": f"Usuario con ID {id} editado correctamente"}


# INACTIVAR usuario


@router.put("/inactivar-usuario/{id}")
def inactivar_usuario(id: int):
    usuarios = cargar_usuarios()
    id_str = str(id)
    if id_str not in usuarios:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    usuarios[id_str]["estado"] = "Inactivo"
    guardar_usuarios(usuarios)
    return {"mensaje": f"Usuario con ID {id} inactivado correctamente"}

# ACTIVAR usuario


@router.put("/activar-usuario/{id}")
def activar_usuario(id: int):
    usuarios = cargar_usuarios()
    id_str = str(id)
    if id_str not in usuarios:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    usuarios[id_str]["estado"] = "Activo"
    guardar_usuarios(usuarios)
    return {"mensaje": f"Usuario con ID {id} activado correctamente"}


"""
with open(ARCHIVO, "r", encoding="utf-8") a -> append, newline="" -> quitar lineas en blanco

readline -> primera linea
lower() -> convierte todo a minuscilas



"""
