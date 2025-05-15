from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

# Modelo que se usa al editar usuario


class UsuarioEditable(BaseModel):
    nombre_completo: str
    correo: str
    rol: str
    estado: str
    contrasena: str


ARCHIVO = Path(__file__).parent / "usuarios.csv"

router = APIRouter(tags=["Acciones"])


# inactivar usuario
@router.put("/inactivar-usuario/{id}")
def inactivar_usuario(id: int):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay usuarios registrados."}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    encontrado = False

    for linea in lineas:
        if linea.strip() == "":
            continue

        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")

        id_actual = int(partes[0])

        if id_actual == id:
            partes[4] = "inactivo"
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)
            encontrado = True
        else:
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)

    if not encontrado:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Usuario con ID {id} inactivado correctamente"}


# activar usuario
@router.put("/activar-usuario/{id}")
def activar_usuario(id: int):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay usuarios registrados."}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    encontrado = False

    for linea in lineas:
        if linea.strip() == "":
            continue

        if linea.lower().startswith("id"):
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")

        id_actual = int(partes[0])

        if id_actual == id:
            partes[4] = "activo"
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)
            encontrado = True
        else:
            nueva_linea = (
                str(partes[0]) + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "\n"
            )
            nuevas_lineas.append(nueva_linea)

    if not encontrado:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Usuario con ID {id} activado correctamente"}


# buscar usuario
@router.get("/buscar-usuario/{nombre_usuario}")
def buscar_usuario(nombre_usuario: str):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay usuarios registrados."}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

        for linea in lineas[1:]:  # Saltar cabecera
            partes = linea.strip().split(",")

            if len(partes) != 7:
                continue

            if partes[1].lower() == nombre_usuario.lower():
                usuario = {
                    "id": int(partes[0]),
                    "nombre_usuario": partes[1],
                    "nombre_completo": partes[2],
                    "correo": partes[3],
                    "rol": partes[4],
                    "estado": partes[5],
                    "contrasena": partes[6]
                }
                return usuario

    return {"mensaje": f"No se encontro el usuario: {nombre_usuario}"}


# editar usuario
@router.put("/editar-usuario/{id}")
def editar_usuario(id: int, datos: UsuarioEditable):
    if not ARCHIVO.exists():
        return {"mensaje": "No hay usuarios registrados."}

    with open(ARCHIVO, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    encontrado = False

    for linea in lineas:
        if linea.strip() == "":
            continue

        if linea.lower().startswith("id"):  # para saber si la line a inicia con id, entonces es pores es cabecera "startswith"
            nuevas_lineas.append(linea)
            continue

        partes = linea.strip().split(",")

        if len(partes) != 7:
            nuevas_lineas.append(linea)
            continue

        id_actual = int(partes[0])

        if id_actual == id:
            # Actualizar campos permitidos
            partes[2] = datos.nombre_completo  # nombre_completo
            partes[3] = datos.correo           # correo
            partes[4] = datos.rol              # rol
            partes[5] = datos.estado           # estado
            partes[6] = datos.contrasena       # contrasena

            nueva_linea = (
                partes[0] + "," +  # id
                partes[1] + "," +  # nombre_usuario (no se cambia)
                partes[2] + "," +  # nombre_completo (editado)
                partes[3] + "," +  # correo (editado)
                partes[4] + "," +  # rol (editado)
                partes[5] + "," +  # estado (editado)
                partes[6] + "\n"   # contrasena (editada)
            )

            nuevas_lineas.append(nueva_linea)
            encontrado = True
        else:
            nueva_linea = (
                partes[0] + "," +
                partes[1] + "," +
                partes[2] + "," +
                partes[3] + "," +
                partes[4] + "," +
                partes[5] + "," +
                partes[6] + "\n"
            )
            nuevas_lineas.append(nueva_linea)

    if not encontrado:
        return {"mensaje": f"No se encontro el usuario con ID {id}"}

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)

    return {"mensaje": f"Usuario con ID {id} editado correctamente"}
