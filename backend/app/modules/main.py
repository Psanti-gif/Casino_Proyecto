from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.modules.usuarios_configuracion import usuarios
from app.modules.usuarios_configuracion import acciones_usuario
from app.modules.usuarios_configuracion import configuracion
from app.modules.gestion_maquinas import maquinas
from app.modules.gestion_maquinas import acciones_maquina
from app.modules.cuadre_maquina import cuadre_maquina
from app.modules.Modulo_Reportes import reportes
from app.modules.registro_contadores import Registro_Contadores

RUTA_MEDIA = Path(__file__).parent / "usuarios_configuracion" / "media"

app = FastAPI()
app.include_router(usuarios.router)
app.include_router(acciones_usuario.router)
app.include_router(configuracion.router)
app.include_router(maquinas.router)
app.include_router(acciones_maquina.router)
app.include_router(cuadre_maquina.router)
app.include_router(reportes.router)
app.include_router(Registro_Contadores.router)

app.mount("/media", StaticFiles(directory=RUTA_MEDIA), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend permitido
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def inicio():
    return {"mensaje": "Api Proyecto Casino"}
