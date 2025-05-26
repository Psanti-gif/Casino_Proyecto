import csv
from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path

router = APIRouter()

class BalanceRequest(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    maquina_id: str
    denominacion: float  # Ahora se recibe en el POST

@router.post("/cuadre_maquina")
def calcular_balance(data: BalanceRequest):
    fecha_inicio = data.fecha_inicio
    fecha_fin = data.fecha_fin
    maquina_id = data.maquina_id
    denominacion = data.denominacion

    contador_inicial = contador_final = None

    # Usa ruta absoluta basada en la ubicación de este archivo
    csv_path = Path(__file__).parent / "contadores.csv"
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["id_maquina"] == maquina_id:
                if row["fecha"] == fecha_inicio:
                    contador_inicial = row
                if row["fecha"] == fecha_fin:
                    contador_final = row

    if not contador_inicial or not contador_final:
        return {"error": "No se encontraron registros para las fechas indicadas"}

    def calc_total(final, inicial, campo):
        return (float(final[campo]) - float(inicial[campo])) * denominacion

    total_in = calc_total(contador_final, contador_inicial, "in")
    total_out = calc_total(contador_final, contador_inicial, "out")
    total_jackpot = calc_total(contador_final, contador_inicial, "jackpot")
    total_billetero = calc_total(contador_final, contador_inicial, "billetero")

    return {
        "total_in": total_in,
        "total_out": total_out,
        "total_jackpot": total_jackpot,
        "total_billetero": total_billetero
    }