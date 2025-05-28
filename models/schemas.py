from pydantic import BaseModel
from typing import List, Dict

class CasinoInfo(BaseModel):
    nombre: str
    maquinas: List[str]

class CasinosResponse(BaseModel):
    casinos: Dict[str, CasinoInfo]
