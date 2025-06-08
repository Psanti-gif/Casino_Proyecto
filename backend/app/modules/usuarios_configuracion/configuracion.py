from fastapi import APIRouter, UploadFile, Form, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import json
import socket


router = APIRouter(tags=["Configuracion"])

CARPETA = Path(__file__).parent
ARCHIVO_CONFIG = CARPETA / "configuracion.json"
ARCHIVO_MARCAS_MODELOS = CARPETA / "marcas_modelos.json"

MEDIA = CARPETA / "media"
MEDIA.mkdir(exist_ok=True)

# Montar carpeta de imágenes
router.mount("/media", StaticFiles(directory=MEDIA), name="media")

# Función auxiliar para procesar texto separado por comas


def procesar_lista(texto):
    return [x.strip() for x in texto.split(",") if x.strip()]

# Obtener configuración actual


@router.get("/configuracion")
def obtener_configuracion():
    if ARCHIVO_CONFIG.exists():
        with ARCHIVO_CONFIG.open("r", encoding="utf-8") as f:
            config = json.load(f)
            config.setdefault("modo_mantenimiento", False)
            config.setdefault("correo", "")
            config.setdefault("divisa", "")
            return config
    return {
        "nombre_empresa": "CUADRE CASINO",
        "telefono": "",
        "direccion": "",
        "nit": "",
        "correo": "",
        "divisa": "",
        "color_primario": "#1d4ed8",
        "color_fondo": "#ffffff",
        "logo_url": "",
        "modo_mantenimiento": False
    }

# Actualizar configuración


@router.put("/configuracion")
def guardar_configuracion(
    nombre_empresa: str = Form(...),
    telefono: str = Form(""),
    direccion: str = Form(""),
    nit: str = Form(""),
    correo: str = Form(""),
    divisa: str = Form(""),
    marcas: str = Form(""),
    modelos: str = Form(""),
    color_primario: str = Form("#1d4ed8"),
    color_fondo: str = Form("#ffffff"),
    modo_mantenimiento: bool = Form(False),
    logo: UploadFile = None
):
    datos = {
        "nombre_empresa": nombre_empresa,
        "telefono": telefono,
        "direccion": direccion,
        "nit": nit,
        "correo": correo,
        "divisa": divisa,
        "color_primario": color_primario,
        "color_fondo": color_fondo,
        "modo_mantenimiento": modo_mantenimiento,
        "logo_url": ""
    }

    if logo:
        ruta_logo = MEDIA / "logo.png"
        with open(ruta_logo, "wb") as f:
            shutil.copyfileobj(logo.file, f)
        datos["logo_url"] = "/media/logo.png"
    else:
        if ARCHIVO_CONFIG.exists():
            previo = json.load(ARCHIVO_CONFIG.open("r", encoding="utf-8"))
            if "logo_url" in previo:
                datos["logo_url"] = previo["logo_url"]

    # Guardar configuracion.json
    with ARCHIVO_CONFIG.open("w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

    # Procesar y agregar marcas y modelos al archivo existente
    marcas_lista = procesar_lista(marcas)
    modelos_lista = procesar_lista(modelos)

    if ARCHIVO_MARCAS_MODELOS.exists():
        with ARCHIVO_MARCAS_MODELOS.open("r", encoding="utf-8") as f:
            marcas_modelos = json.load(f)
    else:
        marcas_modelos = {}

    for marca in marcas_lista:
        modelos_actuales = set(marcas_modelos.get(marca, []))
        nuevos_modelos = set(modelos_lista)
        marcas_modelos[marca] = sorted(
            list(modelos_actuales.union(nuevos_modelos)))

    with ARCHIVO_MARCAS_MODELOS.open("w", encoding="utf-8") as f:
        json.dump(marcas_modelos, f, indent=2, ensure_ascii=False)

    return {"mensaje": "Configuración guardada correctamente"}

# Obtener solo estado de mantenimiento


@router.get("/modo-mantenimiento")
def obtener_modo_mantenimiento():
    if ARCHIVO_CONFIG.exists():
        config = json.load(ARCHIVO_CONFIG.open("r", encoding="utf-8"))
        return {"modo_mantenimiento": config.get("modo_mantenimiento", False)}
    return {"modo_mantenimiento": False}

# Cambiar estado de mantenimiento


@router.put("/modo-mantenimiento")
def cambiar_modo_mantenimiento(modo: bool = Form(...)):
    if ARCHIVO_CONFIG.exists():
        config = json.load(ARCHIVO_CONFIG.open("r", encoding="utf-8"))
    else:
        config = {}

    config["modo_mantenimiento"] = modo

    with ARCHIVO_CONFIG.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return {"mensaje": f"Modo mantenimiento {'activado' if modo else 'desactivado'}"}

# Desactivar mantenimiento con clave


@router.get("/modo-mantenimiento-off")
def modo_mantenimiento_off(clave: str):
    if clave == "admin123":
        if ARCHIVO_CONFIG.exists():
            datos = json.load(ARCHIVO_CONFIG.open("r", encoding="utf-8"))
            datos["modo_mantenimiento"] = False
            with ARCHIVO_CONFIG.open("w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            return {"mensaje": "Modo mantenimiento desactivado"}
    return {"mensaje": "Clave incorrecta"}

# Endpoint para acceder a marcas_modelos.json


@router.get("/marcas_modelos.json")
def obtener_marcas_modelos():
    if ARCHIVO_MARCAS_MODELOS.exists():
        with ARCHIVO_MARCAS_MODELOS.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def obtener_ipv4_local():
    try:
        # Crea un socket UDP "falso" para averiguar la IP local sin enviar datos
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Se usa para obtener la IP del adaptador de red activo
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@router.get("/obtener-ip")
def obtener_ip():
    return {"ip": obtener_ipv4_local()}
