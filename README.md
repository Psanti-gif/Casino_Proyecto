# Proyecto de Casino 🎰

Este es un proyecto fullstack para la presentación del trabajo final, proyecto enfocado en un Casino, realizando un backend en Python (FastAPI) y frontend en Next.js.

## Estructura
- `backend/`: API REST construida en FastAPI.
- `frontend/`: Interfaz visual en Next.js.

## Cómo iniciar

###Requisitos

- Python 3.10+
- Node.js 18+
- npm o yarn

---

### Backend - FastAPI + ReactPy

```bash
cd backend

# Recomendado: activar entorno virtual
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
