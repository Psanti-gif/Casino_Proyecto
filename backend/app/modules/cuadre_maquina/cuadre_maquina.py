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
    id_maquina = data.id
    denominacion = data.denominacion

    response = requests.get("http://127.0.0.1:8000/registros")
    if response.status_code != 200:
        return {"error": "No se pudieron obtener los registros"}
    registros = response.json()

    # Generar lista de fechas del rango
    fechas_rango = []
    fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_final = datetime.strptime(fecha_fin, "%Y-%m-%d")
    while fecha_actual <= fecha_final:
        fechas_rango.append(fecha_actual.strftime("%Y-%m-%d"))
        fecha_actual += timedelta(days=1)

    # Filtrar registros de la máquina y fechas en el rango
    registros_maquina = [r for r in registros if r.get("maquina") == id_maquina and r["fecha"] in fechas_rango]
    registros_maquina.sort(key=lambda r: r["fecha"])

    # Crear un dict para acceso rápido por fecha
    registros_por_fecha = {r["fecha"]: r for r in registros_maquina}

    # Lógica de cuadre considerando fechas faltantes como cortes
    tramos = []
    tramo_inicio = None
    resultados = []

    for idx, fecha in enumerate(fechas_rango):
        if fecha in registros_por_fecha:
            if tramo_inicio is None:
                tramo_inicio = fecha
            # Si es la última fecha del rango, cerrar tramo
            if idx == len(fechas_rango) - 1:
                tramos.append((tramo_inicio, fecha))
        else:
            # Si falta la fecha, cerrar tramo anterior (si existe)
            if tramo_inicio is not None:
                fecha_anterior = fechas_rango[idx - 1] if idx > 0 else fecha
                tramos.append((tramo_inicio, fecha_anterior))
                tramo_inicio = None

    for tramo in tramos:
        ini, fin = tramo
        reg_ini = registros_por_fecha.get(ini)
        reg_fin = registros_por_fecha.get(fin)
        # Si el tramo es de una sola fecha o el inicial falta, usar ceros
        if ini == fin or reg_ini is None:
            total_in = float(reg_fin["in"]) * denominacion if reg_fin else 0
            total_out = float(reg_fin["out"]) * denominacion if reg_fin else 0
            total_jackpot = float(reg_fin["jackpot"]) * denominacion if reg_fin else 0
            total_billetero = float(reg_fin["billetero"]) * denominacion if reg_fin else 0
            utilidad = total_in - (total_out + total_jackpot)
            resultados.append({
                "fecha_inicio": ini,
                "fecha_fin": fin,
                "total_in": total_in,
                "total_out": total_out,
                "total_jackpot": total_jackpot,
                "total_billetero": total_billetero,
                "utilidad": utilidad,
                "maquina": id_maquina,
                "casino": data.casino
            })
        else:
            def calc_total(final, inicial, campo):
                return (float(final[campo]) - float(inicial[campo])) * denominacion
            total_in = calc_total(reg_fin, reg_ini, "in")
            total_out = calc_total(reg_fin, reg_ini, "out")
            total_jackpot = calc_total(reg_fin, reg_ini, "jackpot")
            total_billetero = calc_total(reg_fin, reg_ini, "billetero")
            utilidad = total_in - (total_out + total_jackpot)
            resultados.append({
                "fecha_inicio": ini,
                "fecha_fin": fin,
                "total_in": total_in,
                "total_out": total_out,
                "total_jackpot": total_jackpot,
                "total_billetero": total_billetero,
                "utilidad": utilidad,
                "maquina": id_maquina,
                "casino": data.casino
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