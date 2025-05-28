import requests
import csv
from fastapi import APIRouter
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
    id_maquina = data.id
    denominacion = data.denominacion

    # Obtener registros
    response = requests.get("http://127.0.0.1:8000/registros")
    if response.status_code != 200:
        return {"error": "No se pudieron obtener los registros"}
    registros = response.json()

    # Filtrar registros de la máquina y fechas en el rango
    fechas_rango = []
    fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_final = datetime.strptime(fecha_fin, "%Y-%m-%d")
    while fecha_actual <= fecha_final:
        fechas_rango.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)

    registros_maquina = [r for r in registros if r.get("maquina") == id_maquina and r["fecha"] in fechas_rango]
    registros_maquina.sort(key=lambda r: r["fecha"])

    # Validar que no falte ninguna fecha
    fechas_encontradas = {r["fecha"] for r in registros_maquina}
    for fecha in fechas_rango:
        if fecha not in fechas_encontradas:
            raise Exception(f"Falta el registro para la fecha {fecha}")

    # Identificar cortes
    cortes = []
    for i, r in enumerate(registros_maquina):
        if r.get("recorte", "false"):
            cortes.append(i)

    # Definir los tramos de cuadre
    tramos = []
    inicio = 0
    for corte_idx in cortes:
        if corte_idx > inicio:
            tramos.append((inicio, corte_idx - 1))
        inicio = corte_idx
    if inicio < len(registros_maquina) - 1:
        tramos.append((inicio, len(registros_maquina) - 1))

    # Si no hay cortes, solo un tramo
    if not tramos:
        tramos = [(0, len(registros_maquina) - 1)]

    # Guardar resultados de cada cuadre
    csv_path = Path(__file__).parent / "utilidad_final.csv"
    file_exists = csv_path.exists()
    with open(csv_path, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "utilidad_final", "contador_in", "contador_out", "contador_jackpot",
                "contador_billetero", "maquina", "casino", "fecha_inicio", "fecha_fin"
            ])
        resultados = []
        for tramo in tramos:
            ini, fin = tramo
            reg_ini = registros_maquina[ini]
            reg_fin = registros_maquina[fin]
            def calc_total(final, inicial, campo):
                return (float(final[campo]) - float(inicial[campo])) * denominacion
            total_in = calc_total(reg_fin, reg_ini, "in")
            total_out = calc_total(reg_fin, reg_ini, "out")
            total_jackpot = calc_total(reg_fin, reg_ini, "jackpot")
            total_billetero = calc_total(reg_fin, reg_ini, "billetero")
            utilidad = total_in - (total_out + total_jackpot)
            writer.writerow([
                utilidad,
                float(reg_fin["in"]),
                float(reg_fin["out"]),
                float(reg_fin["jackpot"]),
                float(reg_fin["billetero"]),
                id_maquina,
                data.casino,
                reg_ini["fecha"],
                reg_fin["fecha"]
            ])
            resultados.append({
                "fecha_inicio": reg_ini["fecha"],
                "fecha_fin": reg_fin["fecha"],
                "total_in": total_in,
                "total_out": total_out,
                "total_jackpot": total_jackpot,
                "total_billetero": total_billetero,
                "utilidad": utilidad
            })

    return {"cuadres": resultados}

@router.get("/utilidad_final")
def obtener_utilidad_final():
    csv_path = Path(__file__).parent / "utilidad_final.csv"
    if not csv_path.exists():
        return []
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)