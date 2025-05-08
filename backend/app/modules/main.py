from fastapi import FastAPI
from app.modules.usuarios_configuracion import usuarios

app = FastAPI()
app.include_router(usuarios.router)


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a CUADRE CASINO"}
