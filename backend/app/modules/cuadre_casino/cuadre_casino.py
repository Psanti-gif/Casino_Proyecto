from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import csv
from datetime import datetime

router = APIRouter(tags=["Cuadre casino"])

ARCHIVO_CONTADORES = Path(__file__).parent / \
    "../registro_contadores/registros.csv"


class CuadreCasinoRequest(BaseModel):
    casino: str
    fecha_inicio: str  # formato YYYY-MM-DD
    fecha_fin: str     # formato YYYY-MM-DD


@router.post("/cuadre-casino")
def cuadre_casino(data: CuadreCasinoRequest):
    if not ARCHIVO_CONTADORES.exists():
        raise HTTPException(
            status_code=404, detail="No hay registros de contadores")

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
            fecha_ini = datetime.strptime(data.fecha_inicio, "%Y-%m-%d")
            fecha_fin = datetime.strptime(data.fecha_fin, "%Y-%m-%d")
            if fecha_ini <= fecha <= fecha_fin:
                registros.append({
                    "fecha": row["Fecha"],
                    "maquina": row["Maquina"],
                    "in": float(row["In"]),
                    "out": float(row["Out"]),
                    "jackpot": float(row["Jackpot"]),
                    "billetero": float(row["Billetero"]),
                    "recorte": row.get("Recorte", "False") == "True",
                })

    if not registros:
        raise HTTPException(
            status_code=404, detail="No se encontraron registros para ese casino y rango de fechas")

    # Agrupar por máquina
    maquinas = {}
    for r in registros:
        if r["maquina"] not in maquinas:
            maquinas[r["maquina"]] = []
        maquinas[r["maquina"]].append(r)

    resultado_por_maquina = []
    for maquina, items in maquinas.items():
        items_ordenados = sorted(items, key=lambda x: x["fecha"])
        ini = items_ordenados[0]
        fin = items_ordenados[-1]

        total_in = fin["in"] - ini["in"]
        total_out = fin["out"] - ini["out"]
        total_jackpot = fin["jackpot"] - ini["jackpot"]
        total_billetero = fin["billetero"] - ini["billetero"]
        utilidad = total_in - (total_out + total_jackpot)

        resultado_por_maquina.append({
            "maquina": maquina,
            "fecha_inicio": ini["fecha"],
            "fecha_fin": fin["fecha"],
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
