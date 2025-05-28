from fastapi import FastAPI, Body, HTTPException
from datetime import date
from uuid import uuid4
from pathlib import Path
from typing import Optional

from models.schemas import CasinosResponse
from utils.file_io import load_json, load_machine_data, save_json
from utils.excel_exporter import exportar_reporte_excel
from utils.pdf_exporter import exportar_reporte_pdf

app = FastAPI(title="Cuadre General por Casino")

def calcular_reporte(casino_id: str, desde: date, hasta: date) -> dict:
    casinos_data = load_json("casinos.json")
    casino = casinos_data.get(casino_id)
    if not casino:
        raise HTTPException(status_code=404, detail=f"Casino '{casino_id}' no encontrado.")

    total_in = total_out = total_jackpot = total_billetero = 0
    for maquina_id in casino["maquinas"]:
        data = load_machine_data(maquina_id)
        if not data.get(str(desde)) or not data.get(str(hasta)):
            continue
        total_in += data[str(hasta)]["IN"] - data[str(desde)]["IN"]
        total_out += data[str(hasta)]["OUT"] - data[str(desde)]["OUT"]
        total_jackpot += data[str(hasta)]["JACKPOT"] - data[str(desde)]["JACKPOT"]
        total_billetero += data[str(hasta)]["BILLETERO"] - data[str(desde)]["BILLETERO"]

    utilidad = total_in - (total_out + total_jackpot)

    reporte = {
        "casino": casino["nombre"],
        "casino_id": casino_id,
        "rango_fechas": {"desde": str(desde), "hasta": str(hasta)},
        "totales": {
            "IN": total_in,
            "OUT": total_out,
            "JACKPOT": total_jackpot,
            "BILLETERO": total_billetero
        },
        "utilidad": utilidad
    }
    return reporte

@app.get("/")
def raiz():
    return {"mensaje": "API Cuadre General por Casino funcionando"}

@app.get("/casinos", response_model=CasinosResponse)
def listar_casinos():
    casinos_data = load_json("casinos.json")
    return {"casinos": casinos_data}

@app.get("/cuadre/{casino_id}")
def cuadre_general(casino_id: str, desde: date, hasta: date):
    reporte = calcular_reporte(casino_id, desde, hasta)

    nombre_archivo = f"reporte_{reporte['casino']}_{desde}_{hasta}".replace(" ", "_").replace(":", "-")
    ruta_excel = exportar_reporte_excel(reporte, nombre_archivo)
    ruta_pdf = exportar_reporte_pdf(reporte, nombre_archivo)

    filename = f"reporte_{casino_id}_{uuid4().hex[:8]}.json"
    save_json(reporte, filename)

    reporte["archivo_guardado"] = filename
    reporte["archivo_excel"] = ruta_excel
    reporte["archivo_pdf"] = ruta_pdf

    return reporte

@app.get("/cuadre/previsualizar/{casino_id}")
def previsualizar_cuadre(casino_id: str, desde: date, hasta: date):
    reporte = calcular_reporte(casino_id, desde, hasta)
    return reporte

@app.post("/cuadre/guardar")
def guardar_reporte(reporte: dict = Body(...)):
    if not reporte.get("casino_id") or not reporte.get("rango_fechas"):
        raise HTTPException(status_code=400, detail="Reporte inválido, faltan datos.")

    carpeta = Path("reportes_guardados")
    carpeta.mkdir(exist_ok=True)

    filename = carpeta / f"reporte_confirmado_{reporte['casino_id']}_{uuid4().hex[:8]}.json"
    save_json(reporte, str(filename))

    return {"mensaje": "Reporte guardado correctamente", "archivo": str(filename)}

@app.get("/reportes")
def listar_reportes():
    reportes_dir = Path("reportes_guardados")
    archivos = [f.name for f in reportes_dir.glob("reporte_*.json")]
    return {"reportes": archivos}

@app.get("/reportes/{nombre}")
def ver_reporte(nombre: str):
    try:
        ruta = Path("reportes_guardados") / nombre
        contenido = load_json(str(ruta))
        return contenido
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
