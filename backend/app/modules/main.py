from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.usuarios_configuracion import usuarios
from app.modules.usuarios_configuracion import acciones_usuario
from app.modules.gestion_maquinas import maquinas
from app.modules.gestion_maquinas import acciones_maquina


app = FastAPI()
app.include_router(usuarios.router)
app.include_router(acciones_usuario.router)
app.include_router(maquinas.router)
app.include_router(acciones_maquina.router)


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
