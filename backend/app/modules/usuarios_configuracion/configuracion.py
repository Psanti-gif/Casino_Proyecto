from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import json

router = APIRouter(tags=["Configuracion"])

CARPETA = Path(__file__).parent
ARCHIVO_CONFIG = CARPETA / "configuracion.json"
MEDIA = CARPETA / "media"
MEDIA.mkdir(exist_ok=True)

# Montar carpeta de imágenes
router.mount("/media", StaticFiles(directory=MEDIA), name="media")

# Obtener configuración actual


@router.get("/configuracion")
def obtener_configuracion():
    if ARCHIVO_CONFIG.exists():
        with ARCHIVO_CONFIG.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "nombre_empresa": "CUADRE CASINO",
        "telefono": "",
        "direccion": "",
        "nit": "",
        "color_primario": "#1d4ed8",  # Azul
        "color_fondo": "#ffffff",
        "logo_url": ""
    }

# Actualizar configuración


@router.put("/configuracion")
def guardar_configuracion(
    nombre_empresa: str = Form(...),
    telefono: str = Form(""),
    direccion: str = Form(""),
    nit: str = Form(""),
    color_primario: str = Form("#1d4ed8"),
    color_fondo: str = Form("#ffffff"),
    logo: UploadFile = None
):
    datos = {
        "nombre_empresa": nombre_empresa,
        "telefono": telefono,
        "direccion": direccion,
        "nit": nit,
        "color_primario": color_primario,
        "color_fondo": color_fondo,
        "logo_url": ""
    }

    if logo:
        ruta_logo = MEDIA / "logo.png"
        with open(ruta_logo, "wb") as f:
            shutil.copyfileobj(logo.file, f)
        datos["logo_url"] = "/media/logo.png"
    else:
        # Mantener logo anterior si existe
        if ARCHIVO_CONFIG.exists():
            previo = json.load(ARCHIVO_CONFIG.open("r", encoding="utf-8"))
            if "logo_url" in previo:
                datos["logo_url"] = previo["logo_url"]

    with ARCHIVO_CONFIG.open("w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

    return {"mensaje": "Configuración guardada correctamente"}
