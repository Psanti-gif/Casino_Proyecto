from pathlib import Path
import os
from fastapi import FastAPI, Query, APIRouter
from pydantic import BaseModel
from typing import List
import csv

app = FastAPI()
CARPETA_MODULO = Path(__file__).parent
ARCHIVO_CSV = str(CARPETA_MODULO / "registros.csv")
AUDITORIA_CSV = str(CARPETA_MODULO / "auditoria.csv")

router = APIRouter(tags=["Registro Contadores"])
# Modelo de datos


class Contador(BaseModel):
    fecha: str
    casino: str
    maquina: str
    in_contador: float
    out_contador: float
    jackpot_contador: float
    billetero_contador: float
    recorte: bool  # Nuevo campo

# Inicializar archivo CSV si no existe


def inicializar_csv():
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Casino", "Maquina", "In", "Out", "Jackpot", "Billetero", "Recorte"])  # Agregado Recorte

inicializar_csv()

# Guardar nuevo registro


@router.post("/registrar")
def registrar_contador(contador: Contador):
    for valor in [contador.in_contador, contador.out_contador, contador.jackpot_contador, contador.billetero_contador]:
        if valor < 0:
            return {"error": "Los contadores no pueden tener valores negativos"}

    with open(ARCHIVO_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            contador.fecha,
            contador.casino,
            contador.maquina,
            contador.in_contador,
            contador.out_contador,
            contador.jackpot_contador,
            contador.billetero_contador,
            contador.recorte
        ])
    return {"mensaje": "Registro guardado exitosamente"}

# Obtener todos los registros


@router.get("/registros")
def obtener_registros():
    registros = []
    with open(ARCHIVO_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append({
                "fecha": row["Fecha"],
                "casino": row["Casino"],
                "maquina": row["Maquina"],
                "in": float(row["In"]),
                "out": float(row["Out"]),
                "jackpot": float(row["Jackpot"]),
                "billetero": float(row["Billetero"]),
                "recorte": row.get("Recorte", "False") == "True"
            })
    if not registros:
        return {"Mensaje": "No hay registros BB"}
    return registros

# Buscar por casino y fecha


@router.get("/buscar/")
def buscar_registros(casino: str = Query(...), fecha: str = Query(...)):
    resultados = []
    with open(ARCHIVO_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Casino"] == casino and row["Fecha"] == fecha:
                resultados.append({
                    "fecha": row["Fecha"],
                    "casino": row["Casino"],
                    "maquina": row["Maquina"],
                    "in": float(row["In"]),
                    "out": float(row["Out"]),
                    "jackpot": float(row["Jackpot"]),
                    "billetero": float(row["Billetero"]),
                    "recorte": row.get("Recorte", "False") == "True"  # Nuevo campo
                })
    return resultados

# Modificar registro


@router.put("/modificar")
def modificar_contador(contador: Contador):
    for valor in [contador.in_contador, contador.out_contador, contador.jackpot_contador, contador.billetero_contador]:
        if valor < 0:
            return {"error": "Los contadores no pueden tener valores negativos"}

    registros = []
    modificado = False
    anterior = None

    with open(ARCHIVO_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Fecha"] == contador.fecha and row["Casino"] == contador.casino:
                anterior = row.copy()
                row["In"] = str(contador.in_contador)
                row["Out"] = str(contador.out_contador)
                row["Jackpot"] = str(contador.jackpot_contador)
                row["Billetero"] = str(contador.billetero_contador)
                row["Recorte"] = str(contador.recorte)  # Nuevo campo
                modificado = True
            registros.append(row)

    if not modificado:
        return {"error": "Registro no encontrado"}

    with open(ARCHIVO_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["Fecha", "Casino", "Maquina", "In", "Out", "Jackpot", "Billetero", "Recorte"]  # Agregado Recorte
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(registros)

    registrar_auditoria(anterior, contador)
    return {"mensaje": "Registro modificado exitosamente"}

# Registrar auditoría


def registrar_auditoria(anterior, nuevo: Contador):
    if not os.path.exists(AUDITORIA_CSV):
        with open(AUDITORIA_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "fecha", "casino", "maquina", "in_antes", "out_antes", "jackpot_antes", "billetero_antes",
                "in_despues", "out_despues", "jackpot_despues", "billetero_despues"
            ])
    with open(AUDITORIA_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            anterior["Fecha"], anterior["Casino"], anterior["Maquina"],
            anterior["In"], anterior["Out"], anterior["Jackpot"], anterior["Billetero"],
            nuevo.in_contador, nuevo.out_contador, nuevo.jackpot_contador, nuevo.billetero_contador
        ])

# uvicorn Registro_Contadores:app --reload
