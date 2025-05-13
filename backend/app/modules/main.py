from fastapi import FastAPI
from app.modules.usuarios_configuracion import usuarios
from app.modules.usuarios_configuracion import acciones

app = FastAPI()
app.include_router(usuarios.router)
app.include_router(acciones.router)


@app.get("/")
def inicio():
    return {"mensaje": "Api Proyecto Casino"}
