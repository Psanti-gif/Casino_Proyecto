from fastapi import APIRouter, UploadFile, Form, HTTPException
from pathlib import Path
import json
import shutil

router = APIRouter(tags=["Configuración del sistema"])

CARPETA = Path(__file__).parent / "media"
ARCHIVO_CONFIG = CARPETA / "configuracion.json"
ARCHIVO_LOGO = CARPETA / "logo.png"

# Asegurar que la carpeta media exista
CARPETA.mkdir(parents=True, exist_ok=True)

# Leer configuración actual


def cargar_configuracion():
    if ARCHIVO_CONFIG.exists():
        with ARCHIVO_CONFIG.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "nombre_aplicacion": "CUADRE CASINO",
            "logo_url": "logo.png"
        }

    data["logo_url"] = f"/media/{data.get('logo_url', 'logo.png')}"
    return data

# Guardar archivo de configuración


def guardar_configuracion(data: dict):
    # Solo se guarda el nombre del logo, no la ruta completa
    data["logo_url"] = Path(data.get("logo_url", "logo.png")).name
    with ARCHIVO_CONFIG.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# GET - obtener configuración


@router.get("/configuracion")
def obtener_configuracion():
    return cargar_configuracion()

# PUT - actualizar configuración y subir nuevo logo si viene


@router.put("/configuracion")
async def actualizar_configuracion(
    nombre_aplicacion: str = Form(...),
    logo: UploadFile = None
):
    config = cargar_configuracion()
    config["nombre_aplicacion"] = nombre_aplicacion

    if logo:
        if logo.content_type not in ["image/png", "image/jpeg"]:
            raise HTTPException(
                status_code=400, detail="Formato de imagen no válido")

        # Sobrescribe logo.png
        with ARCHIVO_LOGO.open("wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)

        config["logo_url"] = "logo.png"

    guardar_configuracion(config)
    return {"mensaje": "Configuración actualizada correctamente"}
