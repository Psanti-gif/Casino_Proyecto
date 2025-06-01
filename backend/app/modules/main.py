from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.modules.usuarios_configuracion import usuarios
from app.modules.usuarios_configuracion import acciones_usuario
from app.modules.usuarios_configuracion import configuracion
from app.modules.gestion_maquinas import gestion_maquinas
from app.modules.cuadre_maquina import cuadre_maquina
from app.modules.registro_contadores import Registro_Contadores
from app.modules.gestion_lugares import lugares
from app.modules.cuadre_casino import cuadre_casino
from app.modules.encargados import encargados
from app.modules.modulo_reportes import reportes

# PARA PROGRAMAR ENVIO AUTOMATICO (BONUS)
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()


RUTA_MEDIA = Path(__file__).parent / "usuarios_configuracion" / "media"

app = FastAPI()
app.include_router(usuarios.router)
app.include_router(acciones_usuario.router)
app.include_router(configuracion.router)
app.include_router(gestion_maquinas.router)
app.include_router(cuadre_maquina.router)
app.include_router(Registro_Contadores.router)
app.include_router(lugares.router)
app.include_router(cuadre_casino.router)
app.include_router(encargados.router)
app.include_router(reportes.router)

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


# uvicorn app.modules.main:app --reload
