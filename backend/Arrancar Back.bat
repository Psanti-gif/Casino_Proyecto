@echo off
REM Instalar dependencias globalmente
pip install --upgrade pip
pip install -r app\requirements.txt

REM Ejecutar el proyecto principal con Uvicorn
uvicorn app.modules.main:app --reload

pause
