from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Modelo de datos para los casinos


class Casino(BaseModel):
    id: int
    nombre: str
    direccion: str
    codigo: str
    activo: bool = True


# Base de datos en memoria (como ejemplo)
casinos_db = []


@app.post("/casinos/", response_model=Casino)
def crear_casino(casino: Casino):
    # Verifica si el código ya existe
    if any(codigo == casino.codigo for codigo in [c['codigo'] for c in casinos_db]):
        raise HTTPException(
            status_code=400, detail="El código de casino ya existe.")

    casinos_db.append(casino.dict())
    return casino


@app.get("/casinos/", response_model=List[Casino])
def listar_casinos(activos: bool = True):
    return [Casino(**casino) for casino in casinos_db if casino["activo"] == activos]


@app.put("/casinos/{casino_id}", response_model=Casino)
def actualizar_casino(casino_id: int, casino_update: Casino):
    for idx, casino in enumerate(casinos_db):
        if casino["id"] == casino_id:
            casinos_db[idx] = casino_update.dict()
            return casino_update
    raise HTTPException(status_code=404, detail="Casino no encontrado.")


@app.patch("/casinos/{casino_id}/inactivar", response_model=Casino)
def inactivar_casino(casino_id: int):
    for casino in casinos_db:
        if casino["id"] == casino_id:
            casino["activo"] = False
            return Casino(**casino)
    raise HTTPException(status_code=404, detail="Casino no encontrado.")
