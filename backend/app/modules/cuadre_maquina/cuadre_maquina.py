import requests
import csv
from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime

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
    id_maquina = data.id
    denominacion = data.denominacion

    contador_inicial = contador_final = None

    response = requests.get("http://127.0.0.1:8000/registros")
    if response.status_code != 200:
        return {"error": "No se pudieron obtener los registros"}
    registros = response.json()

    for row in registros:
        if row.get("maquina") == id_maquina:
            if row["fecha"] == fecha_inicio:
                contador_inicial = row
            if row["fecha"] == fecha_fin:
                contador_final = row

    if not contador_inicial or not contador_final:
        return {"error": f"No se encontraron registros para las fechas o id indicados"}

    def calc_total(final, inicial, campo):
        return (float(final[campo]) - float(inicial[campo])) * denominacion

    total_in = calc_total(contador_final, contador_inicial, "in")
    total_out = calc_total(contador_final, contador_inicial, "out")
    total_jackpot = calc_total(contador_final, contador_inicial, "jackpot")
    total_billetero = calc_total(contador_final, contador_inicial, "billetero")
    utilidad = total_in - (total_out + total_jackpot)

    # Guardar en utilidad_final.csv con la fecha actual
    csv_path = Path(__file__).parent / "utilidad_final.csv"
    file_exists = csv_path.exists()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(csv_path, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "utilidad_final", "contador_in", "contador_out", "contador_jackpot",
                "contador_billetero", "maquina", "casino", "fecha"
            ])
        writer.writerow([
            utilidad,
            float(contador_final["in"]),
            float(contador_final["out"]),
            float(contador_final["jackpot"]),
            float(contador_final["billetero"]),
            id_maquina,
            data.casino,
            fecha_actual  # ahora se guarda la fecha actual
        ])

    return {
        "total_in": total_in,
        "total_out": total_out,
        "total_jackpot": total_jackpot,
        "total_billetero": total_billetero
    }

@router.get("/utilidad_final")
def obtener_utilidad_final():
    csv_path = Path(__file__).parent / "utilidad_final.csv"
    if not csv_path.exists():
        return []
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)