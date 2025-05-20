from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import date
from pydantic import BaseModel
import csv
from pathlib import Path

router = APIRouter(tags=["Cuadre de Maquina"])

# --- Modelos ---
class Casino(BaseModel):
    id: int
    nombre: str
    ubicacion: str

class Maquina(BaseModel):
    id: int
    marca: str
    modelo: str
    serial: str
    asset: str
    casino: int  # ID del casino
    denominacion: float
    estado: str

class CuadreFinal(BaseModel):
    maquina_id: int
    asset: str
    marca: str
    modelo: str
    denominacion: float
    desde: date
    hasta: date
    total_in: float
    total_out: float
    total_jackpot: float
    total_billetero: float
    utilidad: float

BASE_DIR = Path(__file__).parent

# --- Funciones de lectura ---
def leer_casinos() -> List[Casino]:
    with open(BASE_DIR / "casinos.csv", newline='', encoding='utf-8') as f:
        return [Casino(**{
            "id": int(row["id"]),
            "nombre": row["nombre"],
            "ubicacion": row["ubicacion"]
        }) for row in csv.DictReader(f)]

def leer_maquinas() -> List[Maquina]:
    with open(BASE_DIR / "maquinas.csv", newline='', encoding='utf-8') as f:
        maquinas = []
        for row in csv.DictReader(f):
            maquinas.append(Maquina(
                id=int(row["id"]),
                marca=row["marca"],
                modelo=row["modelo"],
                serial=row["serial"],
                asset=row["asset"],
                casino=int(row["casino"]),
                denominacion=float(row["denominacion"]),
                estado=row["estado"]
            ))
        return maquinas

def leer_maquina_por_id(maquina_id: int) -> Maquina | None:
    maquinas = leer_maquinas()
    for m in maquinas:
        if m.id == maquina_id:
            return m
    return None

def leer_registro_extremo(maquina_id: int, fecha: date, modo: str) -> dict | None:
    with open(BASE_DIR / "contadores.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        registros = [r for r in reader if int(r["maquina"]) == maquina_id and date.fromisoformat(r["fecha"]) <= fecha]
        if not registros:
            return None
        registros.sort(key=lambda r: r["fecha"])
        return registros[0] if modo == "inicial" else registros[-1]

# --- Rutas ---
@router.get("/casinos", response_model=List[Casino])
def get_casinos():
    return leer_casinos()

@router.get("/casinos/{casino_id}/maquinas", response_model=List[Maquina])
def get_maquinas_por_casino(casino_id: int):
    maquinas = leer_maquinas()
    filtradas = [m for m in maquinas if m.casino == casino_id]
    if not filtradas:
        raise HTTPException(status_code=404, detail="No hay máquinas para este casino")
    return filtradas

@router.get("/maquinas/{maquina_id}/cuadre", response_model=CuadreFinal)
def obtener_cuadre(maquina_id: int, desde: date = Query(...), hasta: date = Query(...)):
    maquina = leer_maquina_por_id(maquina_id)
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    ini = leer_registro_extremo(maquina_id, desde, "inicial")
    fin = leer_registro_extremo(maquina_id, hasta, "final")

    if not ini or not fin:
        raise HTTPException(status_code=404, detail="No hay registros para el rango de fechas")

    denom = maquina.denominacion

    def calc_diff(campo: str) -> float:
        return (int(fin[campo]) - int(ini[campo])) * denom

    total_in = calc_diff("contador_IN")
    total_out = calc_diff("contador_OUT")
    total_jackpot = calc_diff("contador_JACKPOT")
    total_billetero = calc_diff("contador_BILLETERO")
    utilidad = total_in - total_out - total_jackpot

    return CuadreFinal(
        maquina_id=maquina.id,
        asset=maquina.asset,
        marca=maquina.marca,
        modelo=maquina.modelo,
        denominacion=denom,
        desde=desde,
        hasta=hasta,
        total_in=total_in,
        total_out=total_out,
        total_jackpot=total_jackpot,
        total_billetero=total_billetero,
        utilidad=utilidad
    )