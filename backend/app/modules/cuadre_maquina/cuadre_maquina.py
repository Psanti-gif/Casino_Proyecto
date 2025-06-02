import requests
import csv
from fastapi import APIRouter, Body
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

class BalanceRequest(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    casino: str
    maquina: str
    id: str
    denominacion: float  # Ahora se recibe en el POST

@router.post("/cuadre_maquina")
def calcular_balance(data: BalanceRequest):
    fecha_inicio = data.fecha_inicio
    fecha_fin = data.fecha_fin
    id_maquina = data.id.strip().upper()
    denominacion = data.denominacion

    # Obtener registros desde /registros
    response = requests.get("http://127.0.0.1:8000/registros")
    if response.status_code != 200:
        return {"cuadres": []}
    registros = response.json()

    # Generar rango de fechas
    fechas_rango = []
    fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_final = datetime.strptime(fecha_fin, "%Y-%m-%d")
    while fecha_actual <= fecha_final:
        fechas_rango.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)

    # Filtrar registros de la máquina y fechas válidas
    registros_filtrados = [
        r for r in registros
        if str(r.get("maquina", "")).strip().upper() == id_maquina
        and r.get("fecha") in fechas_rango
    ]
    registros_filtrados.sort(key=lambda r: r["fecha"])

    if len(registros_filtrados) < 2:
        return {"cuadres": []}

    ini = registros_filtrados[0]
    fin = registros_filtrados[-1]

    def val(campo, reg):
        return float(reg.get(campo, 0))

    total_in = (val("in", fin) - val("in", ini)) * denominacion
    total_out = (val("out", fin) - val("out", ini)) * denominacion
    total_jackpot = (val("jackpot", fin) - val("jackpot", ini)) * denominacion
    total_billetero = (val("billetero", fin) - val("billetero", ini)) * denominacion
    utilidad = total_in - (total_out + total_jackpot)

    resultado = {
        "fecha": fecha_fin,
        "casino": data.casino,
        "maquina": data.maquina,
        "denominacion": denominacion,
        "in": round(total_in, 2),
        "out": round(total_out, 2),
        "jackpot": round(total_jackpot, 2),
        "billetero": round(total_billetero, 2),
        "utilidad": round(utilidad, 2)
    }

    return {"cuadres": [resultado]}

@router.get("/utilidad_final")
def obtener_utilidad_final():
    csv_path = Path(__file__).parent / "utilidad_final.csv"
    if not csv_path.exists():
        return []
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

@router.post("/guardar_utilidad")
def guardar_utilidad(cuadres: list = Body(...)):
    csv_path = Path(__file__).parent / "utilidad_final.csv"
    file_exists = csv_path.exists()
    with open(csv_path, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "utilidad_final", "contador_in", "contador_out", "contador_jackpot",
                "contador_billetero", "maquina", "casino", "fecha_inicio", "fecha_fin"
            ])
        for cuadre in cuadres:
            writer.writerow([
                cuadre["utilidad"],
                cuadre["total_in"],
                cuadre["total_out"],
                cuadre["total_jackpot"],
                cuadre["total_billetero"],
                cuadre.get("maquina", ""), 
                cuadre.get("casino", ""),   
                cuadre["fecha_inicio"],
                cuadre["fecha_fin"]
            ])
    return {"status": "ok"}