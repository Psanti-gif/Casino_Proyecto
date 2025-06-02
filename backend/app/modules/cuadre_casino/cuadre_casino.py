from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timedelta
import csv
import json

router = APIRouter(tags=["Cuadre casino"])

ARCHIVO_CONTADORES = Path(__file__).parent.parent / \
    "registro_contadores" / "registros.csv"
ARCHIVO_MAQUINAS = Path(__file__).parent.parent / \
    "gestion_maquinas" / "maquinas.json"
ARCHIVO_UTILIDAD = Path(__file__).parent / "utilidad_final_casino.csv"


class CuadreCasinoRequest(BaseModel):
    casino: str
    fecha_inicio: str  # formato YYYY-MM-DD
    fecha_fin: str     # formato YYYY-MM-DD


def obtener_denominacion(codigo_maquina: str):
    if not ARCHIVO_MAQUINAS.exists():
        return 1  # valor por defecto

    with open(ARCHIVO_MAQUINAS, "r", encoding="utf-8") as f:
        maquinas = json.load(f)
        for maquina in maquinas.values():
            if maquina["codigo"] == codigo_maquina:
                return float(maquina.get("denominacion", 1))
    return 1


@router.post("/cuadre_casino")
def cuadre_casino(data: CuadreCasinoRequest):
    if not ARCHIVO_CONTADORES.exists():
        raise HTTPException(
            status_code=404, detail="No hay registros de contadores")

    fecha_ini = datetime.strptime(data.fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(data.fecha_fin, "%Y-%m-%d")

    fechas_rango = []
    actual = fecha_ini
    while actual <= fecha_fin:
        fechas_rango.append(actual.strftime("%Y-%m-%d"))
        actual += timedelta(days=1)

    registros = []
    with open(ARCHIVO_CONTADORES, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Casino"] != data.casino:
                continue
            try:
                fecha = datetime.strptime(row["Fecha"], "%Y-%m-%d")
            except ValueError:
                continue
            if fecha_ini <= fecha <= fecha_fin:
                registros.append({
                    "fecha": row["Fecha"],
                    "maquina": row["Maquina"],
                    "in": float(row["In"]),
                    "out": float(row["Out"]),
                    "jackpot": float(row["Jackpot"]),
                    "billetero": float(row["Billetero"]),
                    "recorte": row.get("Recorte", "False") == "True",
                    "fecha_dt": fecha
                })

    if not registros:
        raise HTTPException(
            status_code=404, detail="No se encontraron registros para ese casino y rango de fechas")

    maquinas = {}
    for r in registros:
        if r["maquina"] not in maquinas:
            maquinas[r["maquina"]] = []
        maquinas[r["maquina"]].append(r)

    resultado_por_maquina = []

    for maquina, items in maquinas.items():
        denominacion = obtener_denominacion(maquina)
        items_ordenados = sorted(items, key=lambda x: x["fecha_dt"])
        registros_por_fecha = {r["fecha"]: r for r in items_ordenados}
        tramos = []
        tramo_inicio = None

        for idx, fecha in enumerate(fechas_rango):
            registro = registros_por_fecha.get(fecha)
            corte = False
            if registro and str(registro.get("recorte", "False")).lower() == "true":
                corte = True

            if fecha in registros_por_fecha:
                if tramo_inicio is None:
                    tramo_inicio = fecha
                if corte and tramo_inicio != fecha:
                    fecha_anterior = fechas_rango[idx -
                                                  1] if idx > 0 else fecha
                    tramos.append((tramo_inicio, fecha_anterior))
                    tramo_inicio = fecha
                if idx == len(fechas_rango) - 1 and tramo_inicio is not None:
                    tramos.append((tramo_inicio, fecha))
            else:
                if tramo_inicio is not None:
                    fecha_anterior = fechas_rango[idx -
                                                  1] if idx > 0 else fecha
                    tramos.append((tramo_inicio, fecha_anterior))
                    tramo_inicio = None

        total_in = total_out = total_jackpot = total_billetero = utilidad = 0
        contador_inicial = {"in": 0, "out": 0, "jackpot": 0, "billetero": 0}
        contador_final = {"in": 0, "out": 0, "jackpot": 0, "billetero": 0}

        for tramo in tramos:
            ini, fin = tramo
            reg_ini = registros_por_fecha.get(ini)
            reg_fin = registros_por_fecha.get(fin)

            if ini == fin or reg_ini is None:
                inicial = {"in": 0, "out": 0, "jackpot": 0, "billetero": 0}
                final = {
                    "in": reg_fin["in"] if reg_fin else 0,
                    "out": reg_fin["out"] if reg_fin else 0,
                    "jackpot": reg_fin["jackpot"] if reg_fin else 0,
                    "billetero": reg_fin["billetero"] if reg_fin else 0,
                }
            else:
                inicial = {
                    "in": reg_ini["in"],
                    "out": reg_ini["out"],
                    "jackpot": reg_ini["jackpot"],
                    "billetero": reg_ini["billetero"],
                }
                final = {
                    "in": reg_fin["in"],
                    "out": reg_fin["out"],
                    "jackpot": reg_fin["jackpot"],
                    "billetero": reg_fin["billetero"],
                }

            if tramos.index(tramo) == 0:
                contador_inicial = inicial
            contador_final = final

            total_in += (final["in"] - inicial["in"]) * denominacion
            total_out += (final["out"] - inicial["out"]) * denominacion
            total_jackpot += (final["jackpot"] -
                              inicial["jackpot"]) * denominacion
            total_billetero += (final["billetero"] -
                                inicial["billetero"]) * denominacion

        utilidad = total_in - (total_out + total_jackpot)

        resultado_por_maquina.append({
            "maquina": maquina,
            "fecha_inicio": items_ordenados[0]["fecha"],
            "fecha_fin": items_ordenados[-1]["fecha"],
            "contador_inicial": contador_inicial,
            "contador_final": contador_final,
            "denominacion": denominacion,
            "total_in": total_in,
            "total_out": total_out,
            "total_jackpot": total_jackpot,
            "total_billetero": total_billetero,
            "utilidad": utilidad
        })

    totales = {
        "total_in": sum(r["total_in"] for r in resultado_por_maquina),
        "total_out": sum(r["total_out"] for r in resultado_por_maquina),
        "total_jackpot": sum(r["total_jackpot"] for r in resultado_por_maquina),
        "total_billetero": sum(r["total_billetero"] for r in resultado_por_maquina),
        "utilidad_total": sum(r["utilidad"] for r in resultado_por_maquina),
    }

    return {
        "casino": data.casino,
        "fecha_inicio": data.fecha_inicio,
        "fecha_fin": data.fecha_fin,
        "detalle_maquinas": resultado_por_maquina,
        "totales": totales
    }


@router.post("/guardar-utilidad-casino")
def guardar_utilidad_casino(payload: dict = Body(...)):
    file_exists = ARCHIVO_UTILIDAD.exists()
    with open(ARCHIVO_UTILIDAD, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "casino", "fecha_inicio", "fecha_fin",
                "total_in", "total_out", "total_jackpot",
                "total_billetero", "utilidad_total"
            ])
        writer.writerow([
            payload.get("casino", ""),
            payload.get("fecha_inicio", ""),
            payload.get("fecha_fin", ""),
            payload["totales"].get("total_in", 0),
            payload["totales"].get("total_out", 0),
            payload["totales"].get("total_jackpot", 0),
            payload["totales"].get("total_billetero", 0),
            payload["totales"].get("utilidad_total", 0)
        ])
    return {"status": "ok", "archivo": str(ARCHIVO_UTILIDAD)}

@router.get("/utilidad_final_casino")
def obtener_utilidad_final():
    csv_path = Path(__file__).parent / "utilidad_final_casino.csv"
    if not csv_path.exists():
        return []
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)