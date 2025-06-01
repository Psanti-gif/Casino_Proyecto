@echo off
REM Instalar dependencias
python -m pip install --upgrade pip
pip install -r app\requirements.txt

REM Arrancar el backend (ajusta el siguiente comando si tu entrypoint es diferente)
cd app
uvicorn modules.main:app --reload

pause
